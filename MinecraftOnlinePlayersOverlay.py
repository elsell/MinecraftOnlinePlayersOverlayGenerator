import sys
import argparse
import configparser
import time
import os
import logging
from mcserver_connector import MinecraftConnector
from PIL import Image, ImageDraw, ImageFont


class MinecraftOnlinePlayersOverlay:
    """
    Generates a transparent image that shows the names and skins
    of players on a Minecraft server.
    """

    def __init__(self, image_output_dir: str, minecraft_server_ip: str, **kwargs):
        """[summary]

        Args:
            * image_output_dir (str): The directory in which the player list image file will be saved.
            * minecraft_server_ip (str):  The IP address of the Minecraft server to poll.

        KeywordArguments:
            * ``minecraft_server_port`` [``int``] -- (default: 25565) The port corresponding to ``minecraft_server_ip``

            * ``draw_shadow`` [``bool``] -- (default: True) Should a shadow be drawn below the player names.

            * ``image_name`` [``str``] -- (default: ``online_players.png``) The name of the generated image.

            * ``vertical_padding`` [``int``] -- (default: ``12``) Pixels between player head images.

            * ``refresh_every_seconds`` [``int``] -- (default: ``3``) How often to refresh the player list in seconds.
        """
        self._log = logging.getLogger(__name__ + ".MOPO")

        default_kwargs = {
            "minecraft_server_port": 25565,
            "draw_shadow": True,
            "image_name": "online_players.png",
            "vertical_padding": 12,
            "refresh_every_seconds": 3,
        }

        # Combine kwargs with default to fill missing gaps
        kwargs = {**default_kwargs, **kwargs}

        self._minecraft_server_ip = minecraft_server_ip
        self._server_port = int(kwargs["minecraft_server_port"])

        self._mcserver = MinecraftConnector(minecraft_server_ip, self._server_port)
        self._image_output_dir = image_output_dir
        self._player_image_name = kwargs["image_name"]
        self._draw_shadow = kwargs["draw_shadow"]
        self._vertical_padding = int(kwargs["vertical_padding"])
        self._refresh_every_seconds = int(kwargs["refresh_every_seconds"])

        self._print_init()

    def cleanup(self):
        self._mcserver.cleanup()

    def _print_init(self):
        self._log.info("Initializing MinecraftOnlinePlayersOverlay (MOPO)")
        items = {
            "Image Output Directory": self._image_output_dir,
            "Output Image Filename": self._player_image_name,
            "Minecraft Server IP": self._minecraft_server_ip,
            "Minecraft Server Port": self._server_port,
            "Draw Shadow": self._draw_shadow,
            "Vertical Padding": self._vertical_padding,
            "Refresh Rate (seconds)": self._refresh_every_seconds,
        }
        for item in items:
            self._log.info(
                "{}{:<30}{}".format(" " * 4, "{}:".format(item), items[item])
            )

    def _save_image(self, image, image_name):
        image_path = os.path.join(self._image_output_dir, image_name)

        try:
            if not os.path.isdir(self._image_output_dir):
                os.mkdir(self._image_output_dir)

            image.save(image_path)
        except FileNotFoundError as e:
            self._log.critical(
                "Could not save image to %s! If you're attempting to save an image to a network location,"
                " please ensure that the network location is accessable. Will wait and try again. (Error: %s)",
                image_path,
                repr(e),
            )

    def _build_player_image_board(self):
        players = self._mcserver.get_online_players()

        if len(players) > 0:
            names = [p["name"] for p in players]
            images = []
            try:
                images = [Image.open(i) for i in [p["image"] for p in players]]
            except AttributeError as e:
                self._log.warning(
                    "Unable to read an image. Will wait until next update as this may resolve itself. %s",
                    repr(e),
                )
                return None

            widths, heights = zip(*(i.size for i in images))

            # These seem backwards because we are making
            # a vertical image.
            total_height = sum(widths) + (self._vertical_padding * len(images))
            total_width = max(heights)

            self._log.debug(
                (
                    f"Image Height (without text): {total_height}",
                    f"Image Width (without text): {total_width}",
                )
            )

            combined_images = Image.new("RGBA", (total_width, total_height))

            y_offset = 0
            for image in images:
                combined_images.paste(image, (0, y_offset))
                y_offset += image.size[0] + self._vertical_padding

            return self._draw_player_names_on_image(
                combined_images, names, total_width, self._vertical_padding
            )

        # Return a blank image if no players are found.
        return Image.new("RGBA", (1, 1))

    def _draw_player_names_on_image(self, image, names, head_height, padding):
        width, height = image.size
        name_width = 1920
        name_right_padding = 15

        named_image = Image.new("RGBA", (width + name_width, height))
        named_image.paste(image, (name_width, 0))

        draw = ImageDraw.Draw(named_image)
        font_size = 50
        font = ImageFont.truetype("arial.ttf", font_size)
        try:
            font = ImageFont.truetype("minecraft_font.ttf", font_size)
        except OSError:
            self._log.warning(
                "Unable to find font minecraft_font.ttf. Falling back to Arial."
            )

        for i, name in enumerate(names):
            x_pos = name_width - name_right_padding
            y_pos = (i * padding) + ((i + 1) * (head_height)) - (head_height * 0.5)
            color_fg = (255, 255, 255)
            color_outline = (0, 0, 0)

            if self._draw_shadow:
                draw.text(
                    (x_pos - 5, y_pos - 5),
                    name,
                    font=font,
                    fill=color_outline,
                    anchor="rm",
                )
                draw.text(
                    (x_pos + 5, y_pos - 5),
                    name,
                    font=font,
                    fill=color_outline,
                    anchor="rm",
                )
                draw.text(
                    (x_pos - 5, y_pos + 5),
                    name,
                    font=font,
                    fill=color_outline,
                    anchor="rm",
                )
                draw.text(
                    (x_pos + 5, y_pos + 5),
                    name,
                    font=font,
                    fill=color_outline,
                    anchor="rm",
                )

            draw.text((x_pos, y_pos), name, color_fg, font=font, anchor="rm")

        return named_image

    def run_player_image_generator(self):
        while True:
            player_image = self._build_player_image_board()
            if player_image:
                self._save_image(player_image, self._player_image_name)
                online_count = len(self._mcserver.get_online_players())
                self._log.info(
                    "(%i Online) Saving image: %s",
                    online_count,
                    self._player_image_name,
                )
            else:
                self._log.info(
                    "Error creating image. Will wait %is and try again.",
                    self._refresh_every_seconds,
                )

            time.sleep(self._refresh_every_seconds)


