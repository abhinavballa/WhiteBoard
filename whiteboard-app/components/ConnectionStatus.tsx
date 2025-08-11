import React from "react";

type ConnectionStatusProps = {
  connected: boolean;
};

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ connected }) => (
  <div className="mb-4">
    <span className={connected ? "text-green-600" : "text-red-600"}>
      {connected ? "Connected to server" : "Disconnected"}
    </span>
  </div>
);