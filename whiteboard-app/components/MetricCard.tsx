import React from "react";

type MetricProps = {
  label: string;
  value: string | number;
};

export const MetricCard: React.FC<MetricProps> = ({ label, value }) => (
  <div className="flex flex-col items-center bg-gray-100 rounded p-4 shadow m-2 min-w-[140px]">
    <span className="text-xs font-semibold text-gray-600">{label}</span>
    <span className="text-xl font-bold text-gray-800">{value}</span>
  </div>
);