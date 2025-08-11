import React, { useState } from "react";
import { Room, createLocalAudioTrack, LocalAudioTrack } from "livekit-client";

const ROOM_NAME = "spanish-grammar-room";

export const LiveKitVoiceInput: React.FC = () => {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const connectToLiveKit = async () => {
    try {
      // Fetch token and URL from backend
      const identity = "user-" + Math.floor(Math.random() * 100000);
      const resp = await fetch(`/api/livekit-token?identity=${identity}`);
      const { token, url, room } = await resp.json();

      if (room !== ROOM_NAME) throw new Error("Room mismatch!");

      const livekitRoom = new Room();
      await livekitRoom.connect(url, token);
      setConnected(true);

      // Create and publish audio track (continuous mic stream)
      const audioTrack: LocalAudioTrack = await createLocalAudioTrack();
      await livekitRoom.localParticipant.publishTrack(audioTrack);

    } catch (err: any) {
      setError(err.message || "Failed to connect to LiveKit");
    }
  };

  return (
    <div>
      {!connected ? (
        <button className="bg-blue-500 text-white px-4 py-2 rounded" onClick={connectToLiveKit}>
          Join Voice Session
        </button>
      ) : (
        <span className="text-green-600">Connected and publishing audio!</span>
      )}
      {error && <div className="text-red-600">{error}</div>}
    </div>
  );
};