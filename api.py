from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from livekit import jwt
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
ROOM_NAME = "spanish-grammar-room"

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.get("/api/livekit-token")
def get_livekit_token(identity: str = Query(...)):
    token = jwt.create_access_token(
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
        room=ROOM_NAME,
        identity=identity,
    )
    return { "token": token, "url": LIVEKIT_URL, "room": ROOM_NAME }