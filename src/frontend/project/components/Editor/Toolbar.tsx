import React, { useState } from 'react';
import { Image, Link, Video, Quote, ListOrdered, List, Hash, Twitter, Code, Code2, Table, Check, Heading1, Heading2, Heading3, FileText, Undo, Redo, Tags, Bold, Italic, Strikethrough, Rocket, MessageSquare } from 'lucide-react';
import 'tippy.js/dist/tippy.css';
import Tippy from '@tippyjs/react';
import { useEditorStore } from '../../store/editorStore';
import { GenerateLoader } from './GenerateLoader';
import { ImagePicker } from './ImagePicker';
import { VideoPicker } from './VideoPicker';
import { UrlPicker } from './UrlPicker';
import { Media, Url } from '../../types';
import { FeedbackModal } from '../Modals/FeedbackModal';
import { toast } from 'react-hot-toast';

interface ToolbarProps {
  onCommandInsert: (commandText: string, replaceLength: number) => void;
  selectedTab: 'blog' | 'twitter' | 'linkedin'; // Add selectedTab prop
}

export const Toolbar: React.FC<ToolbarProps> = ({ onCommandInsert, selectedTab }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [showMediaPicker, setShowMediaPicker] = useState(false);
  const [mediaType, setMediaType] = useState<'image' | 'video' | null>(null);
  const [showUrlPicker, setShowUrlPicker] = useState(false);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedback, setFeedback] = useState('');
  const { currentPost, undo, redo, generatePost, fetchContentByThreadId } = useEditorStore();

  const getTwitterEmbed = () => {
    if (currentPost?.source_type === 'twitter' && currentPost?.source_identifier) {
      return `{{< twitter id="${currentPost.source_identifier}" >}}\n`;
    }
    return currentPost?.tweet?.tweet_id
      ? `{{< twitter id="${currentPost.tweet.tweet_id}" >}}\n`
      : '{{< twitter id="PASTE_TWEET_ID_HERE" >}}\n';
  };


  const getBlogMetadata = () => {
    if (!currentPost) {
      return '';
    }
    const date = new Date(currentPost.createdAt);
    const formattedDate = date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
    return `---\nblogpost: true\ncategory: LLM\ndate: ${formattedDate} \nauthor: Anukool Chaturvedi\ntags: ${currentPost.tags.join(', ')} \nlanguage: English\nexcerpt: 1\n---`;
  }
  // # Add for Tags
  const getTags = () => {
    return currentPost?.tags
      ? `tags: [${currentPost.tags.map((tag: string) => `"${tag}"`).join(', ')}]`
      : 'tags: []';
  };

  const iconColor = (condition: boolean) => (condition ? 'text-green-500' : '');

  const handleGenerate = async () => {
    if (!currentPost?.thread_id) return;
    setIsGenerating(true);
    try {
      await generatePost([selectedTab], currentPost.thread_id);
      // Refresh content after generation
      await fetchContentByThreadId(currentPost.thread_id, selectedTab);
    } catch (err: any) {
      console.error(err);
      if (
        err.response?.status === 403 &&
        err.response?.data?.detail?.includes("Generation limit reached")
      ) {
        toast.error('User has exceeded the generation limit');
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleMediaSelect = (media: Media) => {
    let insertText = '';
    if (media.type === 'image') {
      insertText = `![${media.alt_text || ''}](${media.url})`;
    } else if (media.type === 'video') {
      insertText = `<video src="${media.url}" ${media.thumbnail_url ? `poster="${media.thumbnail_url}"` : ''} controls></video>`;
    }
    onCommandInsert(insertText, 0);
    setShowMediaPicker(false);
  };

  const handleUrlSelect = (url: Url) => {
    const insertText = `[${url.url}](${url.url})`;
    onCommandInsert(insertText, 0);
    setShowUrlPicker(false);
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
    } finally {
      setIsGenerating(false);
    }
  };

  const isGenerateDisabled: boolean = selectedTab === 'blog' ||
    (selectedTab === 'twitter' && !!currentPost?.twitter_post) ||
    (selectedTab === 'linkedin' && !!currentPost?.linkedin_post);

  const shouldShowFeedback = currentPost && (
    (selectedTab === 'blog' && currentPost.content) ||
    (selectedTab === 'twitter' && currentPost.twitter_post) ||
    (selectedTab === 'linkedin' && currentPost.linkedin_post)
  );

  return (
    <>
      <div className="sticky top-0 z-10 flex flex-wrap gap-1 sm:gap-2 md:gap-4 p-2 sm:p-4 bg-white dark:bg-gray-800 shadow-lg rounded-lg">
        <div className="flex flex-wrap gap-0.5 sm:gap-1 md:gap-2 items-center justify-center w-full sm:w-auto">
          {/* Group common actions */}
          <div className="flex gap-0.5 sm:gap-1 items-center">
            <Tippy content="Undo">
              <button onClick={() => undo(selectedTab)} className="p-1 sm:p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                <Undo className="w-3 h-3 sm:w-4 sm:h-4" />
              </button>
            </Tippy>
            <Tippy content="Redo"><button onClick={() => redo(selectedTab)} className="p-1 sm:p-1.5"><Redo className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
            <Tippy content="Heading 1"><button onClick={() => onCommandInsert('# ', 0)} className="p-1 sm:p-1.5"><Heading1 className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
            <Tippy content="Heading 2"><button onClick={() => onCommandInsert('## ', 0)} className="p-1 sm:p-1.5"><Heading2 className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
            <Tippy content="Heading 3"><button onClick={() => onCommandInsert('### ', 0)} className="p-1 sm:p-1.5"><Heading3 className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
          </div>

          {/* Group formatting actions */}
          <div className="flex gap-0.5 sm:gap-1 items-center">
            <Tippy content="Bold"><button onClick={() => onCommandInsert('**', 0)} className="p-1 sm:p-1.5"><Bold className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
            <Tippy content="Italic"><button onClick={() => onCommandInsert('*', 0)} className="p-1 sm:p-1.5"><Italic className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
            <Tippy content="Strikethrough"><button onClick={() => onCommandInsert('~~', 0)} className="p-1 sm:p-1.5"><Strikethrough className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
            <Tippy content="Twitter Embed"><button onClick={() => onCommandInsert(getTwitterEmbed(), 0)} className="p-1 sm:p-1.5"><Twitter className={`w-3 h-3 sm:w-4 sm:h-4 ${iconColor(currentPost?.source_type === 'twitter')}`} /></button></Tippy>
            <Tippy content="Link"><button onClick={() => setShowUrlPicker(true)} className="p-1 sm:p-1.5"><Link className={`w-3 h-3 sm:w-4 sm:h-4 ${iconColor(!!currentPost?.urls?.length)}`} /></button></Tippy>
            <Tippy content="Quote"><button onClick={() => onCommandInsert('> ', 0)} className="p-1 sm:p-1.5"><Quote className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
            <Tippy content="Code Block"><button onClick={() => onCommandInsert('```\n\n```', 0)} className="p-1 sm:p-1.5"><Code className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
            <Tippy content="Inline Code"><button onClick={() => onCommandInsert('`', 0)} className="p-1 sm:p-1.5"><Code2 className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
            <Tippy content="Table"><button onClick={() => onCommandInsert('| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |\n', 0)} className="p-1 sm:p-1.5"><Table className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
            <Tippy content="Checklist"><button onClick={() => onCommandInsert('- [ ] ', 0)} className="p-1 sm:p-1.5"><Check className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
            <Tippy content="Ordered List"><button onClick={() => onCommandInsert('1. ', 0)} className="p-1 sm:p-1.5"><ListOrdered className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
            <Tippy content="Unordered List"><button onClick={() => onCommandInsert('- ', 0)} className="p-1 sm:p-1.5"><List className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
            <Tippy content="Horizontal Rule"><button onClick={() => onCommandInsert('---\n', 0)} className="p-1 sm:p-1.5"><FileText className="w-3 h-3 sm:w-4 sm:h-4" /></button></Tippy>
            <Tippy content="Tags"><button onClick={() => onCommandInsert(getTags(), 0)} className="p-1 sm:p-1.5"><Hash className={`w-3 h-3 sm:w-4 sm:h-4 ${iconColor(!!currentPost?.tags?.length)}`} /></button></Tippy>
          </div>

          {/* Group special actions */}
          <div className="flex gap-0.5 sm:gap-1 items-center">
            <Tippy content="Blog metadata"><button onClick={() => onCommandInsert(getBlogMetadata(), 0)} className="p-1 sm:p-1.5"><Tags className="w-3 h-3 sm:w-4 sm:h-4 text-green-500" /></button></Tippy>
            <div className="flex gap-2 items-center">
              <div className="flex gap-5">
                <Tippy content={currentPost?.media?.some(m => m.type === 'image') ? "Choose Image" : "Insert Blank Image"}>
                  <button onClick={() => {
                    const hasImages = currentPost?.media?.some(m => m.type === 'image');
                    if (!hasImages) {
                      onCommandInsert('![]()\n', 0);
                    } else {
                      setMediaType('image');
                      setShowMediaPicker(true);
                    }
                  }} className="p-1 sm:p-1.5">
                    <Image className={`w-3 h-3 sm:w-4 sm:h-4 ${iconColor(!!currentPost?.media?.some(m => m.type === 'image'))}`} />
                  </button>
                </Tippy>
                <Tippy content={currentPost?.media?.some(m => m.type === 'video') ? "Choose Video" : "Insert Blank Video"}>
                  <button onClick={() => {
                    const hasVideos = currentPost?.media?.some(m => m.type === 'video');
                    if (!hasVideos) {
                      onCommandInsert('<video src="PASTE_VIDEO_URL_HERE" controls></video>\n', 0);
                    } else {
                      setMediaType('video');
                      setShowMediaPicker(true);
                    }
                  }} className="p-1 sm:p-1.5">
                    <Video className={`w-3 h-3 sm:w-4 sm:h-4 ${iconColor(!!currentPost?.media?.some(m => m.type === 'video'))}`} />
                  </button>
                </Tippy>
                {selectedTab !== 'blog' && (
                  <Tippy content={isGenerateDisabled ? 'Content already exists' : `Generate ${selectedTab} post`}>
                    <button
                      onClick={handleGenerate}
                      disabled={isGenerateDisabled || isGenerating}
                      className={`rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors ${isGenerateDisabled || isGenerating ? 'opacity-50 cursor-not-allowed' : ''
                        } p-1 sm:p-1.5`}
                    >
                      <Rocket className={`w-3 h-3 sm:w-4 sm:h-4 ${isGenerating ? 'animate-bounce' : ''}`} />
                    </button>
                  </Tippy>
                )}
                {shouldShowFeedback && (
                  <Tippy content="Provide feedback">
                    <button
                      onClick={() => setShowFeedbackModal(true)}
                      className="hover:bg-gray-100 dark:hover:bg-gray-700 p-1 sm:p-1.5 rounded-lg"
                    >
                      <MessageSquare className="w-3 h-3 sm:w-4 sm:h-4" />
                    </button>
                  </Tippy>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      {showMediaPicker && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 max-w-2xl max-h-[80vh] overflow-auto">
            {mediaType === 'image' ? (
              <ImagePicker
                media={currentPost?.media.filter(m => m.type === 'image') || []}
                onSelect={handleMediaSelect}
                onClose={() => setShowMediaPicker(false)}
              />
            ) : (
              <VideoPicker
                media={currentPost?.media.filter(m => m.type === 'video') || []}
                onSelect={handleMediaSelect}
                onClose={() => setShowMediaPicker(false)}
              />
            )}
          </div>
        </div>
      )}
      <UrlPicker
        isOpen={showUrlPicker}
        onClose={() => setShowUrlPicker(false)}
        urls={currentPost?.urls || []}
        onSelect={handleUrlSelect}
      />
      {showFeedbackModal && (
        <FeedbackModal
          feedback={feedback}
          setFeedback={setFeedback}
          handleFeedbackSubmit={handleFeedbackSubmit}
          setShowFeedbackModal={setShowFeedbackModal}
        />
      )}
      {isGenerating && (
        <GenerateLoader platform={selectedTab as 'twitter' | 'linkedin'} />
      )}
    </>
  );
};
