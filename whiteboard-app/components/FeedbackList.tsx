import React from "react";

type FeedbackMessage = {
  message: string;
  feedback: string;
};

type Props = {
  feedbackMessages: FeedbackMessage[];
};

export const FeedbackList: React.FC<Props> = ({ feedbackMessages }) => (
  <div className="mt-6">
    <h2 className="text-lg font-bold mb-3 text-gray-700">Grammar Feedback</h2>
    <ul className="pl-2">
      {feedbackMessages.length === 0 && (
        <li className="text-gray-400">No feedback yet.</li>
      )}
      {feedbackMessages.map((entry, idx) => (
        <li key={idx} className="mb-3 bg-white rounded shadow p-3 border-l-4 border-red-400">
          <div className="mb-1"><strong>Spanish:</strong> {entry.message}</div>
          <div className="text-sm text-gray-700"><strong>English:</strong> {entry.feedback}</div>
        </li>
      ))}
    </ul>
  </div>
);