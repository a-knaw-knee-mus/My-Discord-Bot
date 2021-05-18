import os
import discord
from discord.ext import commands
from algorithm import main
from keep_alive import keep_alive
import re

client = commands.Bot(command_prefix='$')
client.remove_command('help')

def read_points(message):
  f = open('data.txt', 'w')  
  vals = message.content.split("\n")
  for item in vals:
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
  print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  # Can't be a command since I want the user to have to option to type '$plot```' without a space between the two
  if msg.startswith("$plot"):
    read_points(message)
    main() # executes convex hull algorithm
    await message.channel.send(file=discord.File('out.png'))
    
  await client.process_commands(message)

@client.command()
async def help(ctx):
  myEmbed = discord.Embed(title = 'Help', description = '', color=0xfcba03)
  desc1 = ("Type '$plot' followed by the triple tilde and begin typing points on"
            " each new line and finish it with another triple tilde on its own line.")
  myEmbed.add_field(name="Method 1", value=desc1, inline=False)
  desc2 = ("Type '$plot' followed by 'shift + enter'"
          " which moves to a new line and begin typing in points as normal.")
  myEmbed.add_field(name="Method 2", value=desc2, inline=False)
  await ctx.send(embed=myEmbed)  
    
keep_alive()
client.run(os.getenv('TOKEN'))
