import discord

def set_info_embed_from_list(column_headings, data):
    embedded_message = discord.Embed(
                    title=data[0],
                    description=f"Embed containing info about: \n **{data[0]}**",
                    color=discord.Color.dark_red())
    
    for i in range(0, len(column_headings)):
        embedded_message.add_field(name=column_headings[i], value=data[i], inline=False)
    
    return embedded_message

def set_info_embed_from_dictionary(key, value):
    embedded_message = discord.Embed(color=discord.Color.dark_green())
    
    embedded_message.add_field(name=f"**{key}**", value=value, inline=False)
    
    return embedded_message
    