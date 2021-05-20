import os
import discord
from discord.ext import commands
from algorithm import main
import re
from keep_alive import keep_alive
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

client = commands.Bot(command_prefix='$')
client.remove_command('help')

def read_points(message):
  f = open('data.txt', 'w')  
  vals = message.content.split("\n")
  for item in vals:
    item.strip()
    point = re.split('\s+', item)
    try:       
      x = int(point[0])
      y = int(point[1])
      f.write(f'{x} {y}\n')
    except:
      pass
  f.close()


@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game('$help'))
  print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  # Can't be a command because I want the option to add ``` right after the $plot with no space
  if msg.startswith("$plot"):
    read_points(message)
    main() # executes convex hull algorithm
    await message.channel.send(file=discord.File('out.png'))
  
  await client.process_commands(message)

@client.command(aliases=['rules'])
async def help(ctx):
  myEmbed = discord.Embed(title='CONVEX HULL', description = '', color=0xFF0000)
  myEmbed.set_author(name='Help')
  desc1 = ("Type '$plot' followed by the triple tilde and begin typing points on"
            " each new line and finish it with another triple tilde on its own line.")
  myEmbed.add_field(name="Method 1", value=desc1, inline=True)
  desc2 = ("Type '$plot' followed by 'shift + enter'"
           " which moves to a new line and begin typing in points as normal.")
  myEmbed.add_field(name="Method 2", value=desc2, inline=True)
  desc3 = ("Type '$search' followed by your google images search. You can type a number (1-20) "
          "after $search to indicate the index number of your google image search "
          "if you don't simply want the first image. The index is based off of Chromium's "
          "Google Images and not necessarily your desired browser.")
  myEmbed.add_field(name='GOOGLE IMAGES SEARCH', value=desc3, inline=False)
  await ctx.send(embed=myEmbed)

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
  await ctx.send(file=discord.File('search.png'))

keep_alive()
client.run(os.getenv('TOKEN'))
