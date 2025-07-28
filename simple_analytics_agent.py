import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import socketio

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


@dataclass
class ConversationMetrics:
    """
    This dataclass holds all the conversation metrics we want to track.
    """
    total_speaking_time: float = 0.0      # Total time anyone spoke
    user_speaking_time: float = 0.0       # Time the user spoke
    agent_speaking_time: float = 0.0      # Time the agent spoke
    turn_count: int = 0                   # Number of conversation turns
    average_turn_length: float = 0.0      # Average length of user turns
    longest_pause: float = 0.0            # Longest pause between turns
    interruptions: int = 0                 # Number of times someone interrupted
    conversation_start_time: Optional[datetime] = None  # When conversation started
    last_user_speech: Optional[datetime] = None        # Last time user spoke
    last_agent_speech: Optional[datetime] = None       # Last time agent spoke


class SimpleAnalyticsAssistant(Agent):
    """
    This is our analytics agent that tracks conversation metrics
    and sends them to the web dashboard via Socket.IO.
    """
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a helpful conversational AI assistant with analytics capabilities. "
                "Speak naturally in English and have a friendly conversation with the user. "
                "Respond to their questions and engage in normal conversation. "
                "Keep your responses conversational and helpful. "
                "If the user asks about conversation analytics, provide detailed insights about speaking patterns, "
                "turn counts, timing, and other metrics in a helpful and informative way."
            )
        )
        # Initialize our metrics tracking
        self.metrics = ConversationMetrics()
        self.conversation_start_time = None
        self.current_turn_start = None
        
        # Initialize Socket.IO client
        self.sio = socketio.AsyncClient()
        self.socket_connected = False
        
    def _update_metrics(self, event_type: str, **kwargs):
        """
        This method updates our conversation metrics based on different events.
        It's called whenever something happens in the conversation.
        """
        now = datetime.now()
        
        if event_type == "conversation_start":
            # Conversation just started
            self.metrics.conversation_start_time = now
            self.conversation_start_time = now
            self._send_to_dashboard("Conversation started")
            
        elif event_type == "user_speech_start":
            # User started speaking
            self.metrics.last_user_speech = now
            self.current_turn_start = now
            self._send_to_dashboard("User started speaking")
            
        elif event_type == "user_speech_end":
            # User finished speaking - calculate turn duration
            if self.current_turn_start:
                duration = (now - self.current_turn_start).total_seconds()
                self.metrics.user_speaking_time += duration
                self.metrics.total_speaking_time += duration
                self.metrics.turn_count += 1
                
                # Update average turn length
                if self.metrics.turn_count > 0:
                    self.metrics.average_turn_length = self.metrics.user_speaking_time / self.metrics.turn_count
                
                self._send_to_dashboard(f"User finished speaking. Turn duration: {duration:.1f}s")
                    
        elif event_type == "agent_speech_start":
            # Agent started speaking
            self.metrics.last_agent_speech = now
            self._send_to_dashboard("Agent started speaking")
            
        elif event_type == "agent_speech_end":
            # Agent finished speaking - calculate duration
            if self.metrics.last_agent_speech:
                duration = (now - self.metrics.last_agent_speech).total_seconds()
                self.metrics.agent_speaking_time += duration
                self.metrics.total_speaking_time += duration
                self._send_to_dashboard(f"Agent finished speaking. Duration: {duration:.1f}s")
                
        elif event_type == "interruption":
            # Someone interrupted - increment counter
            self.metrics.interruptions += 1
            self._send_to_dashboard("Interruption detected")
            
        elif event_type == "pause":
            # Track pause duration
            pause_duration = kwargs.get('duration', 0)
            if pause_duration > self.metrics.longest_pause:
                self.metrics.longest_pause = pause_duration
                self._send_to_dashboard(f"New longest pause: {pause_duration:.1f}s")
        
        # Send current metrics to dashboard
        self._send_metrics_to_dashboard()
    
    async def _connect_socket(self):
        """
        Connect to the Socket.IO server.
        """
        try:
            await self.sio.connect('http://localhost:5000')
            self.socket_connected = True
            print("Connected to Socket.IO server")
        except Exception as e:
            print(f"Failed to connect to Socket.IO server: {e}")
            self.socket_connected = False
    
    def _send_to_dashboard(self, message: str):
        """
        Send a simple message to the dashboard.
        """
        if self.socket_connected:
            asyncio.create_task(self.sio.emit('log_message', {
                'message': message,
                'timestamp': datetime.now().isoformat()
            }))
    
    def _send_metrics_to_dashboard(self):
        """
        Send the current metrics to the dashboard.
        """
        if not self.socket_connected:
            return
            
        # Calculate conversation duration if started
        duration_str = "N/A"
        if self.metrics.conversation_start_time:
            duration = (datetime.now() - self.metrics.conversation_start_time).total_seconds()
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            duration_str = f"{minutes}m {seconds}s"
        
        metrics_data = {
            'type': 'metrics_update',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'conversation_duration': duration_str,
                'total_speaking_time': self.metrics.total_speaking_time,
                'user_speaking_time': self.metrics.user_speaking_time,
                'agent_speaking_time': self.metrics.agent_speaking_time,
                'turn_count': self.metrics.turn_count,
                'average_turn_length': self.metrics.average_turn_length,
                'longest_pause': self.metrics.longest_pause,
                'interruptions': self.metrics.interruptions
            }
        }
        
        asyncio.create_task(self.sio.emit('metrics_update', metrics_data))
    
    def get_analytics_summary(self) -> str:
        """
        Generate a voice-friendly analytics summary that the agent can speak.
        This is what the user hears when they ask for analytics.
        """
        if not self.metrics.conversation_start_time:
            return "No conversation data available yet."
            
        # Calculate total conversation duration
        duration = (datetime.now() - self.metrics.conversation_start_time).total_seconds()
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        # Create a natural language summary
        summary = f"""
        Conversation Analytics Summary:
        - Total conversation time: {minutes} minutes and {seconds} seconds
        - Total speaking time: {self.metrics.total_speaking_time:.1f} seconds
        - Your speaking time: {self.metrics.user_speaking_time:.1f} seconds
        - My speaking time: {self.metrics.agent_speaking_time:.1f} seconds
        - Number of turns: {self.metrics.turn_count}
        - Average turn length: {self.metrics.average_turn_length:.1f} seconds
        - Longest pause: {self.metrics.longest_pause:.1f} seconds
        - Interruptions: {self.metrics.interruptions}
        """
        
        # Send the summary to dashboard
        self._send_to_dashboard("Analytics summary requested by user")
        self._send_to_dashboard(summary.strip())
        
        return summary


