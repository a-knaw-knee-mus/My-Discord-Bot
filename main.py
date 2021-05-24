import os
import discord
from discord.ext import commands
from algorithm import main
import re
from keep_alive import keep_alive
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import json

client = commands.Bot(command_prefix='$')
client.remove_command('help')

def read_points(message):
    vals = message.content.split("\n")
    points = []
    for item in vals:
        point = re.split('\s+', item)
        try:
            x = int(point[0])
            y = int(point[1])
            points.append([x, y])
        except:
            pass
    return points

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game('$help'))
  print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  if msg.startswith("$plot"):
    main(read_points(message))  # executes convex hull algorithm
    await message.channel.send(file=discord.File('out.png'))
  
  await client.process_commands(message)

@client.command()
async def help(ctx):
  helpEmbed = discord.Embed(color=0xFF0000)
  helpEmbed.set_author(name='Help')
  chess_desc = ("Type '$chess' followed by the chess.com username and the gamemode "
                "(blitz, rapid or bullet) to get information on the user for the desired gamemode.")
  helpEmbed.add_field(name="CHESS.COM PLAYER DATA SEARCH", value = chess_desc, inline=False)
  helpEmbed.add_field(name='CONVEX HULL', value='Create a convex hull with your input points', inline=False)
  plot_desc1 = ("Type '$plot' followed by the triple tilde and begin typing points on"
            " each new line and finish it with another triple tilde on its own line.")
  helpEmbed.add_field(name="Method 1", value=plot_desc1, inline=True)
  plot_desc2 = ("Type '$plot' followed by 'shift + enter'"
              " which moves to a new line and begin typing in points as normal.")
  helpEmbed.add_field(name="Method 2", value=plot_desc2, inline=True)
  search_desc = ("Type '$search' followed by your google images search. You can type a number (1-20) "
          "after $search to indicate the index number of your google image search "
          "if you don't simply want the first image. The index is based off of Chromium's "
          "Google Images and not necessarily your desired browser.")
  helpEmbed.add_field(name='GOOGLE IMAGES SEARCH', value=search_desc, inline=False)
  await ctx.send(embed=helpEmbed)

@client.command()
async def search(ctx, *, arg):
  url = 'https://www.google.com/search?q=REPLACE&tbm=isch'
  text = arg.split(' ')
  num = 1
  try:
    num = int(text[0])
    if num < 1 or num > 20:
      await ctx.send("Your index number is out of range.")
      return
    arg = arg.partition(' ')[2]
  except: 
    pass 
  arg = arg.replace(" ", "+")
  link = url.replace("REPLACE", arg)
  chrome_options = Options()
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--disable-dev-shm-usage')
  driver = webdriver.Chrome(options=chrome_options)
  driver.get(link)
  driver.find_element_by_xpath(f'//*[@id="islrg"]/div[1]/div[{num}]/a[1]/div[1]/img').screenshot('search.png')
  driver.close()
  await ctx.send(file=discord.File('search.png'))

@client.command()
async def chess(ctx, *, arg):
  text = arg.split(' ')

  # Error check the username
  acceptable_url = 'https://www.chess.com/member/' + text[0]
  r = requests.get(acceptable_url)
  if r.status_code != 200:
    await ctx.send("No chess.com user with that username.")
    return
  
  # Error check the gamemode
  game_mode = 'rapid' # default gamemode if the user doesn't specify one=
  if len(text) == 1:
    await ctx.send('No gamemode was specified so this data is for the rapid gamemode.')
  elif text[1].lower() == 'rapid' or text[1].lower() == 'blitz' or text[1].lower() == 'bullet':
    game_mode = text[1]
  else:
    await ctx.send('That gamemode does not exist so this data is for the rapid gamemode.')

  # Retrieves the source code of the website
  url = 'https://www.chess.com/stats/live/' + game_mode + '/' + text[0]
  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'html.parser')
  results = soup.find_all('script')

  # retrieves the player's profile picture
  icon = soup.find('img')
  player_profile = icon['src']

  # Converts the dictionary in the source code to a useable format
  data = ''.join(results[-1].contents) # The dict in the source code is in the last <script>
  data = ''.join(data.split())
  data = data.partition('.stats=')[2]
  data = data.partition(',ratings')[0] + '}'
  data = data.replace("chartData", "\"chartData\"")
  data = data.replace("userData", "\"userData\"")
  data = json.loads(data)

  # Create the embed to send to the user
  chessEmbed = discord.Embed(color=0x6c9d41)
  chessEmbed.set_author(name=f'{text[0]}\'s stats for {game_mode}', icon_url='https://bit.ly/3wjtIDE')
  chessEmbed.set_thumbnail(url=player_profile)

  highestRatingTime = re.sub("[A-Za-z]+", lambda ele: " " + ele[0] + " ", data['userData']['highestRating']['time'])
  highestRatingTime = re.sub(r'(?<=,)', r' ', highestRatingTime)
  ratings_desc = (f"Their rating: {data['userData']['rating']}\n"
                  f"Highest rating: {data['userData']['highestRating']['rating']} achieved on {highestRatingTime}\n")
  chessEmbed.add_field(name="USER RATINGS", value=ratings_desc, inline=False)

  total_games = int(data['chartData']['black']['games']) + int(data['chartData']['white']['games'])
  all_games_desc = (f"{total_games} - Total games\n"
                    f"{data['chartData']['all']['wins']} - Wins\n"
                    f"{data['chartData']['all']['losses']} - Losses\n"
                    f"{data['chartData']['all']['draws']} - Draws")
  chessEmbed.add_field(name="ALL GAMES", value=all_games_desc, inline=True)

  white_games_desc = (f"{data['chartData']['white']['games']} - Total games\n"
                      f"{data['chartData']['white']['wins']} - Wins\n"
                      f"{data['chartData']['white']['losses']} - Losses\n"
                      f"{data['chartData']['white']['draws']} - Draws")
  chessEmbed.add_field(name="WHITE GAMES", value=white_games_desc, inline=True) 

  black_games_desc = (f"{data['chartData']['black']['games']} - Total games\n"
                      f"{data['chartData']['black']['wins']} - Wins\n"
                      f"{data['chartData']['black']['losses']} - Losses\n"
                      f"{data['chartData']['black']['draws']} - Draws")           
  chessEmbed.add_field(name="BLACK GAMES", value=black_games_desc, inline=True)   

  friends_opponents_desc = (f"Leaderboard Rank: {data['userData']['leaderboardRank']}\n"
                            f"Friend count: {data['userData']['friendCount']}\n"
                            f"Rank among their friends: {data['userData']['friendRank']}\n"
                            f"Percentile: {data['userData']['percentile']}%\n"
                            f"Highest win streak: {data['userData']['winningStreak']}\n"
                            f"Best win: {data['userData']['bestWin']['rating']} against {data['userData']['bestWin']['player']}") 
  chessEmbed.add_field(name="FRIEND/OPPONENT STATS", value=friends_opponents_desc, inline=False)
  await ctx.send(embed=chessEmbed)

keep_alive()
client.run(os.getenv('TOKEN'))
