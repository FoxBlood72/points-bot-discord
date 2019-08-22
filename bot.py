import discord
import database
import json
import re
from discord.ext import commands
from database import *

bot = commands.Bot(command_prefix="!")


config_file = open("config.json")
config = json.load(config_file)

bot.remove_command("help")

@bot.event
async def on_ready():
    print("Bot is running and ready to use!")
    

@bot.event
async def on_reaction_add(reaction, user):
    if(check_leaderboard(reaction.message.id, user.id)):
        if(reaction.emoji == u"\u25B6"):
            page, last_user_count = get_leaderboard_page(reaction.message.id, user.id)
            if(last_user_count < page * 10):
                return
            rows = get_users(page+1)
            embed = discord.Embed(title = "Leaderboard", color=0x8150bc)
            for row in rows:
                if(row[1] != None and row[2] != None):
                    user_name = bot.get_user(int(row[1]))
                    user_name = "#" + str(last_user_count) + " | " + str(user_name)
                    embed.add_field(name = user_name, value = '{:,}'.format(row[2]), inline=False)
                    last_user_count += 1
            
            update_leaderboard(page + 1, last_user_count, reaction.message.id)
            await reaction.message.edit(embed = embed)
            await reaction.message.clear_reactions()
            await reaction.message.add_reaction(u"\u25C0")
            if(last_user_count > (page+1) * 10):
                await reaction.message.add_reaction(u"\u25B6")
        
        if(reaction.emoji == u"\u25C0"):
            page, last_user_count = get_leaderboard_page(reaction.message.id, user.id)
            if(page == 1):
                return
            rows = get_users(page-1)
            embed = discord.Embed(title = "Leaderboard", color=0x8150bc)
            if(last_user_count <= page * 10):
                last_user_count -= 10 + (last_user_count-1) % 10
            else:
                last_user_count -= 20
            
            
            for row in rows:
                if(row[1] != None and row[2] != None):
                    user_name = bot.get_user(int(row[1]))
                    user_name = "#" + str(last_user_count) + " | " + str(user_name)
                    embed.add_field(name = user_name, value = '{:,}'.format(row[2]), inline=False)
                    last_user_count += 1
            
            
            update_leaderboard(page - 1, last_user_count, reaction.message.id)
            await reaction.message.edit(embed = embed)
            await reaction.message.clear_reactions()
            if(page - 1 > 1):
                await reaction.message.add_reaction(u"\u25C0")
            await reaction.message.add_reaction(u"\u25B6")
    
    
    if(reaction.emoji == u"\U0001F44D"):
        roles = user.roles
        
        permission = False
        
        for role in roles:
            if(role.name == "Manager" or role.permissions.administrator):
                permission = True
                
        if(permission and check_requests(reaction.message.id) and not user.bot):
            users, points = get_users_requests(reaction.message.id)
            split_users = users.split()
            for user_id in split_users:
                add_points(user_id, points)
            
            update_requests(reaction.message.id, 1)
            await reaction.message.add_reaction('\U00002705')
            
    
        
@bot.command(pass_context = True)
async def points(ctx, command = None, username = None, point = None):
    #print(username)
    if(command == None or point == None or username == None):
        if(command == None and point == None and username == None):
            points = get_user_point(ctx.message.author.id)
            await ctx.send("You have " + str(points) + " points")
            return
        else:
            await ctx.send("Invalid command, please check the documentation: \n!points [add/remove] <username> <points>")
            return
            
    roles = ctx.message.author.roles
    permission = False
    
    for role in roles:
        if(role.name == "Manager" or role.permissions.administrator):
            permission = True
            
    if(not permission):
        await request_points(ctx)
        #await ctx.send("No permission")
        return

    if(command.lower() == "add"):
        if(point.isdigit()):
            username_id = username[2:]
            username_id = username_id[:-1]
            username_id = username_id.replace("!","")
            if(username_id.isdigit()):
                add_points(username_id, point)
            else:
                from_server = ctx.guild
                user = from_server.get_member_named(username)
                if(user == None):
                    await ctx.send("Invalid user")
                    return
                else:
                    add_points(user.id, point)
            await ctx.send("Points added!")
        else:
            await request_points()
    else:
        if(command.lower() == "remove"):
            if(point.isdigit()):
                username_id = username[2:]
                username_id = username_id[:-1]
                username_id = username_id.replace("!","")
                if(username_id.isdigit()):
                    remove_points(username_id, point)
                else:
                    from_server = ctx.guild
                    user = from_server.get_member_named(username)
                    if(user == None):
                        await ctx.send("Invalid user")
                        return
                    else:
                        remove_points(user.id,point)
                await ctx.send("Points removed!")
            else:
                await ctx.send("Invalid points number!")
        else:
            await ctx.send("Invalid command, please check the documentation: \n!points [add/remove] <username> <points>")


