import React from "react";
import { Dialog } from '@headlessui/react';
import { toast } from 'react-hot-toast';

export const FeedbackModal: React.FC<{
  feedback: string;
  setFeedback: (f: string) => void;
  handleFeedbackSubmit: () => void;
  setShowFeedbackModal: (show: boolean) => void;
}> = ({ feedback, setFeedback, handleFeedbackSubmit, setShowFeedbackModal }) => {
  
  const handleInternalFeedbackSubmit = async () => {
    try {
      await handleFeedbackSubmit(); 
    } catch (err: any) {
      console.error(err);
      if (
        err.response?.status === 403 &&
        err.response?.data?.detail?.includes("Generation limit reached")
      ) {
        toast.error('User has exceeded the generation limit');
      }
    }
  };

  return (
    <Dialog open={true} onClose={() => setShowFeedbackModal(false)} className="relative z-50">
      {/* Dark overlay */}
      <div className="fixed inset-0 bg-black/30 backdrop-blur-sm" aria-hidden="true" />

      {/* Modal container */}
      <div className="fixed inset-0 flex items-center justify-center">
        <Dialog.Panel className="w-[500px] rounded-lg bg-white dark:bg-gray-800 p-6 shadow-xl">
          <Dialog.Title className="text-lg font-semibold mb-4">
            Provide Feedback
          </Dialog.Title>
          
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="What would you like to improve?"
            className="w-full h-32 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          
          <div className="flex justify-end gap-3 mt-4">
            <button
              onClick={() => setShowFeedbackModal(false)}
              className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              Cancel
            </button>
            <button
              onClick={handleInternalFeedbackSubmit}
              disabled={!feedback.trim()}
              className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
            >
              Submit Feedback
            </button>
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
};