def get_config(filename, default_params):
    new_config = configparser.ConfigParser(default_params)
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as config_file:
            new_config.read_file(config_file)
    else:
        with open(filename, "w", encoding="utf-8") as config_file:
            new_config.write(config_file)

    return new_config


def init_log(cmd_args):
    logging.basicConfig(
        level=cmd_args.loglevel.upper(),
        stream=sys.stdout,
        format="[%(asctime)s] %(levelname)8s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-log",
        "--loglevel",
        default="info",
        help="Provide logging level. Example --loglevel debug, default=info",
    )

    parser.add_argument(
        "--config",
        default="Minecraft_Online_Players_Overlay_Settings.ini",
        help="Path to config file. Example --config my_custom_config.ini, default=Minecraft_Online_Players_Overlay_Settings.ini",
    )

    return parser.parse_args()


if __name__ == "__main__":

    parser_args = get_args()

    init_log(parser_args)

    args = {
        "image_output_dir": ".",
        "image_name": "online_players.png",
        "minecraft_server_ip": "mc.3411heavenmedia.com",
        "minecraft_server_port": 25565,
        "draw_shadow": True,
        "vertical_padding": 12,
        "refresh_every_seconds": 10,
    }

    config = get_config(parser_args.config, args)

    runtime_args = dict(config.items("DEFAULT"))

    overlay = MinecraftOnlinePlayersOverlay(**runtime_args)

    try:
        while True:
            overlay.run_player_image_generator()
    except KeyboardInterrupt:
        print("Exiting")

    overlay.cleanup()
