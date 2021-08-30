import os
import discord
from discord.ext import commands
from discord_slash.utils.manage_commands import create_option, create_choice
from algorithm import main
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import os
from discord_slash import SlashCommand, SlashContext
import random

client = commands.Bot(command_prefix='$')
client.remove_command('help')
slash = SlashCommand(client, sync_commands=True)


def read_points(message):
    vals = message.content.split("\n")
    points = []
    for item in vals:
        point = item.split()
        try:
            x = int(point[0])
            y = int(point[1])
            points.append([x, y])
        except:
            pass
    return points


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('/help'))
    print('Logged in as {0.user}'.format(client))


@slash.slash(name='ping', description='Shows the bot latency')
async def _ping(ctx: SlashContext):
    await ctx.send(f'Bot speed = {round(client.latency * 1000)}ms')


@slash.slash(
    name='search',
    description='Search the web for an image',
    options=[
        create_option(
            name='name',
            description='What do you want to search up?',
            required=True,
            option_type=3
        ),
        create_option(
            name='index',
            description='What image number from 1-30',
            required=False,
            option_type=4,
        )
    ]
)
async def _search(ctx: SlashContext, name: str, index: int = 1):
    if index < 1 or index > 30:
        await ctx.send('Index number is out of range')
        return
    await ctx.send(f'Your google image search for {name} at the index of {index} will be sent soon.')
    url = 'https://www.google.com/search?q=REPLACE&tbm=isch'
    arg = name.replace(" ", "+")
    link = url.replace("REPLACE", arg)
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)
    driver.find_element_by_xpath(f'//*[@id="islrg"]/div[1]/div[{index}]/a[1]/div[1]/img').screenshot('search.png')
    driver.close()
    await ctx.send(file=discord.File('search.png'))


@slash.slash(
    name='avatar',
    description='Get the profile picture of the user',
    options=[
        create_option(
            name='username',
            description='Name of the user',
            required=False,
            option_type=6
        )
    ]
)
async def _avatar(ctx, username=None):
    try:
        av = username.avatar_url
        name = username
    except:
        av = ctx.author.avatar_url
        name = ctx.author
    av_embed = discord.Embed(title=f"{name}'s avatar", color=0xf5f542)
    av_embed.set_image(url=av)
    await ctx.send(embed=av_embed)


