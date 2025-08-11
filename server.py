import asyncio
import socketio
from aiohttp import web

sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit('welcome', {'message': 'Conectado al panel de análisis'}, room=sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def metrics_update(sid, data):
    print(f"Received metrics from agent: {data}")
    await sio.emit('metrics_update', data)

async def start_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 5000)
    await site.start()
    print("Socket.IO server running on http://localhost:5000")
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(start_server())