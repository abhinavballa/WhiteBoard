import React, { useEffect, useState } from "react";
import io from "socket.io-client";
import { ConnectionStatus } from "../components/ConnectionStatus";
import { MetricCard } from "../components/MetricCard";
import { FeedbackList } from "../components/FeedbackList";

type Metrics = {
  total_time: number;
  user_time: number;
  agent_time: number;
  turns: number;
  error_count: number;
  feedback_messages: { message: string; feedback: string }[];
  start_time: string | null;
};

const SOCKET_URL = "http://localhost:5000"; // Update if using a different server

const defaultMetrics: Metrics = {
  total_time: 0,
  user_time: 0,
  agent_time: 0,
  turns: 0,
  error_count: 0,
  feedback_messages: [],
  start_time: null,
};

export default function Home() {
  const [connected, setConnected] = useState(false);
  const [metrics, setMetrics] = useState<Metrics>(defaultMetrics);

  useEffect(() => {
    const socket = io(SOCKET_URL);

    socket.on("connect", () => setConnected(true));
    socket.on("disconnect", () => setConnected(false));
    socket.on("welcome", (data) => setConnected(true));
    socket.on("metrics_update", (newMetrics: Metrics) => setMetrics({ ...metrics, ...newMetrics }));

    return () => {
      socket.disconnect();
    };
  }, [metrics]);

  return (
    <main className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-4 text-gray-800">Spanish Grammar Analysis Dashboard</h1>
        <ConnectionStatus connected={connected} />
        <div className="flex flex-wrap gap-2 mt-6">
          <MetricCard label="Total Time" value={metrics.total_time} />
          <MetricCard label="User Time" value={metrics.user_time} />
          <MetricCard label="Agent Time" value={metrics.agent_time} />
          <MetricCard label="Turns" value={metrics.turns} />
          <MetricCard label="Error Count" value={metrics.error_count} />
          <MetricCard label="Session Start" value={metrics.start_time ? metrics.start_time : "-"} />
        </div>
        <FeedbackList feedbackMessages={metrics.feedback_messages} />
      </div>
    </main>
  );
}