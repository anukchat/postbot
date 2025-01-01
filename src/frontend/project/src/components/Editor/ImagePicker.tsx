import React from 'react';
import { Media } from '../../types';
import { X } from 'lucide-react';

interface ImagePickerProps {
  media: Media[];
  onSelect: (media: Media) => void;
  onClose: () => void;
}

export const ImagePicker: React.FC<ImagePickerProps> = ({ media, onSelect, onClose }) => {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">Select Image</h3>
        <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
          <X className="w-5 h-5" />
        </button>
      </div>
      
      <div className="grid grid-cols-3 gap-4">
        {media.map((item) => (
          <div 
            key={item.url}
            className="relative group cursor-pointer"
            onClick={() => onSelect(item)}
          >
            <img 
              src={item.url} 
              alt={item.alt_text || ''} 
              className="w-full h-32 object-cover rounded"
            />
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity flex items-center justify-center">
              <span className="text-white opacity-0 group-hover:opacity-100">Select</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
