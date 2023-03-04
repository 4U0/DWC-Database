import discord
import json
from discord.ext import commands
from typing import List, Tuple, Union

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='/', intents=intents)


def load_db():
    with open('database.json', 'r') as f:
        db = json.load(f)
    return db

def save_db(db):
    with open('database.json', 'w') as f:
        json.dump(db, f)


@bot.command()
@commands.has_role(1025610261702377573)
async def dwc_add(ctx, user: Union[discord.Member, int], *, roblox_profile: str):
    if isinstance(user, discord.Member):
        user = user.id
    db = load_db()
    try:
        user = int(user)
    except ValueError:
        await ctx.send("Invalid user! Please enter a valid Discord ID or mention.")
        return
    #discord_id = member.id
    db[str(user)] = roblox_profile
    save_db(db)
    member = bot.get_user(user)
    target_role_member = ctx.guild.get_member(int(user))
    if member:
        member_name = member.name + "#" + member.discriminator
        role = discord.utils.get(ctx.guild.roles, name="**DEAL WITH CAUTION**")
        await target_role_member.add_roles(role)
    else:
        member_name = f"unknown user ({user})"
    embed = discord.Embed(title="Success", color=discord.Color.green())
    embed.add_field(name="Discord ID", value=f"<@{user}>")
    embed.add_field(name="Reason", value=roblox_profile)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_role(1025610261702377573)
async def dwc_remove(ctx, user: Union[discord.Member, int]):
    if isinstance(user, discord.Member):
        user = user.id
    db = load_db()
    try:
        user = int(user)
    except ValueError:
        await ctx.send("Invalid user! Please enter a valid Discord ID or mention.")
        return
    #discord_id = member.id
    if str(user) in db:
        roblox_profile = db[str(user)]
        del db[str(user)]
        save_db(db)
        member = bot.get_user(user)
        target_role_member = ctx.guild.get_member(int(user))
        if member:
            member_name = member.name + "#" + member.discriminator
            role = discord.utils.get(ctx.guild.roles, name="**DEAL WITH CAUTION**")
            await target_role_member.remove_roles(role)
        else:
            member_name = f"unknown user ({user})"
        embed = discord.Embed(title="Success", color=discord.Color.green())
        embed.add_field(name="Discord ID", value=f"<@{user}>")
        embed.add_field(name="Reason", value=roblox_profile)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="Message", value=f"{user} was not found in the database.")
        await ctx.send(embed=embed)


@bot.command()
@commands.has_role(1025610261702377573)
async def dwcdb(ctx, *search_words: str):
    search_string = " ".join(search_words)
    db = load_db()
    found = False
    results = []
    if search_string.isdigit():
        if search_string in db:
            roblox_profile = db[search_string]
            member = bot.get_user(int(search_string))
            if member:
                member_name = member.name + "#" + member.discriminator
            else:
                member_name = f"unknown user ({search_string})"
            results.append(f"**Discord ID**: <@{search_string}>\n[⚠️] **Reason**: {roblox_profile}")
            found = True
    else:
        for discord_id, roblox_profile in db.items():
            if all(word.lower() in roblox_profile.lower() for word in search_words):
                member = bot.get_user(int(discord_id))
                if member:
                    member_name = member.name + "#" + member.discriminator
                else:
                    member_name = f"unknown user ({discord_id})"
                results.append(f"**Discord ID**: <@{discord_id}>\n[⚠️] **Reason**: {roblox_profile}")
                found = True
    if found:
        embed = discord.Embed(title="Results", color=discord.Color.blue())
        embed.description = "\n\n".join(results)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="Message", value=f"No results found for '{search_string}'.")
        await ctx.send(embed=embed)

@bot.command()
async def dwclist(ctx):
    db = load_db()
    if not db:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="Message", value="The database is empty.")
        await ctx.send(embed=embed)
        return

    results = []
    for discord_id, roblox_profile in db.items():
        member = bot.get_user(int(discord_id))
        if member:
            member_name = member.name + "#" + member.discriminator
        else:
            member_name = f"unknown user ({discord_id})"
        results.append(f"**Discord ID**: <@{discord_id}>\n[⚠️] **Reason**: {roblox_profile}")

    current_page = 0
    total_pages = (len(results) - 1) // 10 + 1
    embed = discord.Embed(title="Results", color=discord.Color.blue())
    embed.description = "\n\n".join(results[:10])
    embed.set_footer(text=f"Page {current_page + 1} of {total_pages}")
    message = await ctx.send(embed=embed)
    if total_pages > 1:
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

            if str(reaction.emoji) == "➡️" and current_page < total_pages - 1:
                current_page += 1
                start_index = current_page * 10
                end_index = min(start_index + 10, len(results))
                embed.description = "\n\n".join(results[start_index:end_index])
                embed.set_footer(text=f"Page {current_page + 1} of {total_pages}")
                await message.edit(embed=embed)
                await message.remove_reaction(reaction, user)
            elif str(reaction.emoji) == "⬅️" and current_page > 0:
                current_page -= 1
                start_index = current_page * 10
                end_index = min(start_index + 10, len(results))
                embed.description = "\n\n".join(results[start_index:end_index])
                embed.set_footer(text=f"Page {current_page + 1} of {total_pages}")
                await message.edit(embed=embed)
                await message.remove_reaction(reaction, user)
            else:
                await message.remove_reaction(reaction, user)

