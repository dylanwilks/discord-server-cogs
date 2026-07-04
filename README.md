# discord-server-cogs

A personal discord bot made with discord.py that I host on a Raspberry Pi for managing servers and permissions. I've generalized the code during development
to allow for re-use without regards to servers if desired, allowing for permission control through discord without the need for roles during runtime. The bot
also comes with an audio cog to play audio from Youtube (via yt-dlp).

<img width="1086" height="304" alt="image" src="https://github.com/user-attachments/assets/9ac38b6c-addf-4774-b379-db90535625ba" />

## Cog Library
To keep track of permissions and servers, [`lib/`](https://github.com/dylanwilks/discord-server-cogs/tree/main/lib) contains 3 modules each with
their own class:
- [`BaseCog`](https://github.com/dylanwilks/discord-server-cogs/blob/main/lib/basecog.py), deriving `commands.Cog`.
- [`OrderedCog`](https://github.com/dylanwilks/discord-server-cogs/blob/main/lib/orderedcog.py), deriving `BaseCog`.
- [`ServerCog`](https://github.com/dylanwilks/discord-server-cogs/blob/main/lib/servercog.py), deriving `OrderedCog`.

Basic functionality is described below, but more can be seen in their corresponding files.

### BaseCog
Responsible for keeping track of the commands each user and channel has access to. Provides functionality `get_users(self)` and `get_channels(self)` for instances of this class to 
fetch users and channels respectively that have access to its commands, along with static methods `get_command_users(command_name: str)` and `get_command_channels(command_name: str)`
which function similarly but more finely.

Note that if a channel is granted access to some commands, a webhook to that channel will be generated. This will also generate a text file containing the URL of the webhook. The path
to where this text file should be stored can be changed in the config file.

### OrderedCog
Extends `BaseCog` by allowing permission levels to be set for each command. A user/channel with permission level $n$ will be able to call every command in an instance of this class that
requires permission level $n$ or less, inducing an order/hierarchy on the commands (hence the name 'ordered', stemming from totally ordered posets). A static method
`assert_perms(user_perm: int, channel_perm: int)` is provided for use as a decorator to accomplish this, demonstated below.

```python
from lib.orderedcog import OrderedCog
...
@OrderedCog.assert_perms(user_perm=0, channel_perm=0)
async def command(
    self,
    ctx: commands.Context
) -> None:
...
```
> **Note:** Setting only the permission level for a user or channel is not enough to enable use of the cog's commands. You will still have to permit the user or channel to use those commands.

### ServerCog
This does not introduce a new sort of permission required by users/channels but instead keeps track of the state of a server. By default the class asserts that states
`ACTIVE` and `INACTIVE` are members of a class called `State` that is derived from `enum.IntFlag`, but more states can be added if desired.

The state tracked by an instance of this class can be updated using `_update_state(self, state: 'State')` and fetched with `get_state(self)`. To assert a certain state
for a command to be used, use the static method `assert_state(state: 'State')`:
```python
from lib.servercog import ServerCog
...
@ServerCog.assert_state(state=State.ACTIVE)
async def command(
    self,
    ctx: commands.Context
) -> None:
...
```
There are some example cogs that use this class in [`cogs/servers/`](https://github.com/dylanwilks/discord-server-cogs/tree/main/cogs/servers) that I use personally.

## Managing Permissions
Permissions are controlled using `sqlite`. If the aforementioned `commands.Cog` subclasses are used, they will generate their respective
tables that hold user/channel-command pairs, user/channel-cog permission levels, or cog states.

Each of the subclasses will load commands under the `db` group when an instance of theirs is added (and removed otherwise). These commands
are used for manipulating and fetching data from the tables. A full list of these commands can be seen by typing `!help db` when an instance
of these classes is loaded.

To get started, a user is to be set admin, granting permission to all commands. This can be done by supplying the `admin` command with the user's ID.

```sh
docker exec <container_name> admin <user_id>
```

## Managing Servers
Using both `_update_state` and `get_state` in tandem with the `subprocess` library you can create a task that periodically checks the state of a server
and update it accordingly if necessary. You can thus use `subprocess` to also control state correctly if the server supports it. An example of this can be 
seen [here](https://github.com/dylanwilks/discord-server-cogs/blob/main/cogs/servers/satisfactory-server.py).

<img width="1091" height="201" alt="image" src="https://github.com/user-attachments/assets/48e6906c-dcc0-4e0d-a4e1-aacbae751389" />

## Config
Settings, configurations, and some constants are stored in `.env` and JSON files. Values in `.env` are intended for initializing the bot, while values in 
JSON files are settings that can be changed during runtime.

### Environment Variables
| Parameter             |  Default   | Function                                                      |
|-----------------------|:----------:|---------------------------------------------------------------|
| `BOT_TOKEN` | `REQUIRED` | Token of the bot |
| `BOT_NAME` | `""` | If blank then no name change is performed |
| `BOT_ICON` | `""` | Sets the icon of the bot and its webhooks if not blank |
| `BOT_DB` | `~/db/bot.db` | Path for the `.db` file |
| `BOT_PREFIX` | `!` | Set the prefix for your commands |
| `BOT_WATCHER_SECONDS` | `1.0` | Number of seconds to wait for updates to .py files in `cogs/` |
| `BOT_NAME_MINUTES` | `10.0` | Number of minutes to wait for name update and change back |
| `BOT_CONSTANTS` | `~/config/constants.json` | Path for the constants JSON file |
| `BOT_CONFIG` | `~/config/config.json` | Path for the config JSON file |
| `BOG_COGS` | `~/config/cogs.json` | Path for the cogs JSON file |
| `PRIVATE_KEYS` | `""` | ssh keys mounted in to add to the ssh agent |

You may add extra fields to the JSON files. A class `Config` is provided to aid in reading JSON files, and may be used like so:
```python
from lib.config import Config
...
constants = Config.from_json(os.environ["BOT_CONSTANTS"])
await ctx.send(eval(constants.messages.servers.no_subcommand))
...
```
## Usage/Development
Some notes on developing extensions/cogs during runtime and utilizing existing commands:

### Adding and modifying a extension/cog
All development should be done outside of the container. Extensions should be mounted in. If you have added an extension `cogs/path/ext.py` during runtime, running 
```
!bot load-extension cogs.path.ext
```
will load the extension. Modifications to any extensions loaded within [`cogs/`](https://github.com/dylanwilks/discord-server-cogs/tree/main/cogs) 
and its subdirectories will cause them to be automatically reloaded. All extensions are loaded on container start unless they begin with `_`.
Keep in mind that `!help` will only list commands that can be used by the caller.

### Audio
The audio cog in [`cogs/audio.py`](https://github.com/dylanwilks/discord-server-cogs/tree/main/cogs/audio.py) provides basic audio 
functionality to queue, pause, loop, and rotate videos from Youtube (audio only).
Commands require the user to be in a voice channel to operate. Additional configs are in [`cogs.json`](https://github.com/dylanwilks/discord-server-cogs/tree/main/cogs/cogs.json).
For yt-dlp to solve Javascript challenges the image only comes with quickjs at the moment. If this causes slow play times,
comment out the following line (or build the image with a faster alternative):
```python
'js_runtimes': {'quickjs': {'path': None}},
```

## Running and logging
Preferably with Docker Compose, have a file called `docker-compose.yml` with
```
services:
  discord-server-cogs:
    image: dylanwilks/discord-server-cogs
    container_name: discord-server-cogs
    build:
      context: .
      dockerfile: Dockerfile
    env_file:
      - .env
    volumes:
      - db:/usr/src/app/db
      - ./cogs:/usr/src/app/cogs
      - ./config:/usr/src/app/config
      - ./scripts:/usr/src/app/scripts
    restart: always

volumes:
  db:
    name: db
```
and then call
```
docker compose up
```
to build and run the container.

All messages from the program will be printed to the container's shell and can thus be read with `docker attach` or `docker logs`.
More detailed logs are present in `handler.log`, `errors.log`, and `commands.log`, which are located in the container. Their paths
are specified in [`config.json`](https://github.com/dylanwilks/discord-server-cogs/tree/main/config/config.json).
