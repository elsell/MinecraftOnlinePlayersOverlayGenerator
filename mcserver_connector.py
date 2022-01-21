import os
import shutil
import logging
import tempfile
from urllib import request
import requests
from mcstatus import MinecraftServer


class MinecraftConnector:
    """mcstatus wrapper that adds the ability to get
    player head information along with online player info.

    Raises:
        SystemExit: Raised if the server configured does not provide any player
        information.
    """

    MC_HEADS_GET_HEAD = "https://mc-heads.net/avatar/{}.png"

    def __init__(self, server_ip: str, server_port: int = 25565):
        self._server_ip = server_ip
        self._server_port = server_port
        self._temp_dir = self._get_temp_dir()

        self._log = logging.getLogger(__name__ + ".MinecraftConnector")

        self._init_logging()

        self._server = MinecraftServer(self._server_ip, self._server_port)

    def cleanup(self):
        logging.debug("Removing temp dir: %s", self._temp_dir)
        shutil.rmtree(self._temp_dir)

    def _init_logging(self):
        self._log.info("Init Minecraft Connector")
        self._log.info("{}{:<30}{}".format(" " * 4, "Server IP:", self._server_ip))
        self._log.info("{}{:<30}{}".format(" " * 4, "Server Port:", self._server_port))
        self._log.info("{}{:<30}{}".format(" " * 4, "Temp Dir", self._temp_dir))

    def _get_temp_dir(self):
        return tempfile.mkdtemp(prefix="mcconnector_")

    def _status(self):
        try:
            return self._server.status()
        except Exception:
            self._log.error(
                "Unable to connect to server %s. "
                "Will continue running in-case it comes online.",
                "{}:{}".format(self._server_ip, self._server_port),
            )
            return None

    def _get_head_image(self, uuid: str):
        """
        Returns file path to the head image.
        Will download the image every time. In the future,
        some sort of cache or existence check would be neat.
        """
        request_url = MinecraftConnector.MC_HEADS_GET_HEAD.format(uuid)
        logging.debug("Request head for UUID: %s", uuid)
        logging.debug("Making request to %s", request_url)
        r = requests.get(request_url, stream=True)

        if r.status_code == 200:
            filepath = os.path.join(self._temp_dir, "{}.png".format(uuid))
            logging.debug("Set image filepath to: %s", filepath)
            with open(filepath, "wb") as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

            return filepath

        return None

    def get_online_players(self):
        """
        @return [{id: str, name: str}, ...]
        """
        status = self._status()

        if status:
            status = status.raw
            if "sample" not in status["players"]:
                self._log.fatal(
                    "Server did not return any player information! Unable to proceed."
                )
                raise SystemExit

            players = list(status["players"]["sample"])

            self._log.debug("%i players found.", len(players))

            for p in players:
                head = None

                head = self._get_head_image(p["id"])

                p["image"] = head

            return sorted(players, key=lambda p: p["name"])

        return []


if __name__ == "__main__":
    m = MinecraftConnector("mc.3411.best")
    print(m.get_online_players())
    # m.cleanup()
