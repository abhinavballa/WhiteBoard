import React from "react";

type Props = {
  connected: boolean;
};

export const ConnectionStatus: React.FC<Props> = ({ connected }) => (
  <div className="mb-4">
    <span
      className={`px-2 py-1 rounded text-sm font-mono ${
        connected ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
      }`}
    >
      {connected ? "Connected to server" : "Disconnected"}
    </span>
  </div>
);