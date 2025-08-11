import React from "react";

type FeedbackMessage = {
  message: string;
  feedback: string;
};

type FeedbackListProps = {
  feedbackMessages: FeedbackMessage[];
};

export const FeedbackList: React.FC<FeedbackListProps> = ({ feedbackMessages }) => (
  <div className="mt-6">
    <h2 className="text-xl font-semibold mb-2">Feedback Messages</h2>
    <ul>
      {feedbackMessages.map((fm, idx) => (
        <li key={idx} className="mb-2 p-2 bg-gray-100 rounded">
          <strong>Spanish:</strong> {fm.message}
          <br />
          <strong>Feedback:</strong> {fm.feedback}
        </li>
      ))}
    </ul>
  </div>
);