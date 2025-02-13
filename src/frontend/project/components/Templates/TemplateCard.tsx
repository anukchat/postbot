import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

interface TemplateProps {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  category: string;
}

export const TemplateCard: React.FC<TemplateProps> = ({ 
  id, 
  title, 
  description, 
  thumbnail,
  category 
}) => {
  const navigate = useNavigate();

  const handleTemplateSelect = () => {
    navigate('/dashboard', { 
      state: { 
        showSourceModal: true,
        selectedTemplate: {
          id,
          title,
          description,
          category
        }
      } 
    });
  };

  return (
    <div 
      onClick={handleTemplateSelect}
      className="group relative bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden border border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500"
    >
      {/* Thumbnail with gradient overlay */}
      <div className="aspect-[16/9] overflow-hidden relative">
        <div className="absolute inset-0 bg-gradient-to-b from-black/0 to-black/60 z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        <img 
          src={thumbnail} 
          alt={title}
          className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-300"
        />
      </div>

      {/* Content */}
      <div className="p-4">
        <span className="inline-block text-xs font-medium text-blue-500 dark:text-blue-400 mb-2 px-2 py-1 bg-blue-50 dark:bg-blue-900/30 rounded-full">
          {category}
        </span>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2 group-hover:text-blue-500 dark:group-hover:text-blue-400 transition-colors">
          {title}
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-4">
          {description}
        </p>

        {/* Use Template button - visible on hover */}
        <div className="flex items-center justify-end">
          <span className="inline-flex items-center gap-1 text-sm font-medium text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            Use Template
            <ArrowRight className="w-4 h-4" />
          </span>
        </div>
      </div>
    </div>
  );
};