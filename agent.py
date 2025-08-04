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

def analyze_grammar(spanish_text):
    # Placeholder: Replace with actual grammar-checking logic or API
    # For demo, we'll "detect" error if sentence doesn't end with a period
    feedback = []
    error_flag = False
    if not spanish_text.strip().endswith('.'):
        feedback.append("Recuerda terminar las frases con un punto final.")
        error_flag = True
    # You could expand this to call a Spanish grammar API or LLM here
    return feedback, error_flag

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "Eres un asistente conversacional de IA que habla solo en español. "
                "Corrige los errores gramaticales del usuario y proporciona retroalimentación constructiva en español. "
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
            'feedback_messages': [],  # Now a list of dicts
            'start_time': None
        }
        self.current_turn_start = None

    async def on_user_message(self, user_text):
        feedback, error = analyze_grammar(user_text)
        if error:
            self.metrics['error_count'] += 1
            for fb in feedback:
                self.metrics['feedback_messages'].append({
                    'message': user_text,
                    'feedback': fb
                })
        await self.sio.emit('metrics_update', self.metrics)

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="es"),
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