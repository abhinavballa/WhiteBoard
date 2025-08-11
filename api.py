from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import jwt  # This is PyJWT
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
ROOM_NAME = "spanish-grammar-room"

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

def create_livekit_token(identity, room, exp_minutes=60):
    now = datetime.utcnow()
    exp = now + timedelta(minutes=exp_minutes)
    payload = {
        "iss": LIVEKIT_API_KEY,
        "sub": identity,
        "room": room,
        "exp": int(exp.timestamp()),
        "nbf": int(now.timestamp()),
        # Add additional claims if needed
    }
    token = jwt.encode(payload, LIVEKIT_API_SECRET, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

@app.get("/api/livekit-token")
def get_livekit_token(identity: str = Query(...)):
    token = create_livekit_token(identity, ROOM_NAME)
    return { "token": token, "url": LIVEKIT_URL, "room": ROOM_NAME }