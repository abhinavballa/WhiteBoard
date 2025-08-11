import asyncio
import socketio
import os
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

# Load environment variables
load_dotenv()
ROOM_NAME = os.getenv("ROOM_NAME", "spanish-grammar-room")  # fallback to default room name

async def get_grammar_feedback(llm, spanish_text):
    # Prompt OpenAI to provide a grammar correction in English.
    prompt = (
        f"You are a Spanish language tutor. A student said the following sentence in Spanish:\n\n"
        f"\"{spanish_text}\"\n\n"
        f"Detect any grammar, verb conjugation, gender agreement, or sentence structure errors. "
        f"Respond in this format:\n"
        f"Spanish sentence: <the original sentence>\n"
        f"Error description (English): <brief explanation of mistake(s) in English, or 'No errors found.' if correct>"
    )
    response = await llm.complete(prompt)
    # Parse response (expecting two lines: Spanish sentence and Error description)
    lines = response.text.strip().split("\n")
    sentence = ""
    error_desc = ""
    for line in lines:
        if line.lower().startswith("spanish sentence:"):
            sentence = line[len("Spanish sentence:"):].strip()
        elif line.lower().startswith("error description"):
            error_desc = line.split(":", 1)[1].strip()
    # Fallback if format doesn't match
    if not sentence:
        sentence = spanish_text
    if not error_desc:
        error_desc = response.text.strip()
    return sentence, error_desc

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "Eres un asistente conversacional de IA que habla solo en español. "
                "Corrige los errores gramaticales del usuario y proporciona retroalimentación constructiva en inglés. "
                "Sé amable y motiva al usuario a mejorar su gramática."
            )
        )
        self.sio = socketio.AsyncClient()
        self.metrics = {
            'total_time': 0,
            'user_time': 0,
            'agent_time': 0,
            'turns': 0,
            'error_count': 0,
            'feedback_messages': [],
            'start_time': None
        }
        self.current_turn_start = None

    async def on_user_message(self, user_text):
        sentence, error_desc = await get_grammar_feedback(self.llm, user_text)
        error_flag = error_desc.lower() != "no errors found."
        if error_flag:
            self.metrics['error_count'] += 1
        self.metrics['feedback_messages'].append({
            'message': sentence,
            'feedback': error_desc
        })
        await self.sio.emit('metrics_update', self.metrics)

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
        room=ctx.room if hasattr(ctx, "room") and ctx.room else ROOM_NAME,
        agent=agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(), 
        ),
    )

    await ctx.connect()
    
    # Start analytics
    agent.metrics['start_time'] = datetime.now().isoformat()
    await agent.sio.emit('metrics_update', agent.metrics)

    await session.generate_reply(
        instructions="¡Hola! Soy tu asistente de IA. Podemos conversar en español. "
                     "Te ayudaré corrigiendo tus errores gramaticales y te daré retroalimentación en el panel. "
                     "Abre dashboard.html para ver tus métricas y retroalimentación en tiempo real."
    )

    # Listen for user messages and process feedback
    async for event in session.events():
        if event.type == "user_message":
            agent.metrics['turns'] += 1
            await agent.on_user_message(event.text)

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))