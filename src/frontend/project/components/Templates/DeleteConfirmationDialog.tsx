import React from 'react';
import { Dialog } from '@headlessui/react';
import { LoadingSpinner } from '../common/LoadingSpinner';

interface DeleteConfirmationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  isLoading: boolean;
  templateName: string;
}

export const DeleteConfirmationDialog: React.FC<DeleteConfirmationDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  isLoading,
  templateName,
}) => {
  const handleConfirm = async () => {
    await onConfirm();
  };

  return (
    <Dialog open={isOpen} onClose={onClose} className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen">
        <div className="fixed inset-0 bg-black opacity-30" />

        <div className="relative bg-white dark:bg-gray-800 rounded-lg max-w-md w-full mx-4 p-6">
          <Dialog.Title className="text-xl font-semibold mb-4">
            Delete Template
          </Dialog.Title>

          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Are you sure you want to delete the template "{templateName}"? This action cannot be undone.
          </p>

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleConfirm}
              className="px-4 py-2 bg-red-600 text-white hover:bg-red-700 rounded-lg flex items-center"
              disabled={isLoading}
            >
              {isLoading && <LoadingSpinner size="sm" className="mr-2" />}
              Delete
            </button>
          </div>
        </div>
      </div>
    </Dialog>
  );
};