@bot.command(pass_context = True)
async def help(ctx):
    embed = discord.Embed(title = "Help command list", color=0x8150bc)
    embed.add_field(name = "!leaderboard", value = config["leaderboard_help"], inline = False)
    embed.add_field(name = "!points", value = config["points_help"], inline = False)
    embed.add_field(name = "!help", value = config["help_help"], inline = False)
    await ctx.send(embed = embed)


@bot.command(pass_context = True)
async def leaderboard(ctx):
    rows = get_users(1)
    embed = discord.Embed(title = "Leaderboard", color=0x8150bc)
    count = 1
    for row in rows:
        if(row[1] != None and row[2] != None):
            user = bot.get_user(int(row[1]))
            user = "#" + str(count) + " | " + str(user)
            embed.add_field(name = user, value = '{:,}'.format(row[2]), inline=False)
            count += 1
            
    msg_sent = await ctx.send(embed=embed)
    add_leaderboard(ctx.message.author.id, msg_sent.id, count)
    if(count == 11):
        await msg_sent.add_reaction(u"\u25B6")
           


@bot.event
async def on_message_edit(before, after):
    if(check_requests(after.id)):
        update_requests(after.id, -1)

@bot.event
async def on_command_error(ctx, error):
    try:
        await request_points(ctx)
    except Exception as e:
        print("Some shit happened: " + str(error))
        print("Error from try catch : " + str(e))
    
    
@bot.command(pass_context=True)
async def reset(ctx):
    permission = False
    roles = ctx.message.author.roles
    for role in roles:
        if(role.permissions.administrator):
            permission = True
            
    if(permission):
        await reset_database()
        await ctx.send("Database was rest!")
    else:
        await ctx.send("No permision!")
    
    
async def format_user(user_name):
    for i in range(len(user_name)):
        if(user_name[i] != ' '):
            break
        else:
            user_name = user_name[1:]
            
    for i in user_name[::-1]:
        if(i != " "):
            break
        else:
            user_name = user_name[:-1]    
    return user_name
    
async def request_points(ctx):
    #print("here it go")
    message_sent = ctx.message.content
    if(message_sent[:12] == "!points add "):
        message_sent = message_sent[12:]
        split_message = re.split('\s+',message_sent)
        users = ''
        #print(split_message)
        for i in range(0,len(split_message) - 1):
            users += split_message[i]
            users += ' '
            
        users = users[:-1]
        #print(users)
        split_users = users.split(',')
        saved_users = ''
        #print(split_users)
        for user in split_users:
            user = await format_user(user)
            #print(user)
            if(user[:1] == '"' and user[-1:] == '"'):
                user = user[1:]
                user = user[:-1]
                #print(user)
                user_id = ctx.guild.get_member_named(user)
                if(user_id == None):
                    await ctx.send("The following user does not exist: " + str(user) + "\nPlease do not use white spaces between users and commas")
                    return
                    
                saved_users += str(user_id.id)
                saved_users += ' '
            elif(user[:1] == "<"):
                user = user.strip()
                user = user[2:]
                user = user[:-1]
                user = user.replace("!","")
                if(user.isdigit()):
                    found = bot.get_user(int(user))
                else:
                    await ctx.send("The following user does not exist : " + str(user) + "\nPlease use comma between users!")
                    return
                    
                if(found == None):
                    await ctx.send("The following user does not exist : " + str(user) + "\nPlease use comma between users!")
                    return
                
                saved_users += str(user)
                saved_users += ' '
            elif(user[-1:] == ">"):
                user = user.strip()
                user = user[2:]
                user = user[:-1]
                user = user.replace("!","")
                if(user.isdigit()):
                    found = bot.get_user(int(user))
                else:
                    await ctx.send("The following user does not exist : " + str(user) + "\nPlease use comma between users!")
                    return
                
                found = bot.get_user(user)
                if(found == None):
                    await ctx.send("The following user does not exist : " + str(user) + "\nPlease use comma between users!")
                    return
                saved_users += str(user)
                saved_users += ' '
            else:
                #print("Ja")
                user_id = ctx.guild.get_member_named(user)
                if(user_id == None):
                    await ctx.send("The following user does not exist : " + str(user))
                    return
                saved_users += str(user_id.id)
                saved_users += ' '
        
        insert_points_requests(ctx.message.id, saved_users, split_message[len(split_message) - 1], 0, ctx.message.author.id)
        
        roles = ctx.message.author.roles
        permission = False
    
        for role in roles:
            if(role.name == "Manager" or role.permissions.administrator):
                permission = True
        
        if(not permission):
            await ctx.message.add_reaction(u"\U0001F44D")
        else:
            users_req = saved_users.split()
            for user in users_req:
                add_points(user, split_message[len(split_message) - 1])
            await ctx.send("Points added")
    
    
bot.run(config["bot_token"])