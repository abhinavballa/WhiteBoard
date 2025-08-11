import React from "react";

type MetricCardProps = {
  label: string;
  value: string | number;
};

export const MetricCard: React.FC<MetricCardProps> = ({ label, value }) => (
  <div className="bg-white p-4 rounded shadow w-40 mb-2">
    <div className="text-xs text-gray-500">{label}</div>
    <div className="text-lg font-bold">{value}</div>
  </div>
);