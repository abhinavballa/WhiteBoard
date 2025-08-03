import asyncio
import socketio
from datetime import datetime
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a helpful conversational AI assistant. "
                "Speak naturally in English and have friendly conversations. "
                "Respond to questions and engage naturally. "
                "If the user asks about analytics, provide conversation insights."
            )
        )
        self.sio = socketio.AsyncClient()
        self.metrics = {
            'total_time': 0,
            'user_time': 0,
            'agent_time': 0,
            'turns': 0,
            'start_time': None
        }
        self.current_turn_start = None


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(model="sonic-2", voice="c0c374aa-09be-42d9-9828-4d2d7df86962"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    agent = Assistant()
    
    # Connect to Socket.IO server
    await agent.sio.connect('http://localhost:5000')
    
    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(), 
        ),
    )

    await ctx.connect()
    
    # Start analytics
    agent.metrics['start_time'] = datetime.now()
    await agent.sio.emit('metrics_update', agent.metrics)

    await session.generate_reply(
        instructions="Greet the user and explain you're a conversational AI with analytics. Tell them to open dashboard.html to see live metrics."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))