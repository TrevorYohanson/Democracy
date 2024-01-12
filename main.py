import discord
from discord.ext import commands
import asyncio
from Config import TOKEN

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command(name="votestop", aliases=["stopvote"])
@commands.check_any(commands.has_any_role("Founder", "Administrator"))
async def votestop(ctx):
    if any(role.name in ["Founder", "Administrator"] for role in ctx.author.roles):
        initiator = ctx.author
        await ctx.send(f"The promotion vote was halted by {initiator.mention}")
        print('Vote stopped by !VoteStop')
        await tally_votes(ctx, initiator=initiator)
    else:
        await ctx.send("You lack the necessary roles to stop the promotion vote.")
        print(f'{ctx.author} attempted to use !VoteStop')


@bot.command(name="promotionvote", aliases=["promote", "votepromote"])
@commands.check(lambda ctx: any(role.name in ["Warfighter", "Operator", "Team Leader"] for role in ctx.author.roles))
async def promote(ctx, target: discord.Member):
    role_hierarchy = ["Warfighter", "Operator", "Team Leader"]

    current_role_index = max((role_hierarchy.index(role.name) for role in ctx.author.roles if role.name in role_hierarchy), default=None)

    if current_role_index is not None and current_role_index < len(role_hierarchy) - 1:
        target_role = discord.utils.get(ctx.guild.roles, name=role_hierarchy[current_role_index + 1])

        initiator = ctx.author

        vote_message = await ctx.send(
            f"{initiator.mention} initiated a promotion vote for {target.mention} to {target_role.name}\n\nVote with 👍 or 👎 to support or oppose.")

        await vote_message.add_reaction('👍')
        await vote_message.add_reaction('👎')

        await asyncio.sleep(3600)

        vote_message = await ctx.channel.fetch_message(vote_message.id)
        
        await tally_votes(ctx, target, initiator)
    else:
        await ctx.send(f"{target.mention}, I apologize, but further promotion is not possible for you. If you believe this is a mistake, please contact Vayx.")


async def tally_votes(ctx, target=None, initiator=None):
    try:
        vote_message = await ctx.channel.fetch_message(ctx.message.id)
    except discord.NotFound:
        await ctx.send("Error: Unable to find the vote message.")
        return

    reactions = [reaction for reaction in vote_message.reactions if reaction.emoji in ['👍', '👎']]
    initiator_vote = '👍'
    users_except_initiator = set()

    for reaction in reactions:
        if reaction.emoji == '👍':
            users_except_initiator.update(await reaction.users().flatten())
        elif reaction.emoji == '👎' and initiator in await reaction.users().flatten():
            initiator_vote = '👎'

    yes_votes = len(users_except_initiator) if initiator_vote == '👍' else len(users_except_initiator) - 1
    no_votes = len(reactions) - yes_votes

    await ctx.send(f"Vote Tally:\n👍 Yes Votes: {yes_votes}\n👎 No Votes: {no_votes}")

    if target and yes_votes > (len(ctx.channel.members) // 2):
        promoted_role = discord.utils.get(ctx.guild.roles, name="Promoted")
        if promoted_role:
            await target.add_roles(promoted_role)
            await ctx.send(f"The promotion vote passed! {target.mention} has been promoted and received the {promoted_role.mention} role.")
        else:
            await ctx.send("Error: Could not find the 'Promoted' role.")
    elif target:
        await ctx.send(f"The promotion vote did not pass. {target.mention} will not be promoted.")


@bot.command(aliases=["demotionvote"])
async def demote(ctx, target: discord.Member):
    initiator = ctx.author
    await ctx.send(f"{initiator.mention} initiated a demotion vote for {target.mention}")

bot.run(TOKEN)
