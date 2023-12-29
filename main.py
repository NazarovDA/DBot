import discord

from discord import (
    Message,
    Member,
    TextChannel,
    RawReactionActionEvent,
    RawMemberRemoveEvent,
    Reaction,
    Embed,
    Guild
)

import traceback

from random import shuffle

# !-------- Logging --------!
import logging as log
import re
import random
log.basicConfig(filename="discord_bot.log", level=log.INFO)

#   if not discord.version_info == VersionInfo(major=2, minor=0, micro=1, releaselevel='final', serial=0):
#       log.critical("discord.py version is not the one the program was written for. it is recommended to install Version 2.0.1: https://github.com/Rapptz/discord.py")

try:
    with open("settings.json", "r") as SETTINGS_FILE:
        import json
        SETTINGS = json.load(SETTINGS_FILE)
except:
    try:
        import settings as SETTINGS_FILE
        SETTINGS = SETTINGS_FILE.SETTINGS
    except: ...


import json

try:
    with open("tournament.json", "r") as FILE:
        TOURNAMENT_INFO = json.load(FILE)
except FileNotFoundError:
    TOURNAMENT_INFO = {
        "members": []
    }

DICE_ROLL_REGEX = re.compile("\!roll \d{1,2}[d]\d*")

TOURNAMENT_REGISTER_MESSAGE_ID: int = 1113922644199354488
TOURNAMENT_CHANNEL_ID               = 1089216328725962853
VOTINGS_CHANNEL                     = 974968723221917696
VOTINGS = {
    # Fleurino's message about main builds
    983857007343857705: {
        "🛡️": 1000435488664072193, # tank
        "🗡️": 1000435920044044339, # dps role
        "💊": 1000435736690040852, # healer
    },
    # Fleurino's message about PvP/PvE
    988482120857026650: {
        "😇": None, # i do not know what to do
        "⚔️": None, # i do not know what to do
        "😈": None, # i do not know what to do
    },
    # Fleurino's message about av. gear score
    1000434698201346068: {
        "🥇": 1024326266763100253, # expeditioners role (merged mutators in)
        "🏆": 1180466569361502238, # raiders role
        "👑": 1084092935647264818, # chestrunner role
        "⚔️": 1092217764678221897, # pvp role
    },
    1046909706486161548: {
        "🗡️":  1046908760368623788, # Weaponsmith
        "👕": 1046909094440734771, # Armorer
        "⛏️": 1046909175034294354, # Engineer
        "💍": 1046915774310264832, # Jewelcrafter
        "✨": 1046909301500948561, # Arcanist
        "🪑": 1046909240800981132, # Furnisher
        "🧑‍🍳": 1046909379783438399, # Chef
    }
}

from asyncio import sleep

DICE_ROLLERS = []
ROLL_SLEEP_SECONDS = 5
from discord.ui import View, button
class RollADiceView(View):
    @button(label="Roll some dice!", style=discord.ButtonStyle.success, emoji="😎")
    async def button_callback(self, interaction: discord.Interaction, button):
        DICE_ROLLERS.append(interaction.user.nick)
        
        if len(DICE_ROLLERS) < 2:
            await sleep(ROLL_SLEEP_SECONDS)

            m = ""
            for roll in DICE_ROLLERS:
                m += f"{roll} rolled {random.randint(1, 8)}\n"

            await interaction.channel.send(m)
            button.disabled = True
            
            DICE_ROLLERS.clear()
    


def create_teams():
    shuffle(TOURNAMENT_INFO["members"])

    players: list[int] = TOURNAMENT_INFO["members"]

    l = len(players)

    TOURNAMENT_INFO["teams"] = [[players[x], players[x+1]] for x in range(0, l if l % 2 == 0 else l-1, 2)]



def save_tour_data():
    with open("tournament.json", "w") as FILE:
        json.dump(obj=TOURNAMENT_INFO, fp=FILE)


