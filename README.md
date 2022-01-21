![Code Quality](https://api.codiga.io/project/30759/score/svg)
![Code Grade](https://api.codiga.io/project/30759/status/svg)
![Maintenance](https://img.shields.io/maintenance/yes/2022)
![GitHub all releases](https://img.shields.io/github/downloads/elsell/MinecraftOnlinePlayersOverlayGenerator/total?color=brightgreen) 
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/elsell/MinecraftOnlinePlayersOverlayGenerator)



# Minecraft - Online Players Overlay Generator

## Contents
- [About](#about)
- [Quick Start](#quick-start)
  - [Download Pre-Built Binary](#1-download-a-pre-built-binary)
  - [Run from Source](#2-download-and-run-the-source-code)
- [Configuration](#configuration)
- [Command-Line Options](#command-line-options)
- [FAQ](#faq)
- [Projects Used](#projects-used)


## About

MOPOG (pronounced M-OH-POG) automatically generates an image displaying the players that are currently on a Minecraft server.

The intended use of the image is as an overlay on a live-stream, and works beautifully with [OBS Studio](https://obsproject.com/). 

### Screenshot
![online_players2 (Small)](https://user-images.githubusercontent.com/35787503/150449459-858507e7-e4e0-4e62-9c1b-85f178204eda.png)

## Quick Start

There are two ways to use MOPOG:
1. Download a pre-built binary (fast, easy, and still configurable!)
2. Download and run the Python source (a bit more work, but allows deep customization!)


### 1. Download a Pre-Built Binary
----------------------

#### 1. [Download the latest build](https://github.com/elsell/MinecraftOnlinePlayersOverlayGenerator/releases/latest)

#### 2. Run mowpog.exe

A configuration file called `Minecraft_Online_Players_Overlay_Settings.ini` will be generated.

#### 3. Configure MOPOG For Your Server

Open `Minecraft_Online_Players_Overlay_Settings.ini` and change `minecraft_server_ip` and `minecraft_server_port` to correspond to your server. See [Configuration](#configuration) for more details.

#### 4. Restart MOPOG and Use the Generated Image as You See Fit

By default, an image called `online_players.png` will be saved to the same directory that the program is run in. The output directory can be changed - see [Configuration](#configuration).

### 2. Download and Run the Source Code
----------------------
> [Python](https://www.python.org/downloads/) and [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) are required for this method. MOPOG was developed using Python 3.9.9.

1. Clone this repository
```
git clone https://elsell/MinecraftOnlinePlayersOverlayGenerator && cd MinecraftOnlinePlayersOverlayGenerator
```

2. Install Dependencies
```
python -m pip install –upgrade && python -m pip install -r requirements.txt
```

3. Run the Script
```
python MinecraftOnlinePlayersOverlayGenerator.py
```
*See [Command Line Options](#command-line-options) for more details.*
A configuration file called `Minecraft_Online_Players_Overlay_Settings.ini` will be generated.

4. Configure MOPOG For Your Server
Open `Minecraft_Online_Players_Overlay_Settings.ini` and change `minecraft_server_ip` and `minecraft_server_port` to correspond to your server. See [Configuration](#configuration) for more details.


# Configuration
MOPOG uses a configuration file to give you control over how it runs. 

By default, the configuration file is named `Minecraft_Online_Players_Overlay_Settings.ini` and is generated on the first run of MOPOG. 

Below is a copy of the default configuration file, containing a complete list of all configurable parameters.
> **NOTE:** Some parameters are marked as `optional` and are not required to be in your configuration file. 

```ini
# Minecraft_Online_Players_Overlay_Settings.ini

[DEFAULT]
# (required) The directory in which the output image will be saved.
image_output_dir = .

# (optional) The filename of the generated image. 
image_name = online_players.png

# (required) The IP address of the Minecraft server you wish to query.
minecraft_server_ip = mc.3411heavenmedia.com

# (optional) The port on which the Minecraft server listens. 
minecraft_server_port = 25565

# (optional) Whether a faint shadow/outline will be drawn behind the player names.
#            Useful when overlaying on a light background.
draw_shadow = True

# (optional) The space between each player head as it's drawn on the image.
vertical_padding = 12

# (optional) How often to refresh the player list. For larger servers (> 25 players),
#            it is recommended that this be >= 30 seconds.
refresh_every_seconds = 10
```

# Command-Line Options

### - `--help`

Show available command-line options. 

**Example:**
```
$ python MinecraftOnlinePlayersOverlay.py --help

usage: MinecraftOnlinePlayersOverlay.py [-h] [-log LOGLEVEL] [--config CONFIG]

optional arguments:
  -h, --help            show this help message and exit
  -log LOGLEVEL, --loglevel LOGLEVEL
                        Provide logging level. Example --loglevel debug, default=info
  --config CONFIG       Path to config file. Example --config my_custom_config.ini,
                        default=Minecraft_Online_Players_Overlay_Settings.ini
```

### - `--config <configuration_file>`

*Default: `Minecraft_Online_Players_Overlay_Settings.ini`*

Pass a pre-existing/custom-named configuration file to MOPOG. If the file does not exist, it will be created with default values.

**Example:**
```
python MinecraftOnlinePlayersOverlay.py --config my_config.ini
```

### - `--loglevel <log_level>, -log <log_level>`

Change the verbosity of MOPOG's logging.

*Default: `info`*

> Valid options can be found on the [Python logging library's website](https://docs.python.org/3/library/logging.html#logging-levels).

**Example:**
```
python MinecraftOnlinePlayersOverlay.py --loglevel debug
```

# FAQ

## I'm getting an error about no players being found!

First, check that the server isn't using a plugin to spoof the number of players. Some servers show that they have players when they do not, but MOPOG sees the truth. 

If you are still getting an error, there may be an incompatibility with the version of the server that is being queried. Please [Submit an Issue](https://github.com/elsell/MinecraftOnlinePlayersOverlayGenerator/issues/new/choose) so that we can get to the bottom of it!

## Can I make the list lay horizontally?

Unfortunately, MOPOG currently only supports a vertical list. However, if you have Python experience and would like to contribute, feel free to fork this repo and add that feature!

## Do I need to enable `query` in my `server.properties`?

Nope! MOPOG uses the same `status` request that the Minecraft client uses, and does not require `query` to be enabled in `server.properties`.

## Is there any reason that MOPOG might stop working?

Yes! It's important to recognize that MOPOG relies on [MC Heads](https://mc-heads.net) to retrieve images of player skins. Should this service stop working, MOPOG would also stop working. 

It would be possible to directly use the [Mojang API](https://wiki.vg/Mojang_API#UUID_to_Profile_and_Skin.2FCape), but using MC Heads was easier to set up. 

If this becomes a problem, MOPOG will have to switch to using the Mojang API directly.

## Will I get rate-limited?

Most APIs limit the number of times that a user can request information in a time period, including Mojang. 

However, MOPOG uses [MC Heads](https://mc-heads.net) who do not enforce any rate-limit! Therefore you are free to set the refresh interval as low as you feel comfortable. 

> **NOTE:** Even though you are theoretically unlimited, very quick refresh rates could potentially slow down the Minecraft server. 
> In addition, the query itself often takes more than 1 second, so it's best to stick to a refresh interval that is no less than 5 seconds. 


# Projects Used

MOPOG doesn't work alone! Here is a small, non-comprehensive list, of projects that it uses:

- [MC Heads](https://mc-heads.net)
- [Minecraft Font](https://www.fonts4free.net/minecraft-pixel-font.html) (Attribution-ShareAlike 3.0 Unported)
- [mcstatus](https://github.com/Dinnerbone/mcstatus)
