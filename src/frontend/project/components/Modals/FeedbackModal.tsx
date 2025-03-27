import React, { useState } from "react";
import { Dialog } from '@headlessui/react';
import { toast } from 'react-hot-toast';

export const FeedbackModal: React.FC<{
  feedback: string;
  setFeedback: (f: string) => void;
  handleFeedbackSubmit: () => void;
  setShowFeedbackModal: (show: boolean) => void;
}> = ({ feedback, setFeedback, handleFeedbackSubmit, setShowFeedbackModal }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const handleInternalFeedbackSubmit = async () => {
    setIsSubmitting(true);
    try {
      await handleFeedbackSubmit();
      setShowFeedbackModal(false);
    } catch (err: any) {
      console.error(err);
      if (
        err.response?.status === 403 &&
        err.response?.data?.detail?.includes("Generation limit reached")
      ) {
        toast.error('User has exceeded the generation limit');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog 
      open={true} 
      onClose={() => !isSubmitting && setShowFeedbackModal(false)} 
      className="relative z-[99999]"
    >
      {/* Dark overlay with higher z-index to block editor */}
      <div className="fixed inset-0 bg-black/30 backdrop-blur-sm z-[99998]" aria-hidden="true" />

      {/* Modal container */}
      <div className="fixed inset-0 flex items-center justify-center z-[99999]">
        <Dialog.Panel className="w-[500px] rounded-lg bg-white dark:bg-gray-800 p-6 shadow-xl">
          <Dialog.Title className="text-lg font-semibold mb-4">
            Provide Feedback
          </Dialog.Title>
          
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            disabled={isSubmitting}
            placeholder="What would you like to improve?"
            className="w-full h-32 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          
          <div className="flex justify-end gap-3 mt-4">
            <button
              onClick={() => setShowFeedbackModal(false)}
              disabled={isSubmitting}
              className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleInternalFeedbackSubmit}
              disabled={!feedback.trim() || isSubmitting}
              className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 flex items-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Submitting...
                </>
              ) : (
                'Submit Feedback'
              )}
            </button>
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
};