class Client(discord.Client):
    async def on_ready(self):
        print(f'logged as {self.user}')

    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        # intents.reactions is required
        if not self.intents.reactions:
            print("Reaction processing is not allowed")
            return

        if payload.channel_id == VOTINGS_CHANNEL: # demographics channel id
            member: Member = payload.member
            role = VOTINGS[payload.message_id][payload.emoji.name] # gather role from _VOTINGS

            if role == None: return

            await member.add_roles(
                self.guilds[0].get_role(role),
                reason=f"Answered to voting {payload.message_id}"
            )

        if payload.message_id == TOURNAMENT_REGISTER_MESSAGE_ID:
            member: Member = payload.member

            if member.id not in TOURNAMENT_INFO['members']:
                TOURNAMENT_INFO["members"].append(member.id)
                create_teams()
                save_tour_data()



    async def on_message(self, message: Message):
        if not self.intents.message_content:
            print("messages are not allowed")
            return
        def prepare_team(team: list[int]):
            return f"player 1: {self.guilds[0].get_member(team[0]).display_name}, player 2: {self.guilds[0].get_member(team[1]).display_name}"
                 
        def roll_a_dice(count, max):
            ans = f"Your roll{'' if count < 2 else 's'}:"
            for x in range(count):
                ans+=f"\nRoll {x+1}: {random.randint(1, max)}"
            return ans

        def prepare_team(team: list[int]):
            return f"player 1: {self.guilds[0].get_member(team[0]).display_name}, player 2: {self.guilds[0].get_member(team[1]).name}"
        #print(message.content)

        if message.content.startswith("!"):
            if DICE_ROLL_REGEX.fullmatch(message.content):
                await message.reply(roll_a_dice(*list(map(lambda x: int(x), message.content.split(" ")[1].split("d")))))
            # if message.content.startswith("!info"):
                # await message.reply(
                    # f"You are {message.author.display_name} \ {message.author.name}"
                # )
            if message.content.startswith("!race"):
                await message.channel.send(view=RollADiceView())
            if message.channel.id == TOURNAMENT_CHANNEL_ID:
                if message.content.startswith("!teams"):
                    await message.reply(
                        "".join("Teams are:\n" + f"Team {i + 1}: {prepare_team(team)}" for i, team in enumerate(TOURNAMENT_INFO['teams']))
                    )



    async def on_member_join(self, member):
        # intent.members is required
        ...

    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        if not self.intents.reactions:
            print("Reaction processing is not allowed")
            return

        if payload.message_id in list(VOTINGS.keys()):
            member: Member = self.guilds[0].get_member(
                payload.user_id
            )

            if member == None: return

            await member.remove_roles(
                self.guilds[0].get_role(
                    VOTINGS[payload.message_id][payload.emoji.name]
                )
            )

    async def on_raw_member_remove(self, payload: RawMemberRemoveEvent):
        # intent.members is required
        if not self.intents.members:
            print("Members processing is not allowed")
            return

        channel: TextChannel = self.get_channel(
            975376546376335391 # 'members' channel
        )

        votingsChannel: TextChannel = self.get_channel(VOTINGS_CHANNEL)
        for voting in VOTINGS:
            message: Message = await votingsChannel.fetch_message(voting)
            for reaction in message.reactions:
                reaction: Reaction
                await reaction.remove(payload.user)

        roles = [
                self.guilds[0].get_role(role).name
                for role
                in [role.id for role in payload.user.roles] if role in list(VOTINGS[983857007343857705].values()) + list(VOTINGS[1000434698201346068].values())
            ]

        await channel.send(
            f"**{payload.user.display_name}**{f' ({payload.user.name})' if payload.user.name != payload.user.display_name else ''} has left." +\
            f"{' They were ' + ', '.join(roles) + '.' if roles.__len__() > 0 else ''}"
        )

    async def on_error(self, event, *args, **kwargs):
        log.error(f"{event=}\n{args=}\n{kwargs=}\n--TRACEBACK--\n{traceback.format_exc()}\n\n")

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True
    intents.reactions = True
    intents.message_content = True

    client = Client(intents=intents)
    client.run(SETTINGS["TOKEN"])
