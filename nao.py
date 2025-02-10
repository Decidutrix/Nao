from turtle import title
import discord
from discord.ext import commands
import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load env variables
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')


#Define bot command prefix
intents = discord.Intents.default()
intents.reactions = True
intents.messages = True
intents.message_content = True #needed to handle reactions
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Bot ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


# Event : Member Join
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="name_here")
    if channel:
        await channel.send(f"Welcome to Azorius {member.mention}! Please read and accept the rules in the rules channel <3.")

# Event : Member Leave
@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(channel_id_here)
    if channel:
        await channel.send(f"{member.mention} has left the guild.")


# Command : Party Up
@bot.command(name="partyup")
async def partyup(ctx, party_name: str, num_members: int, *dungeon: str):
    if num_members <1:
        await ctx.send("A party must always have at least 1 member.")
        return
    
    role_id = os.getenv('role_id_here')
    # Customizing the party request
    response = (f"The **{party_name}** party is requesting help <@&{role_id}>! They need {num_members} more for {dungeon}, please react with ✅ to answer the call!")
    
    party_message = await ctx.send(response)

    #add the reation to the message
    await party_message.add_reaction("✅")

    # Wait for user to react
    def check(reaction, user):
        return reaction.message.id == party_message.id and str(reaction.emoji) == "✅" and user != bot.user
    
    #list of users who reacted
    party_members = []

    while len(party_members) < num_members:
        reaction, user = await bot.wait_for("reaction_add", check=check)

        if user not in party_members:
            party_members.append(user)

            await ctx.send(f"{user.display_name} has joined the {party_name} party!")

        #party full
        await ctx.send(f"the {party_name} party is full with {len(party_members)}.")

        await party_message.clear_reactions()


# Mabi wiki page
async def search_mabinogi_wiki(query):
    """
    Search the Mabinogi Wiki for a specific query and return the first result.
    """

    try:
        # Format the query from URL
        formatted_query = query.replace(" ", "_")
        url = f"https://wiki.mabinogiworld.com/view/{formatted_query}"

        # Send a request to Mabi Wiki
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title of page
        title = soup.find("h1", id="firstHeading").text.strip()

        contents = soup.find("div", class_="mw-parser-output")
        if contents:
            return f"**{title}**\n{url}"
        else:
            return f"No content found."
    except Exception as e:
        return f"An error occurred: {str(e)}"   

# Command : Search Mabi Wiki
@bot.command(name="wiki")
async def wiki(ctx, *, query: str):
    """
    Search the Mabinogi Wiki for a specific query.
    Usage: !wiki <query>
    Example: !wiki Holy Water of Lymilark
    """
    result = await search_mabinogi_wiki(query)
    await ctx.send(result)


## Rules channel stuff

# Configuration
RULES_CHANNEL_ID = channel_id_here
ACCEPTED_ROLE_ID = role_id_here
REACTION_EMOJI = "✅"

@bot.event
async def on_raw_reaction_add(payload):
    """
    Handle reactions added to messages in the rules channel
    """
    # Check if the reaction is in the rules channel
    if payload.channel_id == RULES_CHANNEL_ID and str(payload.emoji) == REACTION_EMOJI:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        # Check if the member is not a bot
        if member and not member.bot:
            # Assign role to member
            role = guild.get_role(ACCEPTED_ROLE_ID)
            if role:
                await member.add_roles(role)
                print(f"Assigned {role} to {member.display_name}")

@bot.event
async def on_raw_reaction_remove(payload):
    """
    Handle reactions removed from message in the rules channel
    """
    # Check if the reaction is in the rules channel
    if payload.channel_id == RULES_CHANNEL_ID and str(payload.emoji) == REACTION_EMOJI:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        # Check if the member is not a bot
        if member and not member.bot:
            # Remove the role from the member
            role = guild.get_role(ACCEPTED_ROLE_ID)
            if role:
                await member.remove_roles(role)
                print(f"Removed {role} from {member.display_name}")

# Careful this posts every time the bot goes live. After the 1st post I comment all of this event.
@bot.event
async def on_ready():
     rules_channel = bot.get_channel(RULES_CHANNEL_ID)
     if rules_channel:
         rules_message = (
             "**PLEASE READ**\nPlease follow all of Discord's official [ToS](https://discord.com/terms) and [Guidelines](https://discord.com/guidelines)\nDiscrimination against players will not be tolerated and will result in a permanent ban. This server is for both new and returning players.\n**NO** Spamming\n**NO** Politics\n**NO** Hate speech (for example: racism, anti-lgbtq, threats, harassment, etc. this is a automatic perma-ban offense)\n**NO** use of @everyone and/or @here , if you need to get the attention of the entire server please use @Milletians\n**NO** Arguing with GMs, if you feel that you're being targeted or treated unfairly please DM @Leader\n**NO** Drama\n**Please** respect everyone's time, do not ghost members, if something comes up just send a quick message in the server.\n\n*Streamer Rules*\nYou have a right to post a notification of your live stream during events such as the [Glenn Bearna Winter Event](https://tinyurl.com/27ta55zd) and other streams you do. Do NOT spam multiple links! You are also not entitled to viewership, so do not expect viewership from the server. Do not also ask the streamer, GMs or the Leader to not have the links posted. If you don't want to see the links let a GM or the Leader know and they will assist you in turning off the notifications of the channel.\nTo agree to these rules please use the ✅."
         )
         message = await rules_channel.send(rules_message)
         await message.add_reaction(REACTION_EMOJI)

#run the bot
bot.run(TOKEN)