async def entrypoint(ctx: agents.JobContext):
    """
    This is the main entry point for our LiveKit agent.
    It sets up the session with all the AI plugins and starts the conversation.
    """
    # Create the session with all our AI plugins
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),      # Speech-to-Text
        llm=openai.LLM(model="gpt-4o-mini"),                    # Language model for translation
        tts=cartesia.TTS(model="sonic-2", voice="c0c374aa-09be-42d9-9828-4d2d7df86962"),  # Text-to-Speech
        vad=silero.VAD.load(),                                   # Voice Activity Detection
        turn_detection=MultilingualModel(),                      # Turn detection
    )

    # Create our enhanced agent
    agent = SimpleAnalyticsAssistant()
    
    # Connect to Socket.IO server
    await agent._connect_socket()
    
    # Start the session with our agent
    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),  # Noise cancellation
        ),
    )

    # Connect to the room
    await ctx.connect()
    
    # Mark the start of our conversation for analytics
    agent._update_metrics("conversation_start")

    # Generate the initial greeting
    await session.generate_reply(
        instructions=(
            "Greet the user and explain that you are a conversational AI assistant "
            "with analytics capabilities. Tell them you can have a normal conversation in English. "
            "Also mention that they can ask for conversation analytics by saying 'show me my stats' or 'analytics'. "
            "Tell them they can open the dashboard.html file in their browser to see real-time analytics!"
        )
    )


if __name__ == "__main__":
    # This runs the agent when the script is executed
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint)) 