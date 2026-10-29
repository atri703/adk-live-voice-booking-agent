"""Google ADK speech-to-speech booking agent."""
import os

from google.adk.agents import Agent
from app.store import create_booking, delete_booking, list_bookings, update_booking

root_agent = Agent(
    name="voice_booking_agent",
    model=os.getenv("GEMINI_LIVE_MODEL", "gemini-2.5-flash-native-audio-preview-09-2025"),
    instruction=(
        "You are a friendly appointment booking voice assistant. "
        "Use tools for all booking reads and writes. Never invent booking IDs or availability. "
        "Ask for missing name, date, time, duration, and timezone. "
        "Use ISO 8601 timestamps with explicit timezone offsets for tool calls. "
        "Before deleting, ask for explicit confirmation. "
        "Before updating, identify the booking unambiguously and confirm changes. "
        "Summarize successful operations succinctly. "
        "This is a demo with a shared local booking dataset; do not claim calendar integration."
    ),
    tools=[list_bookings, create_booking, update_booking, delete_booking],
)
