import discord
import json
from discord.ext import commands

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
async def dwc_add(ctx, member: discord.Member, roblox_profile: str):
    db = load_db()
    discord_id = member.id
    db[str(discord_id)] = roblox_profile
    save_db(db)
    member = bot.get_user(discord_id)
    target_role_member = ctx.guild.get_member(int(discord_id))
    if member:
        member_name = member.name + "#" + member.discriminator
        role = discord.utils.get(ctx.guild.roles, name="**DEAL WITH CAUTION**")
        await target_role_member.add_roles(role)
    else:
        member_name = f"unknown user ({discord_id})"
    embed = discord.Embed(title="Success", color=discord.Color.green())
    embed.add_field(name="Discord ID", value=f"<@{discord_id}> ({member_name})")
    embed.add_field(name="Roblox Profile", value=roblox_profile)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_role(1025610261702377573)
async def dwc_remove(ctx, member: discord.Member):
    db = load_db()
    discord_id = member.id
    if str(discord_id) in db:
        roblox_profile = db[str(discord_id)]
        del db[str(discord_id)]
        save_db(db)
        member = bot.get_user(discord_id)
        target_role_member = ctx.guild.get_member(int(discord_id))
        if member:
            member_name = member.name + "#" + member.discriminator
            role = discord.utils.get(ctx.guild.roles, name="**DEAL WITH CAUTION**")
            await target_role_member.remove_roles(role)
        else:
            member_name = f"unknown user ({discord_id})"
        embed = discord.Embed(title="Success", color=discord.Color.green())
        embed.add_field(name="Discord ID", value=f"<@{discord_id}> ({member_name})")
        embed.add_field(name="Roblox Profile", value=roblox_profile)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="Message", value=f"{discord_id} was not found in the database.")
        await ctx.send(embed=embed)


@bot.command()
@commands.has_role(1025610261702377573)
async def dwcdb(ctx, search_string: str):
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
            results.append(f"Discord ID: <@{search_string}> ({member_name})\nRoblox Profile: {roblox_profile}")
            found = True
    else:
        for discord_id, roblox_profile in db.items():
            if roblox_profile == search_string:
                member = bot.get_user(int(discord_id))
                if member:
                    member_name = member.name + "#" + member.discriminator
                else:
                    member_name = f"unknown user ({discord_id})"
                results.append(f"Discord ID: <@{discord_id}> ({member_name})\nRoblox Profile: {roblox_profile}")
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
        results.append(f"Discord ID: <@{discord_id}> ({member_name})\nRoblox Profile: {roblox_profile}")

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
async def dwc_send(ctx, channel: discord.TextChannel, query: str):
    db = load_db()
    results = []

    for discord_id, roblox_profile in db.items():
        member = bot.get_user(int(discord_id))
        if member:
            member_name = member.name + "#" + member.discriminator
        else:
            member_name = f"unknown user ({discord_id})"

        if query.lower() in roblox_profile.lower() or query.lower() in member_name.lower():
            results.append(f"Discord ID: <@{discord_id}> ({member_name})\nRoblox Profile: {roblox_profile}")

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
async def cmds(ctx):
    embed = discord.Embed(title="Available Commands", color=discord.Color.blue())
    embed.add_field(name="/dwc_add {discord-mention} {roblox profile link/username}", value="Adds a new entry to the database", inline=False)
    embed.add_field(name="/dwc_remove {discord-mention}", value="Removes an entry from the database", inline=False)
    embed.add_field(name="/dwcdb {roblox profile link/username or discord id}", value="Searches the database for entries that match the given query", inline=False)
    embed.add_field(name="/dwc_send {channel} {query/string}", value="Searches the database and sends results to a specified channel", inline=False)
    embed.add_field(name="/dwclist", value="Lists all entries in the database", inline=False)
    embed.add_field(name="/cmds", value="Shows all available commands and their description", inline=False)
    await ctx.send(embed=embed)


bot.run('BOT TOKEN HERE')
