# discord-server-cogs

A personal discord bot made with discord.py that I host on a Raspberry Pi running Alpine Linux for managing servers and permissions. I've generalized the code during development
to allow for re-use without regards to servers if desired, allowing for permission control through discord without the need for roles during runtime.

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
to where this text file should be stored can be changed in the class definition under `async def create_webhook(self, channel)`. Likewise, generating a webhook can be disabled altogether 
by removing `await self.create_webhooks()` under `async def cog_load(self)`.

### OrderedCog
Extends `BaseCog` by allowing permission levels to be set for each command. A user/channel with permission level $n$ will be able to call every command in an instance of this class that
requires permission level $n$ or less, inducing an order/hierarchy on the commands (hence the name 'ordered', stemming from totally ordered posets). A static method
`assert_perms(user_perm: int, channel_perm: int)` is provided for use as a decorator to accomplish this, as demonstated below.

```python
...
@OrderedCog.assert_perms(user_perm=0, channel_perm=0)
async def command(
    self,
    ctx: commands.Context
) -> None:
...
```

### ServerCog
This does not introduce a new sort of permission required by users/channels but instead keeps track of the state of a server. By default the class asserts that states
`ACTIVE` and `INACTIVE` are members of a class called `State` that is derived from `enum.IntFlag`, but more states can be added if desired.

The state tracked by an instance of this class can be updated using `_update_state(self, state: 'State')` and fetched with `get_state(self)`. To assert a certain state
for a command to be used, use the static method `assert_state(state: 'State')`:
```python
...
@ServerCog.assert_state(state=State.ACTIVE)
async def command(
    self,
    ctx: commands.Context
) -> None:
...
```

## Managing Permissions
Permissions are controlled using `sqlite`. If the aforementioned `commands.Cog` subclasses are used, they will generate their respective
tables that hold user/channel-command pairs, user/channel-cog permission levels, or cog states.

Each of the subclasses will load commands under the `db` group when an instance of theirs is added (and removed otherwise). These commands
are used for manipulating and fetching data from the tables. A full list of these commands can be seen by typing `!help db` when an instance
of these classes is loaded.

To get started, a user is to be set admin, granting permission to all commands. This can be done by supplying `admin.py` with the user's ID.

```sh
python3 admin.py <user_id>
```

## Managing Servers
Using both `_update_state` and `get_state` in tandem with the `subprocess` library you can create a task that periodically checks the state of a server
and update it accordingly if necessary. You can thus use `subprocess` to also control state correctly if the server supports it. An example of this can be 
seen [here](https://github.com/dylanwilks/discord-server-cogs/blob/main/cogs/servers/satisfactory-server.py).

<img width="1091" height="201" alt="image" src="https://github.com/user-attachments/assets/48e6906c-dcc0-4e0d-a4e1-aacbae751389" />
