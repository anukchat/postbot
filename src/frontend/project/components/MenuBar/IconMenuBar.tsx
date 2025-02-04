import React, { useState } from 'react';
import { 
  MessageSquare, 
  Settings, 
  History, 
  HelpCircle, 
  Rocket, 
  Share2, 
  FileDown, 
  Save,
  Send,
  Twitter,
  Link,
  Undo,
  Redo
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
  const { currentPost, savePost, downloadMarkdown, publishPost, generatePost, fetchContentByThreadId, undo, redo } = useEditorStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [showUrlPicker, setShowUrlPicker] = useState(false);

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

  const getTwitterEmbed = () => {
    if (currentPost?.source_type === 'twitter' && currentPost?.source_identifier) {
      return `{{< twitter id="${currentPost.source_identifier}" >}}\n`;
    }
    return currentPost?.tweet?.tweet_id
      ? `{{< twitter id="${currentPost.tweet.tweet_id}" >}}\n`
      : '{{< twitter id="PASTE_TWEET_ID_HERE" >}}\n';
  };

  const handleUrlSelect = (url: { url: string }) => {
    const insertText = `[${url.url}](${url.url})`;
    onCommandInsert?.(insertText, 0);
    setShowUrlPicker(false);
  };

  return (
    <div className="sticky top-0 z-10 bg-white dark:bg-gray-800 border-b dark:border-gray-700">
      <div className="max-w-xl mx-auto px-4">
        <div className="flex items-center py-2 justify-evenly">
          {/* Left group */}
          <div className="flex items-center gap-3">
            <Tippy content="Undo">
              <button onClick={() => undo(selectedTab)} 
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
            <Undo className="w-4 h-4" />
              </button>
            </Tippy>
            <Tippy content="Redo">
              <button onClick={() => redo(selectedTab)}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
            <Redo className="w-4 h-4" />
              </button>
            </Tippy>
            <Tippy content="Save">
              <button onClick={savePost}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
            <Save className="w-4 h-4" />
              </button>
            </Tippy>
            <Tippy content="Download">
              <button onClick={downloadMarkdown}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
            <FileDown className="w-4 h-4" />
              </button>
            </Tippy>
          </div>
          <div className="h-6 w-px bg-gray-200 dark:bg-gray-700" />
          {/* Center group */}
          <div className="flex items-center gap-3">
            <Tippy content="Twitter Embed">
              <button onClick={() => onCommandInsert?.(getTwitterEmbed(), 0)}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
            <Twitter className="w-4 h-4" />
              </button>
            </Tippy>
            <Tippy content="Insert Link">
              <button onClick={() => setShowUrlPicker(true)}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
            <Link className="w-4 h-4" />
              </button>
            </Tippy>
            <Tippy content="Version History">
              <button onClick={() => toast('History feature coming soon')}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
            <History className="w-4 h-4" />
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
          </div>
          <div className="h-6 w-px bg-gray-200 dark:bg-gray-700" />
          {/* Right group */}
          <div className="flex items-center gap-3">
            {shouldShowFeedback && (
              <Tippy content="Provide feedback">
            <button onClick={() => setShowFeedbackModal(true)}
              className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
              <MessageSquare className="w-4 h-4" />
            </button>
              </Tippy>
            )}
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
            <Tippy content="Publish">
              <button onClick={publishPost}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
            <Send className="w-4 h-4" />
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
