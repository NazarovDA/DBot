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

# !-------- Logging --------!
import logging as log
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


VOTINGS_CHANNEL = 974968723221917696
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
        "🐣": 1024326266763100253, # expeditioner role
        "🐓": 1001095283372998716, # mutator role
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
            content = (f"**{payload.user.nick}** ({payload.user.name}#{payload.user.discriminator})" if payload.user.nick else f"**{payload.user.name}#{payload.user.discriminator}**") + " has left." + f"{' They were ' + ', '.join(roles) + '.' if roles.__len__() > 0 else ''}"
        )

    async def on_error(self, event, *args, **kwargs): 
        log.error(f"{event=}\n{args=}\n{kwargs=}\n--TRACEBACK--\n{traceback.format_exc()}\n\n")

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True
    intents.reactions = True
    # intents.messages = True

    client = Client(intents=intents)
    client.run(SETTINGS["TOKEN"])