@bot.command()
@commands.has_role(1025610261702377573)
async def dwc_send(ctx, channel: discord.TextChannel, *, query: str):
    db = load_db()
    results = []

    for discord_id, roblox_profile in db.items():
        member = bot.get_user(int(discord_id))
        if member:
            member_name = member.name + "#" + member.discriminator
        else:
            member_name = f"unknown user ({discord_id})"

        if query.lower() in roblox_profile.lower() or query.lower() in member_name.lower():
            results.append(f"**Discord ID**: <@{discord_id}>\n[⚠️] **Reason**: {roblox_profile}")

    if not results:
        embed = discord.Embed(title="No Results", color=discord.Color.red())
        embed.add_field(name="Message", value="There were no matches for the given query.")
        await ctx.send(embed=embed)
        return

    current_page = 0
    total_pages = (len(results) - 1) // 10 + 1
    embed = discord.Embed(title="Results", color=discord.Color.blue())
    embed.description = "\n\n".join(results[:10])
    embed.set_footer(text=f"Page {current_page + 1} of {total_pages}")
    message = await channel.send(embed=embed)
    if total_pages > 1:
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

            if str(reaction.emoji) == "➡️" and current_page < total_pages - 1:
                current_page += 1
                start_index = current_page * 10
                end_index = min(start_index + 10, len(results))
                embed.description = "\n\n".join(results[start_index:end_index])
                embed.set_footer(text=f"Page {current_page + 1} of {total_pages}")
                await message.edit(embed=embed)
                await message.remove_reaction(reaction, user)
            elif str(reaction.emoji) == "⬅️" and current_page > 0:
                current_page -= 1
                start_index = current_page * 10
                end_index = min(start_index + 10, len(results))
                embed.description = "\n\n".join(results[start_index:end_index])
                embed.set_footer(text=f"Page {current_page + 1} of {total_pages}")
                await message.edit(embed=embed)
                await message.remove_reaction(reaction, user)
            else:
                await message.remove_reaction(reaction, user)


@bot.command()
@commands.has_role(1025610261702377573)
async def dwc_edit(ctx, user: Union[discord.Member, int], *, roblox_profile: str):
    if isinstance(user, discord.Member):
        user = user.id
    db = load_db()
    try:
        user = int(user)
    except ValueError:
        await ctx.send("Invalid user! Please enter a valid Discord ID or mention.")
        return
    if str(user) in db:
        del db[str(user)]
        db[str(user)] = roblox_profile
        save_db(db)
        member = bot.get_user(user)
        if member:
            member_name = member.name + "#" + member.discriminator
        else:
            member_name = f"unknown user ({user})"
        embed = discord.Embed(title="Success", color=discord.Color.green())
        embed.add_field(name="Message", value=f"Updated Roblox profile for <@{user}> in the database.")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="Message", value=f"No entry found for Discord ID '{user}' in the database.")
        await ctx.send(embed=embed)




@bot.command()
async def cmds(ctx):
    embed = discord.Embed(title="Available Commands", color=discord.Color.blue())
    embed.add_field(name="/dwc_add", value="Adds a user's Discord ID and Reason to the database.\nExample: `/dwc-add 123456789012345678/@Mention scammed $100`", inline=False)
    embed.add_field(name="/dwc_remove", value="Removes a user's Discord ID and Reason from the database.\nExample: `/dwc-remove 123456789012345678 or @Mention`", inline=False)
    embed.add_field(name="/dwcdb", value="Searches the database for a given Discord ID or Reason and returns any matching results.\nExamples: `/dwcdb 123456789012345678`, `/dwcdb charged back`", inline=False)
    embed.add_field(name="/dwc_edit", value="Edits the current reason for a user.\nExample: `/dwc-edit 123456789012345678 new reason`", inline=False)
    embed.add_field(name="/dwclist", value="Lists all users and their corresponding Roblox profile links in the database.\nExample: `/dwclist`", inline=False)
    embed.add_field(name="/dwc_send", value="Searches the database and sends results to a specified channel\nExample: `/dwc_send #dwc-db scammed $100`", inline=False)
    embed.add_field(name="/cmds", value="Shows all available commands and their description", inline=False)
    await ctx.send(embed=embed)


bot.run('BOT TOKEN HERE')
