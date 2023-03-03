# Discord Bot for Managing Roblox Profile Links
This Discord bot allows users with a certain role to add and remove Roblox profile links for members of the server. 
It also provides a command to search for members by their Roblox profile link, and a command to list all the members with their Roblox profile links.

### Requirements
```
Python 3.8 or higher
discord.py library
json library
```

# Installation

**Clone the repository or download the source code.**

> **Install the required libraries using pip:**
```python
pip install discord.py
```
> Create a new Discord bot in the Discord developer portal and get its token.

> Create a new role in your Discord server with the desired name and permissions.

> Replace the discord token with your discord bot token at the bottom:

`bot.login=<your_discord_bot_token>`

> Edit the dwc_add command decorator to use the ID of the role you created in step 4:

```python
@commands.has_role(<your_role_id>)
```
> Run the bot using the following command:

`python bot.py`

# Usage
The bot responds to the following commands:

```
/dwc_add <@member> <roblox_profile>: Adds a Roblox profile link for the specified member. Requires the role specified in step 7.
/dwc_remove <@member>: Removes the Roblox profile link for the specified member. Requires the role specified in step 7.
/dwcdb <search_string>: Searches the database for members with the specified Roblox profile link or Discord ID.
/dwclist: Lists all the members in the database with their Roblox profile links.
```

# Contributing
If you want to contribute to this project, feel free to open an issue or submit a pull request. Make sure to follow the code style of the project and write clear commit messages.
