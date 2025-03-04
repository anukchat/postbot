import React, { useEffect } from 'react';
import { useEditorStore } from '../../store/editorStore';
import { useNavigate } from 'react-router-dom';
import { X, CheckCircle, AlertCircle, Clock, Loader2 } from 'lucide-react';
import { toast } from 'react-hot-toast';
import Tippy from '@tippyjs/react';
import 'tippy.js/dist/tippy.css';

export const GenerationStatusList: React.FC = () => {
  const {
    runningGenerations,
    hasRunningGenerations,
    cancelGeneration,
    clearCompletedGenerations
  } = useEditorStore();
  const navigate = useNavigate();
  
  // Notify when generations complete
  useEffect(() => {
    const completedGenerations = Object.entries(runningGenerations).filter(
      ([_, gen]) => gen.status === 'completed' && gen.notificationShown !== true
    );
    
    completedGenerations.forEach(([id]) => {
      toast.success(
        <div className="flex flex-col">
          <span>Content generation completed!</span>
          <button 
            className="text-blue-400 underline mt-1 text-sm"
            onClick={() => {
              navigate(`/dashboard`, { state: { threadId: id } });
              toast.dismiss();
            }}
          >
            View content
          </button>
        </div>,
        { duration: 5000, position: 'top-right' }
      );
      
      // Mark as notified to prevent duplicate notifications
      useEditorStore.setState(state => ({
        runningGenerations: {
          ...state.runningGenerations,
          [id]: {
            ...state.runningGenerations[id],
            notificationShown: true
          }
        }
      }));
    });
  }, [runningGenerations, navigate]);
  
  if (!hasRunningGenerations) return null;
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'cancelled':
        return <X className="h-4 w-4 text-orange-500" />;
      case 'initializing':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'running':
      default:
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
    }
  };
  
  const getElapsedTime = (startTime: number) => {
    const seconds = Math.floor((Date.now() - startTime) / 1000);
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const activeGenerations = Object.entries(runningGenerations).filter(
    ([_, gen]) => gen.status === 'initializing' || gen.status === 'running'
  );
  
  const completedGenerations = Object.entries(runningGenerations).filter(
    ([_, gen]) => gen.status === 'completed' || gen.status === 'failed' || gen.status === 'cancelled'
  );
  
  return (
    <div className="fixed bottom-4 right-4 z-50 w-72 bg-white dark:bg-gray-800 shadow-lg rounded-lg overflow-hidden">
      <div className="px-4 py-2 bg-gray-100 dark:bg-gray-700 flex justify-between items-center">
        <h3 className="font-medium text-sm">Content Generation</h3>
        {completedGenerations.length > 0 && (
          <Tippy content="Clear completed generations">
            <button 
              onClick={clearCompletedGenerations} 
              className="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white"
            >
              <X className="h-4 w-4" />
            </button>
          </Tippy>
        )}
      </div>
      
      <div className="max-h-64 overflow-y-auto divide-y divide-gray-200 dark:divide-gray-700">
        {/* Active generations */}
        {activeGenerations.map(([id, generation]) => (
          <div key={id} className="p-3 bg-white dark:bg-gray-800">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                {getStatusIcon(generation.status)}
                <span className="text-sm font-medium truncate">
                  {generation.post_types.join(', ')} content
                </span>
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {getElapsedTime(generation.startTime)}
              </span>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">
              {generation.progress || 'Processing...'}
            </p>
            <div className="mt-2 flex justify-end">
              <button
                onClick={() => cancelGeneration(id)}
                className="text-xs text-red-500 hover:text-red-700"
              >
                Cancel
              </button>
            </div>
          </div>
        ))}
        
        {/* Completed/Failed/Cancelled generations */}
        {completedGenerations.map(([id, generation]) => (
          <div 
            key={id} 
            className={`p-3 ${
              generation.status === 'completed' 
                ? 'bg-green-50 dark:bg-green-900/20' 
                : generation.status === 'failed'
                ? 'bg-red-50 dark:bg-red-900/20'
                : 'bg-gray-50 dark:bg-gray-900/20'
            }`}
          >
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                {getStatusIcon(generation.status)}
                <span className="text-sm font-medium truncate">
                  {generation.post_types.join(', ')} content
                </span>
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {getElapsedTime(generation.startTime)}
              </span>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">
              {generation.progress}
            </p>
            {generation.status === 'completed' && (
              <div className="mt-2 flex justify-end">
                <button
                  onClick={() => {
                    navigate(`/dashboard`, { state: { threadId: id } });
                  }}
                  className="text-xs text-blue-500 hover:text-blue-700"
                >
                  View Content
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};