import React from "react";

type Props = {
  connected: boolean;
};

export const ConnectionStatus: React.FC<Props> = ({ connected }) => (
  <div className={`py-2 px-4 rounded text-white ${connected ? "bg-green-500" : "bg-red-500"}`}>
    {connected ? "Connected to analysis server" : "Disconnected"}
  </div>
);