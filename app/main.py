"""FastAPI WebSocket bridge for ADK live voice."""
import asyncio
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

load_dotenv()
from app.agent import root_agent  # noqa: E402

APP_NAME = "voice_booking"
session_service = DatabaseSessionService(
    db_url=os.getenv("SESSION_DB_URL", "sqlite:///./data/sessions.db")
)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
active_sessions = set()


@asynccontextmanager
async def lifespan(_app):
    Path("data").mkdir(exist_ok=True)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def index():
    return FileResponse("frontend/index.html")


@app.websocket("/ws/{user_id}/{session_id}")
async def voice(websocket: WebSocket, user_id: str, session_id: str):
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", user_id + session_id):
        await websocket.close(code=1008)
        return
    key = (user_id, session_id)
    if key in active_sessions:
        await websocket.close(code=1008)
        return
    active_sessions.add(key)
    await websocket.accept()
    queue = LiveRequestQueue()
    try:
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
        if session is None:
            await session_service.create_session(
                app_name=APP_NAME, user_id=user_id, session_id=session_id
            )
        config = RunConfig(
            response_modalities=["AUDIO"],
            session_resumption=types.SessionResumptionConfig(),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
        )

        async def upstream():
            while True:
                data = await websocket.receive()
                if data["type"] == "websocket.disconnect":
                    break
                if data.get("bytes"):
                    queue.send_realtime(
                        types.Blob(data=data["bytes"], mime_type="audio/pcm;rate=16000")
                    )
                elif data.get("text") == "audio_end":
                    queue.send_audio_stream_end()

        async def downstream():
            async for event in runner.run_live(
                user_id=user_id,
                session_id=session_id,
                live_request_queue=queue,
                run_config=config,
            ):
                await websocket.send_text(event.model_dump_json(exclude_none=True, by_alias=True))

        tasks = [asyncio.create_task(upstream()), asyncio.create_task(downstream())]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        queue.close()
        for task in pending:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        for task in done:
            if not task.cancelled():
                exc = task.exception()
                if exc and not isinstance(exc, WebSocketDisconnect):
                    raise exc
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        queue.close()
        active_sessions.discard(key)
        try:
            await websocket.close()
        except RuntimeError:
            pass
