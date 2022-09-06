import discord 

from discord import (
    Message,
    Member, 
    VoiceState, 
    Guild, 
    VoiceChannel, 
    TextChannel, 
    Role,
    VoiceClient,
    RawReactionActionEvent,
    RawReactionClearEvent,
    Attachment,
    RawMemberRemoveEvent,
    Emoji,
    Reaction,
    VersionInfo
)

# !-------- Logging --------!
import logging as log
log.basicConfig(filename="discord_bot.log", level=log.INFO)

if not discord.version_info == VersionInfo(major=2, minor=0, micro=1, releaselevel='final', serial=0):
    log.critical("discord.py version is not the one the program was written for. it is recommended to install Version 2.0.1: https://github.com/Rapptz/discord.py")

with open("settings.json", "r") as SETTINGS_FILE:
    try:
        import json
        SETTINGS = json.load(SETTINGS_FILE)
    except:
        import settings as SETTINGS_FILE
        SETTINGS = SETTINGS_FILE.SETTINGS


__VOTINGS_CHANNEL = 974968723221917696
__VOTINGS = {
    # Fleurino's message about main builds
    983857007343857705: {
        "🛡️": 1000435488664072193, # tank
        "🪓": 1000435920044044339, # dps role
        "💊": 1000435736690040852, # healer
        "🪄": 1000435920044044339, # dps role
        "🏹": 1000435920044044339, # dps role
    },
    # Fleurino's message about PvP/PvE
    988482120857026650: {
        "⚔️": None, # i do not know what to do
        "😇": None, # i do not know what to do
    },
    # Fleurino's message about av. gear score
    1000434698201346068: {
        "🐣": None, # i do not know what to do
        "🐤": None, # i do not know what to do
        "🐦": 1001095283372998716, # mutator role
    }
}

class Client(discord.Client):
    async def on_ready(self):
        print(f'logged as {self.user}')

    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        # intents.reactions is required
        if not self.intents.reactions(): 
            print("Reaction processing is not allowed")
            return

        if payload.channel_id == __VOTINGS_CHANNEL: # demographics channel id 
            member: Member = payload.member
            try:
                role = __VOTINGS[payload.message_id][payload.emoji.name] # gather role from _VOTINGS

                if role == None: return

                await member.add_roles(
                    roles=[
                        role
                    ],
                    reason=f"Answered to voting {payload.message_id}"
                )
            except Exception as e: print(e)

    async def on_member_join(self, member):
        # intent.members is required
        ... 

    async def on_raw_member_remove(self, payload: RawMemberRemoveEvent): 
        # intent.members is required
        if not self.intents.members(): 
            print("Members processing is not allowed")
            return

        channel: TextChannel = self.get_channel(
            963514720176967742 # 'welcome' channel
        )
        
        votingsChannel = await self.fetch_channel(__VOTINGS_CHANNEL)
        for voting in __VOTINGS:
            message: Message = await votingsChannel.fetch_message(voting)
            for reaction in message.reactions:
                reaction: Reaction
                await reaction.remove(payload.user)


        await channel.send(
            content=f"{payload.user.nick}({payload.user.name}) has left."
        )

    async def on_error(self, event, *args, **kwargs): log.error(f"{event}----\n{args}----\n{kwargs}")

if __name__ == "__main__":
    intents = discord.Intents.default()
    # intents.members = True
    intents.reactions = True
    # intents.messages = True

    client = Client(intents=intents)
    client.run(SETTINGS["TOKEN"])