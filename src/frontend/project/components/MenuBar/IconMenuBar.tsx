import React, { useState, useMemo } from 'react';
import { 
  MessageSquare, 
  Settings, 
  History, 
  HelpCircle, 
  Rocket, 
  Undo,
  Redo,
  Copy,  // new import for copy icon
  Save, 
  FileDown, 
  Send, 
  XCircle,
  Link, // Add Link icon import
  FileText,
  Twitter, // Add FileText icon import
} from 'lucide-react';
import Tippy from '@tippyjs/react';
import 'tippy.js/dist/tippy.css';
import { useEditorStore } from '../../store/editorStore';
import { FeedbackModal } from '../Modals/FeedbackModal';
import { toast } from 'react-hot-toast';

interface IconMenuBarProps {
  selectedTab: 'blog' | 'twitter' | 'linkedin';
  onCommandInsert?: (commandText: string, replaceLength: number) => void;
}

export const IconMenuBar: React.FC<IconMenuBarProps> = ({ selectedTab, onCommandInsert }) => {
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedback, setFeedback] = useState('');
  const { currentPost, generatePost, fetchContentByThreadId, savePost, downloadMarkdown, publishPost, rejectPost } = useEditorStore();
  const [isGenerating, setIsGenerating] = useState(false);

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
    <>
      <div className="fixed top-6 left-1/2 -translate-x-1/2 z-[1000]">
        <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-2">
          {/* Group 1: Edit Actions */}
          <div className="flex items-center gap-2">
            <div className="flex gap-1 p-1 bg-gray-50 dark:bg-gray-700 rounded-md">
              <Tippy content="Undo (Ctrl+Z)">
                <button onClick={handleUndo}
                  className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-600">
                  <Undo className="w-4 h-4" />
                </button>
              </Tippy>
              <Tippy content="Redo (Ctrl+Y)">
                <button onClick={handleRedo}
                  className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-600">
                  <Redo className="w-4 h-4" />
                </button>
              </Tippy>
            </div>

            {/* Group 2: Document Actions */}
            <div className="flex gap-1 p-1 bg-gray-50 dark:bg-gray-700 rounded-md">
              <Tippy content="Save (Ctrl+S)">
                <button onClick={savePost}
                  className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-600">
                  <Save className="w-4 h-4" />
                </button>
              </Tippy>
              <Tippy content="Copy with formatting">
                <button onClick={handleCopy}
                  className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-600">
                  <Copy className="w-4 h-4" />
                </button>
              </Tippy>
              <Tippy content="Download">
                <button onClick={downloadMarkdown}
                  className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-600">
                  <FileDown className="w-4 h-4" />
                </button>
              </Tippy>
            </div>

            {/* Group 3: Generate & Feedback */}
            <div className="flex gap-1 p-1 bg-gray-50 dark:bg-gray-700 rounded-md">
              {!isGenerateDisabled && (
                <Tippy content={`Generate ${selectedTab} post`}>
                  <button onClick={async () => {
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
                    className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-600">
                    <Rocket className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
                  </button>
                </Tippy>
              )}
              {shouldShowFeedback && (
                <Tippy content="Provide feedback">
                  <button onClick={() => setShowFeedbackModal(true)}
                    className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-600">
                    <MessageSquare className="w-4 h-4" />
                  </button>
                </Tippy>
              )}
            </div>

            {/* Group 4: Publish Actions */}
            <div className="flex gap-1 p-1 bg-gray-50 dark:bg-gray-700 rounded-md">
              <Tippy content="Publish">
                <button onClick={publishPost}
                  disabled={currentPost?.status === 'Published'}
                  className="p-1.5 rounded hover:bg-green-100 dark:hover:bg-green-700">
                  <Send className="w-4 h-4 text-green-500" />
                </button>
              </Tippy>
              <Tippy content="Reject">
                <button onClick={rejectPost}
                  disabled={currentPost?.status === 'Rejected'}
                  className="p-1.5 rounded hover:bg-red-100 dark:hover:bg-red-700">
                  <XCircle className="w-4 h-4 text-red-500" />
                </button>
              </Tippy>
            </div>

            {/* Group 5: Help & Settings */}
            <div className="flex gap-1 p-1 bg-gray-50 dark:bg-gray-700 rounded-md">
              <Tippy content="Settings">
                <button className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-600">
                  <Settings className="w-4 h-4" />
                </button>
              </Tippy>
              <Tippy content="Help">
                <button className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-600">
                  <HelpCircle className="w-4 h-4" />
                </button>
              </Tippy>
            </div>
          </div>
        </div>
      </div>

      {/* Add floating tabs on the right side
      <div className="fixed right-4 top-1/2 -translate-y-1/2 z-50">
        <div className="flex flex-col gap-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-2">
          <Tippy content="Blog" placement="left">
            <button
              onClick={() => onCommandInsert?.('blog', 0)}
              className={`p-2 rounded-md ${selectedTab === 'blog' ? 'bg-blue-100 dark:bg-blue-800' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
            >
              <FileText className="w-4 h-4" />
            </button>
          </Tippy>
          <Tippy content="Twitter" placement="left">
            <button
              onClick={() => onCommandInsert?.('twitter', 0)}
              className={`p-2 rounded-md ${selectedTab === 'twitter' ? 'bg-blue-100 dark:bg-blue-800' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
            >
              <Twitter className="w-4 h-4" />
            </button>
          </Tippy>
          <Tippy content="LinkedIn" placement="left">
            <button
              onClick={() => onCommandInsert?.('linkedin', 0)}
              className={`p-2 rounded-md ${selectedTab === 'linkedin' ? 'bg-blue-100 dark:bg-blue-800' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
            >
              <Link className="w-4 h-4" />
            </button>
          </Tippy>
        </div>
      </div> */}

      {/* Existing modals */}
      {showFeedbackModal && (
        <div className="relative z-[9999]">
          <FeedbackModal
            feedback={feedback}
            setFeedback={setFeedback}
            handleFeedbackSubmit={handleFeedbackSubmit}
            setShowFeedbackModal={setShowFeedbackModal}
          />
        </div>
      )}
    </>
  );
};
