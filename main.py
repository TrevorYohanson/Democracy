import discord
from discord.ext import commands
import asyncio
from config import TOKEN

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def hello(ctx):
    await ctx.send("Hello, I am a robot")

@bot.command(aliases=["promotionvote"])
async def promote(ctx, target: discord.Member):
    role_hierarchy = ["Warfighter", "Operator", "Team Leader"]

    if any(role.name in role_hierarchy for role in ctx.author.roles):
        current_role_index = next((i for i, role in enumerate(role_hierarchy) if role in [r.name for r in ctx.author.roles]), None)

        if current_role_index is not None and current_role_index < len(role_hierarchy) - 1:
            target_role = discord.utils.get(ctx.guild.roles, name=role_hierarchy[current_role_index + 1])

            initiator = ctx.author

            vote_message = await ctx.send(f"A promotion vote has been started by {initiator.mention} to promote {target.mention} to {target_role.name}\n\nPlease use 👍 to vote to promote {target.mention} to {target_role.name} ")

            
            await asyncio.sleep(3600)

            
            vote_message = await ctx.channel.fetch_message(vote_message.id)
            reactions = vote_message.reactions

            
            yes_votes = sum(reaction.count for reaction in reactions if str(reaction.emoji) == '👍')

            
            if yes_votes > (len(ctx.channel.members) // 2):
                await ctx.author.add_roles(target_role)
                await ctx.send(f"The promotion vote for {target.mention} was successful! {ctx.author.mention} has been promoted to {target_role.name}.")
            else:
                await ctx.send(f"The promotion vote for {target.mention} did not pass.\n\n Take a bit to try to understand why the promotion was denied. Please take some time to improve yourself and come back stronger")
        else:
            await ctx.send(f"{target.mention}, I am sorry but you can not be promoted to {target_role.name}. If you think this is an error, please message Vayx.")
    else:
        await ctx.send(f"{target.mention}, I don't think that you can be promoted from your rank. Please contact Vayx if you think this is a mistake.")

@bot.command(aliases=["demotionvote"])
async def demote(ctx, target: discord.Member):
    initiator = ctx.author
    await ctx.send(f"A demotion vote has been started by {initiator.mention} to promote {target.mention}")
