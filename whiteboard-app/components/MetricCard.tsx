import React from "react";

type Props = {
  label: string;
  value: string | number | null;
};

export const MetricCard: React.FC<Props> = ({ label, value }) => (
  <div className="flex flex-col items-start bg-white rounded shadow p-4 w-40 border-l-4 border-blue-400">
    <span className="font-semibold text-sm text-gray-600">{label}</span>
    <span className="text-xl font-bold text-gray-900 mt-1">{value}</span>
  </div>
);