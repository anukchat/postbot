import React from 'react';
import Modal from 'react-modal';
import { Url } from '../../types';
import { LinkPreview } from './LinkPreview';
import { X } from 'lucide-react';

interface UrlPickerProps {
  isOpen: boolean;
  onClose: () => void;
  urls: Url[];
  onSelect: (url: Url) => void;
}

export const UrlPicker: React.FC<UrlPickerProps> = ({ isOpen, onClose, urls, onSelect }) => {
  const customStyles = {
    overlay: {
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      zIndex: 1000,
    },
    content: {
      top: '50%',
      left: '50%',
      right: 'auto',
      bottom: 'auto',
      marginRight: '-50%',
      transform: 'translate(-50%, -50%)',
      width: '600px',
      maxHeight: '80vh',
      padding: '20px',
      border: 'none',
      borderRadius: '10px',
      backgroundColor: '#fff',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    },
  };

  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onClose}
      style={customStyles}
      contentLabel="Select Link"
      ariaHideApp={false}
    >
      <div className="space-y-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium">Select Link</h3>
          <button 
            onClick={onClose} 
            className="p-1 hover:bg-gray-100 rounded transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="space-y-3 max-h-[60vh] overflow-y-auto">
          {urls.length > 0 ? (
            urls.map((url) => (
              <LinkPreview 
                key={url.url} 
                url={url} 
                onSelect={onSelect} 
              />
            ))
          ) : (
            <div className="text-center text-gray-500 py-8">
              No links available
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
};
