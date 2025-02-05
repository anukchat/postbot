import React, { useState, useMemo } from 'react';
import { 
  MessageSquare, 
  Settings, 
  History, 
  HelpCircle, 
  Rocket, 
  Undo,
  Redo,
  Copy  // new import for copy icon
} from 'lucide-react';
import Tippy from '@tippyjs/react';
import 'tippy.js/dist/tippy.css';
import { useEditorStore } from '../../store/editorStore';
import { FeedbackModal } from '../Modals/FeedbackModal';
import { UrlPicker } from '../Editor/UrlPicker';
import { toast } from 'react-hot-toast';

interface IconMenuBarProps {
  selectedTab: 'blog' | 'twitter' | 'linkedin';
  onCommandInsert?: (commandText: string, replaceLength: number) => void;
}

export const IconMenuBar: React.FC<IconMenuBarProps> = ({ selectedTab, onCommandInsert }) => {
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedback, setFeedback] = useState('');
  const { currentPost, generatePost, fetchContentByThreadId } = useEditorStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [showUrlPicker, setShowUrlPicker] = useState(false);

  // New function to handle copying the rich editor content (HTML)
  const handleCopy = async () => {
    // Query the rendered editor container by class name
    const editorElement = document.querySelector('.custom-editor');
    if (editorElement) {
      try {
        const html = editorElement.innerHTML;
        // Write both HTML and plain text to the clipboard
        await navigator.clipboard.write([
          new ClipboardItem({
            "text/html": new Blob([html], { type: "text/html" }),
            "text/plain": new Blob([html], { type: "text/plain" })
          })
        ]);
        toast.success('Content copied with formatting');
      } catch (error) {
        toast.error('Failed to copy rich content');
      }
    } else {
      toast.error('Editor content not found');
    }
  };

  const handleFeedbackSubmit = async () => {
    if (!feedback.trim() || !currentPost?.thread_id) return;
    
    setIsGenerating(true);
    try {
      const payload = {
        thread_id: currentPost.thread_id,
        post_types: [selectedTab],
        feedback: feedback,
        ...(currentPost.source_type === 'twitter' ? { tweet_id: currentPost.source_identifier } : {}),
        ...(currentPost.source_type === 'web_url' ? { url: currentPost.source_identifier } : {})
      };
      
      await generatePost([selectedTab], currentPost.thread_id, payload);
      await fetchContentByThreadId(currentPost.thread_id, selectedTab);
      setShowFeedbackModal(false);
      setFeedback('');
      toast.success('Feedback submitted successfully');
    } catch (error) {
      toast.error('Failed to submit feedback');
    } finally {
      setIsGenerating(false);
    }
  };

  const isGenerateDisabled = selectedTab === 'blog' ||
    (selectedTab === 'twitter' && !!currentPost?.twitter_post) ||
    (selectedTab === 'linkedin' && !!currentPost?.linkedin_post);

  const shouldShowFeedback = currentPost && (
    (selectedTab === 'blog' && currentPost.content) ||
    (selectedTab === 'twitter' && currentPost.twitter_post) ||
    (selectedTab === 'linkedin' && currentPost.linkedin_post)
  );

  const handleUrlSelect = (url: { url: string }) => {
    const insertText = `[${url.url}](${url.url})`;
    onCommandInsert?.(insertText, 0);
    setShowUrlPicker(false);
  };

  const handleUndo = (e: React.MouseEvent) => {
    e.preventDefault();
    document.execCommand('undo', false);
  };

  const handleRedo = (e: React.MouseEvent) => {
    e.preventDefault();
    document.execCommand('redo', false);
  };

  const hasTweetReference = useMemo(() => {
    if (!currentPost) return false;
    return (
      currentPost.source_type === 'twitter' ||
      !!currentPost.tweet?.tweet_id 
    );
  }, [currentPost]);

  const hasLinkReferences = useMemo(() => {
    if (!currentPost) return false;
    return (
      !!currentPost.urls?.length || // Check if there are URLs in the post
      currentPost.content?.includes('](') || // Markdown link syntax
      currentPost.content?.includes('<a href') // HTML link syntax
    );
  }, [currentPost]);

  return (
    <div className="sticky top-0 z-10 bg-white dark:bg-gray-800 border-b dark:border-gray-700">
      <div className="max-w-xl mx-auto px-4">
        <div className="flex items-center py-2 justify-evenly">
          {/* Left group */}
          <div className="flex items-center gap-3">
            <Tippy content="Undo (Ctrl+Z)">
              <button onClick={handleUndo}
                className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
                <Undo className="w-4 h-4" />
              </button>
            </Tippy>
            <Tippy content="Redo (Ctrl+Y)">
              <button onClick={handleRedo}
                className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
                <Redo className="w-4 h-4" />
              </button>
            </Tippy>
          </div>
          <div className="h-6 w-px bg-gray-200 dark:bg-gray-700" />
          {/* Center group */}
          <div className="flex items-center gap-3">
            {/* New Copy Content button */}
            <Tippy content="Copy Content with formatting">
              <button onClick={handleCopy}
                className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
                <Copy className="w-4 h-4" />
              </button>
            </Tippy>
            {selectedTab !== 'blog' && (
              <Tippy content={isGenerateDisabled ? 'Content already exists' : `Generate ${selectedTab} post`}>
                <button
                  onClick={async () => {
                    setIsGenerating(true);
                    try {
                      await generatePost([selectedTab], currentPost?.thread_id!);
                      await fetchContentByThreadId(currentPost?.thread_id!, selectedTab);
                      toast.success(`${selectedTab} post generated successfully`);
                    } catch (error) {
                      toast.error('Generation failed');
                    } finally {
                      setIsGenerating(false);
                    }
                  }}
                  disabled={isGenerateDisabled || isGenerating}
                  className={`p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 
                    ${(isGenerateDisabled || isGenerating) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                >
                  <Rocket className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
                </button>
              </Tippy>
            )}
            {shouldShowFeedback && (
              <Tippy content="Provide feedback">
                <button onClick={() => setShowFeedbackModal(true)}
                  className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
                  <MessageSquare className="w-4 h-4" />
                </button>
              </Tippy>
            )}
            <Tippy content="Version History">
              <button onClick={() => toast('History feature coming soon')}
                className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
                <History className="w-4 h-4" />
              </button>
            </Tippy>
          </div>
          <div className="h-6 w-px bg-gray-200 dark:bg-gray-700" />
          {/* Right group */}
          <div className="flex items-center gap-3">
            <Tippy content="Settings">
              <button onClick={() => toast('Settings feature coming soon')}
                className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
                <Settings className="w-4 h-4" />
              </button>
            </Tippy>
            <Tippy content="Help">
              <button onClick={() => toast('Help feature coming soon')}
                className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
                <HelpCircle className="w-4 h-4" />
              </button>
            </Tippy>
          </div>
        </div>
      </div>

      {/* Modals */}
      {showFeedbackModal && (
        <FeedbackModal
          feedback={feedback}
          setFeedback={setFeedback}
          handleFeedbackSubmit={handleFeedbackSubmit}
          setShowFeedbackModal={setShowFeedbackModal}
        />
      )}
      
      <UrlPicker
        isOpen={showUrlPicker}
        onClose={() => setShowUrlPicker(false)}
        urls={currentPost?.urls || []}
        onSelect={handleUrlSelect}
      />
    </div>
  );
};
