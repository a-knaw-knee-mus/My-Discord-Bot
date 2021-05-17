import os
import discord
from algorithm import main
from keep_alive import keep_alive
import re

client = discord.Client()

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

  if msg.startswith("$help"):
    output = (
      "```Type '$plot' followed by the triple tilde and begin typing points on"
      " each new line and finish it with another triple tilde on its own line.\n\n"
      "You can also type '$plot' followed by 'shift + enter'"
      " which moves to a new line and begin typing in points as normal.```"
    )
    await message.channel.send(output)

  if msg.startswith("$plot"):
    read_points(message)
    main() # executes convex hull algorithm
    await message.channel.send(file=discord.File('out.png'))

keep_alive()
client.run(os.getenv('TOKEN'))