@slash.slash(
    name='chess',
    description='Find stats on a player from chess.com',
    options=[
        create_option(
            name='username',
            description='Username of the player',
            required=True,
            option_type=3
        ),
        create_option(
            name='gamemode',
            description='Pick a gamemode',
            option_type=3,
            required=True,
            choices=[
                create_choice(name='Rapid', value='rapid'),
                create_choice(name='Blitz', value='blitz'),
                create_choice(name='Bullet', value='bullet')]
        )
    ]
)
async def _chess(ctx: SlashContext, username: str, gamemode: str):
    acceptable_url = 'https://www.chess.com/member/' + username
    r = requests.get(acceptable_url)
    if r.status_code != 200:
        await ctx.send("No chess.com user with that username.")
        return

    # Retrieves the source code of the website
    url = 'https://www.chess.com/stats/live/' + gamemode + '/' + username
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.find_all('script')

    # retrieves the player's profile picture
    icon = soup.find('img')
    player_profile = icon['src']
    
    # The username with proper casing found in the source code
    user = ''.join(results[-1].contents)
    user = ''.join(user.split())
    user = user.partition('username:\'')[2]
    user = user.partition('\',leaderboardPath')[0]

    # Converts the dictionary in the source code to a usable format
    data = ''.join(results[-1].contents)  # The dict in the source code is in the last <script>
    data = ''.join(data.split())
    data = data.partition('.stats=')[2]
    data = data.partition(',days')[0] + '}'
    data = data.replace("chartData", "\"chartData\"")
    data = data.replace("userData", "\"userData\"")
    data = json.loads(data)

    # Create the embed to send to the user
    chessEmbed = discord.Embed(color=0x6c9d41)
    chessEmbed.set_author(name=f'{user}\'s stats for {gamemode.capitalize()}', icon_url='https://bit.ly/3wjtIDE')
    chessEmbed.set_thumbnail(url=player_profile)

    highestRatingTime = re.sub("[A-Za-z]+", lambda ele: " " + ele[0] + " ",
                               data['userData']['highestRating']['time'])
    highestRatingTime = re.sub(r'(?<=,)', r' ', highestRatingTime)
    ratings_desc = (f"```Their rating:   {data['userData']['rating']}\n"
                    f"Highest rating: {data['userData']['highestRating']['rating']} achieved on{highestRatingTime}\n"
                    f"Avg Accuracy:   {data['userData']['accuracy']['average']}%```")
    chessEmbed.add_field(name="USER RATINGS", value=ratings_desc, inline=False)

    total_games = int(data['chartData']['black']['games']) + int(data['chartData']['white']['games'])
    all_games_desc = (f"```Total:  {total_games}\n"
                      f"Wins:   {data['chartData']['all']['wins']}\n"
                      f"Losses: {data['chartData']['all']['losses']}\n"
                      f"Draws:  {data['chartData']['all']['draws']}```")
    chessEmbed.add_field(name="ALL GAMES", value=all_games_desc, inline=True)

    white_games_desc = (f"```Total:  {data['chartData']['white']['games']}\n"
                        f"Wins:   {data['chartData']['white']['wins']}\n"
                        f"Losses: {data['chartData']['white']['losses']}\n"
                        f"Draws:  {data['chartData']['white']['draws']}```")
    chessEmbed.add_field(name="WHITE GAMES", value=white_games_desc, inline=True)

    black_games_desc = (f"```Total:  {data['chartData']['black']['games']}\n"
                        f"Wins:   {data['chartData']['black']['wins']}\n"
                        f"Losses: {data['chartData']['black']['losses']}\n"
                        f"Draws:  {data['chartData']['black']['draws']}```")
    chessEmbed.add_field(name="BLACK GAMES", value=black_games_desc, inline=True)

    friends_opponents_desc = (f"```Leaderboard Rank: {data['userData']['leaderboardRank']}\n"
                              f"Friend count: {data['userData']['friendCount']}\n"
                              f"Rank among their friends: {data['userData']['friendRank']}\n"
                              f"Percentile: {data['userData']['percentile']}%\n"
                              f"Highest win streak: {data['userData']['winningStreak']}\n"
                              f"Best win: {data['userData']['bestWin']['rating']} against {data['userData']['bestWin']['player']}```")
    chessEmbed.add_field(name="FRIEND/OPPONENT STATS", value=friends_opponents_desc, inline=False)
    chessEmbed.add_field(name='MORE INFO HERE', value=url, inline=False)
    await ctx.send(embed=chessEmbed)


@slash.slash(name='help', description='Show the commands of the bot')
async def _help(ctx):
    helpEmbed = discord.Embed(color=0xFF0000)
    helpEmbed.set_author(name='Help')
    chess_desc = "Type '/chess' followed by the chess.com username and the gamemode."
    helpEmbed.add_field(name="CHESS.COM PLAYER DATA SEARCH", value=chess_desc, inline=False)
    helpEmbed.add_field(name='CONVEX HULL', value='Create a convex hull with your input points', inline=False)
    plot_desc1 = ("Type '$plot' followed by the triple tilde and begin typing points on"
                  " each new line and finish it with another triple tilde on its own line.")
    helpEmbed.add_field(name="Method 1", value=plot_desc1, inline=True)
    plot_desc2 = ("Type '$plot' followed by 'shift + enter'"
                  " which moves to a new line and begin typing in points as normal.")
    helpEmbed.add_field(name="Method 2", value=plot_desc2, inline=True)
    search_desc = ("Type '/search' followed by your google images search. You can type a number (1-30) "
                   "after the search to indicate the index number of your google image search "
                   "if you don't simply want the first image. The index is based off of Chromium's "
                   "Google Images and not necessarily your desired browser.")
    helpEmbed.add_field(name='GOOGLE IMAGES SEARCH', value=search_desc, inline=False)
    avatar_desc = "Enter a username for their avatar or leave it empty for your own avatar."
    helpEmbed.add_field(name='AVATAR VIEWER', value=avatar_desc, inline=False)
    await ctx.send(embed=helpEmbed)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg.startswith("$plot"):
        main(read_points(message))  # executes convex hull algorithm
        await message.reply(file=discord.File('out.png'), mention_author=False)

    if msg.startswith('nice') or ' nice' in msg:
        await message.add_reaction('👍')

    await client.process_commands(message)

client.run(os.getenv('TOKEN'))
