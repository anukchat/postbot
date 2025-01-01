import React from 'react';
import { Media } from '../../types';
import { X, Play } from 'lucide-react';

interface VideoPickerProps {
    media: Media[];
    onSelect: (media: Media) => void;
    onClose: () => void;
}

export const VideoPicker: React.FC<VideoPickerProps> = ({ media, onSelect, onClose }) => {
    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium">Select Video</h3>
                <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
                    <X className="w-5 h-5" />
                </button>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
                {media.map((item) => (
                    <div 
                        key={item.url}
                        className="relative group cursor-pointer"
                        onClick={() => onSelect(item)}
                    >
                        <div className="relative">
                            <video 
                                src={item.url}
                                poster={item.thumbnail_url}
                                preload="metadata"
                                className="w-full h-40 object-cover rounded"
                            >
                                <source src={item.url} type="video/mp4" />
                                Your browser does not support the video tag.
                            </video>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <Play className="w-12 h-12 text-white opacity-75 group-hover:opacity-100" />
                            </div>
                        </div>
                        {item.title && (
                            <p className="mt-2 text-sm truncate">{item.title}</p>
                        )}
                        {item.duration && (
                            <span className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-xs">
                                {Math.floor(item.duration / 60)}:{(item.duration % 60).toString().padStart(2, '0')}
                            </span>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};
