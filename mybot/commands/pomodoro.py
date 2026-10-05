"""Per-channel pomodoro timer: /pomodoro_start, _pause, _resume, _cancel, _status."""
import asyncio
from datetime import datetime, timedelta

import discord
from discord import app_commands

#pomodoro state
_pomo: dict[int,dict] = {} # channel_id -> {"who": int, "end": datetime, "paused": bool, "remaining": int, "task": asyncio.Task|None}

def _fmt(secs:int) -> str: #formats seconds as xm ys
    secs = max(0, int(secs))
    m, s = divmod(secs,60) #returns a tuple of the time
    return f"{m}m {s}s" #f string for time taken

#computes seconds left in the current timer
def _remaining(state: dict) -> int:
    if state.get("paused"): #if paused, trust the state["remaining"]
        return int(state.get("remaining", 0))
    #or else subtract now from the total seconds
    return max(0, int((state["end"] - datetime.utcnow()).total_seconds()))

#runs the ticking logic for one channel
async def _pomo_loop(channel: discord.abc.Messageable, channel_id: int):
    try: #pairs with except cancelled error at the bottom to stop the loop cleanly
        while True:
            state = _pomo.get(channel_id)
            if not state:
                return
            if state.get("paused"):
                await asyncio.sleep(1.0) #if paused, dont count down and sleeps for one second and runs the loop again
                continue
            secs = _remaining(state) #calculate seconds left
            if secs <= 0:
                await channel.send("⏰ **Time’s up!** Great work. Type `/pomodoro_start` to begin another.")
                _pomo.pop(channel_id, None)
                return
            await asyncio.sleep(min(5, secs)) #sleep a bit before the next check
    except asyncio.CancelledError:
        return


def setup(tree: app_commands.CommandTree) -> None:
    @tree.command(description="Start a pomodoro (minutes).")
    @app_commands.describe(minutes="Length in minutes (1–180)")
    async def pomodoro_start(interaction: discord.Interaction, minutes: int):
        if minutes < 1 or minutes > 180:
            await interaction.response.send_message("Please choose 1–180 minutes.", ephemeral=True)
            return

        ch_id = interaction.channel_id
        state = _pomo.get(ch_id)

        # If a timer is already running (not paused), don't start a new one
        if state and not state.get("paused", False):
            await interaction.response.send_message(
                "A pomodoro is already running in this channel. Try `/pomodoro_pause`, `/pomodoro_status`, or `/pomodoro_cancel`.",
                ephemeral=True
            )
            return

        # Fresh start (ignore any paused remainder)
        if state and state.get("task"):
            state["task"].cancel()

        end = datetime.utcnow() + timedelta(minutes=minutes)
        _pomo[ch_id] = {
            "who": interaction.user.id,
            "started_at": datetime.utcnow(),
            "end": end,
            "paused": False,
            "remaining": 0,
            "task": asyncio.create_task(_pomo_loop(interaction.channel, ch_id)),
        }

        await interaction.response.send_message(
            f"▶️ Pomodoro started for **{minutes}m**. I’ll ping this channel when time’s up.",
            ephemeral=True
        )

    @tree.command(description="Pause the current pomodoro.")
    async def pomodoro_pause(interaction: discord.Interaction):
        ch_id = interaction.channel_id
        state = _pomo.get(ch_id)
        if not state or state.get("paused", False):
            await interaction.response.send_message("No running pomodoro to pause.", ephemeral=True)
            return

        state["remaining"] = _remaining(state)
        state["paused"] = True
        if state.get("task"):
            state["task"].cancel()
            state["task"] = None

        await interaction.response.send_message(f"⏸️ Paused. **{_fmt(state['remaining'])}** left.", ephemeral=True)

    @tree.command(description="Resume a paused pomodoro.")
    async def pomodoro_resume(interaction: discord.Interaction):
        ch_id = interaction.channel_id
        state = _pomo.get(ch_id)
        if not state or not state.get("paused", False):
            await interaction.response.send_message("Nothing to resume.", ephemeral=True)
            return

        state["end"] = datetime.utcnow() + timedelta(seconds=int(state.get("remaining", 0)))
        state["paused"] = False
        state["task"] = asyncio.create_task(_pomo_loop(interaction.channel, ch_id))

        await interaction.response.send_message("▶️ Resumed.", ephemeral=True)

    @tree.command(description="Cancel the current pomodoro.")
    async def pomodoro_cancel(interaction: discord.Interaction):
        ch_id = interaction.channel_id
        state = _pomo.get(ch_id)
        if not state:
            await interaction.response.send_message("No pomodoro to cancel.", ephemeral=True)
            return

        if state.get("task"):
            state["task"].cancel()
        _pomo.pop(ch_id, None)
        await interaction.response.send_message("🛑 Pomodoro cancelled.", ephemeral=True)

    @tree.command(description="Show remaining time.")
    async def pomodoro_status(interaction: discord.Interaction):
        state = _pomo.get(interaction.channel_id)
        if not state:
            await interaction.response.send_message("No pomodoro running.", ephemeral=True)
            return

        secs = _remaining(state)
        await interaction.response.send_message(
            f"⏱️ **{_fmt(secs)}** remaining{' (paused)' if state.get('paused') else ''}.",
            ephemeral=True
        )
