import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any
import socketio
from aiohttp import web

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# Store connected clients
connected_clients = set()

@sio.event
async def connect(sid, environ):
    """
    Handle client connection.
    """
    connected_clients.add(sid)
    logger.info(f"Client connected: {sid}. Total clients: {len(connected_clients)}")
    
    # Send welcome message
    await sio.emit('welcome', {
        'message': 'Connected to Voice Analytics Dashboard',
        'timestamp': datetime.now().isoformat(),
        'client_count': len(connected_clients)
    }, room=sid)

@sio.event
async def disconnect(sid):
    """
    Handle client disconnection.
    """
    connected_clients.discard(sid)
    logger.info(f"Client disconnected: {sid}. Total clients: {len(connected_clients)}")

@sio.event
async def metrics_update(sid, data):
    """
    Handle metrics updates from the agent.
    Broadcast to all connected clients.
    """
    logger.info(f"Received metrics update from agent")
    
    # Broadcast to all connected clients
    await sio.emit('metrics_update', data, skip_sid=sid)

@sio.event
async def log_message(sid, data):
    """
    Handle log messages from the agent.
    Broadcast to all connected clients.
    """
    logger.info(f"Received log message: {data.get('message', '')}")
    
    # Broadcast to all connected clients
    await sio.emit('log_message', data, skip_sid=sid)

@sio.event
async def request_analytics(sid, data):
    """
    Handle analytics requests from clients.
    """
    logger.info(f"Client {sid} requested analytics")
    
    # Send acknowledgment
    await sio.emit('analytics_request_received', {
        'message': 'Analytics request received',
        'timestamp': datetime.now().isoformat()
    }, room=sid)

async def start_server():
    """
    Start the Socket.IO server.
    """
    logger.info("Starting Socket.IO server on http://localhost:5000")
    
    # Create web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 5000)
    await site.start()
    
    logger.info("Socket.IO server running on http://localhost:5000")
    
    # Keep the server running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(start_server()) 