import discord

from discord import (
    Message,
    Member,
    TextChannel,
    RawReactionActionEvent,
    RawMemberRemoveEvent,
    Reaction,
    Embed,
    Guild,
    VoiceState,
    VoiceChannel
)

import traceback
import argparse

from datetime import datetime as dt

from random import shuffle, choice

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
        "💊": 1000435736690040852, # healer
        "🗡️": 1000435920044044339, # dps role
    },
    # Fleurino's message about content interest
    988482120857026650: {
        "🥇": 1024326266763100253, # mutations
        "🐉": 1292131496483881043, # hive
        "🪱": 1180466569361502238, # wurm
        "🤑": 1084092935647264818, # chestrun
        "⚔️": 1092217764678221897, # pvp
    },
    # Fleurino's message about crafting capabilities
    1000434698201346068: {
        "🗡️": 1046908760368623788, # Weaponsmith
        "👕": 1046909094440734771, # Armorer
        "⛏️": 1046909175034294354, # Engineer
        "💍": 1046915774310264832, # Jewelcrafter
        "✨": 1046909301500948561, # Arcanist
        "🪑": 1046909240800981132, # Furnisher
        "🧑‍🍳": 1046909379783438399, # Chef
    },
}

uncoolNames = [
    "Echo 📢",
    "Foxtrot 📢",
    "Golf 📢",
    "Hotel 📢",
    "India 📢",
    "Juliet 📢",
    "Kilo 📢",
]

coolNames = [
    "Amok 💣",
    "Beer 🍻",
    "Chaos 🦖",
    "Devils 😈",
]

from discord.ui import View, button

from asyncio import sleep

DICE_ROLLERS = []
ROLL_SLEEP_SECONDS = 5

temp_channels: list[VoiceChannel] = []

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

    async def on_message(self, message: Message):
        if not self.intents.message_content:
            print("messages are not allowed")
            return
                 
        def roll_a_dice(count, max):
            ans = f"Your roll{'' if count < 2 else 's'}:"
            for x in range(count):
                ans+=f"\nRoll {x+1}: {random.randint(1, max)}"
            return ans
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

    async def on_member_join(self, member):
        # intent.members is required
        ...

    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        if not self.intents.voice_states: print("voice state is not allowed")
        
        if after.channel:
            if after.channel.id == 1089216373542109265: 
                def check_names(temp_names: list):
                    for vc in temp_channels:
                        if vc.name[6:] in temp_names:
                            temp_names.remove(vc.name[6:])

                initialChannel = after.channel
                guild = initialChannel.guild

                temp_names = coolNames[:]
                check_names(temp_names)
                
                if len(temp_names) == 0:
                    temp_names += uncoolNames[:]
                check_names(temp_names)

                try:
                    # print(initialChannel.category)
                    VC = await guild.create_voice_channel(
                        name = "Party " + choice(temp_names), 
                        reason = None,
                        category=initialChannel.category,
                        position=initialChannel.position + 1
                    )

                    await member.move_to(
                        VC
                    )

                    temp_channels.append(VC)
                except IndexError as e:
                    print(e)
                    member.move_to(channel=guild.get_channel(962652775395774477))

        if before.channel in temp_channels:
            await sleep(2)

            if len(before.channel.members) == 0:
                await before.channel.delete()
                try:
                    temp_channels.remove(before.channel)
                except ValueError as e:
                    print(e)

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
        print(f"`on_raw_member_remove` was called at {dt.now()} with arg: {payload.user}")
        log.info(f"`on_raw_member_remove` was called at {dt.now()} with arg: {payload.user}")
        # intent.members is required
        if not self.intents.members:
            print("Members processing is not allowed")
            return

        channel: TextChannel = self.get_channel(
            975376546376335391 # 'members' channel
        )

        votingsChannel: TextChannel = self.get_channel(VOTINGS_CHANNEL)
        for voting in VOTINGS:
            try:
                message: Message = await votingsChannel.fetch_message(voting)
                for reaction in message.reactions:
                    reaction: Reaction
                    await reaction.remove(payload.user)
            except discord.NotFound: 
                await channel.send(f"An error occurred when deleting user {payload.user.display_name} roles. Message {voting} was not found in #{votingsChannel.name}") 
            except discord.Forbidden: 
                await channel.send(f"An error occurred when deleting user {payload.user.display_name} roles. The bot is not allowed to work with {voting} in #{votingsChannel.name}") 
            except discord.HTTPException as e: 
                await channel.send(f"An error occurred when deleting user {payload.user.display_name} roles. Discord API returned an error {e.status} — {e.text}") 

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
        error_message = f"{event=}\n{args=}\n{kwargs=}\n--TRACEBACK--\n{traceback.format_exc()}\n\n"
        log.error(error_message)
        channel: TextChannel = self.get_channel(
            1089216328725962853 # 'test-text' channel
        )

        await channel.send(f"\nUnexpected error: {error_message}")

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True
    intents.reactions = True
    intents.message_content = True
    intents.voice_states = True

    client = Client(intents=intents)
    client.run(SETTINGS["TOKEN"])
