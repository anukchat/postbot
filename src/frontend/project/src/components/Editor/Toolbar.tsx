import React from 'react';
import { Image, Link, Video, Quote, ListOrdered, List, Hash, Twitter, Code,Code2, Table, Check, Heading1, Heading2, Heading3, FileText, Undo, Redo, Tags, Bold, Italic, Strikethrough } from 'lucide-react';
import 'tippy.js/dist/tippy.css';
import Tippy from '@tippyjs/react';
import { useEditorStore } from '../../store/editorStore';

interface ToolbarProps {
  onCommandInsert: (commandText: string, replaceLength: number) => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({ onCommandInsert }) => {
  const { currentPost, undo, redo } = useEditorStore();

  const getTwitterEmbed = () => {
    return currentPost?.tweet?.tweet_id
      ? `{{< twitter id="${currentPost.tweet.tweet_id}" >}}\n`
      : '{{< twitter id="PASTE_TWEET_ID_HERE" >}}\n';
  };

  const getImageEmbed = () => {
    return currentPost?.media?.[0]?.type === 'photo'
        ? `![](${currentPost.media[0].original_url})\n`
        : '![]()\n';
    };

  const getLinkEmbed = () => {
    return currentPost?.urls?.[0]?.original_url
      ? `[${currentPost.urls[0].original_url}](${currentPost.urls[0].original_url})`
      : '[]()';
  };

  const getVideoEmbed = () => {
    return currentPost?.media?.[0]?.type === 'video'
      ? `<video src="${currentPost.media[0].original_url}" controls></video>\n`
      : '<video src="PASTE_VIDEO_URL_HERE" controls></video>\n';
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

  return (
    <div className="sticky top-0 z-10 flex gap-6 p-4 bg-white dark:bg-gray-800 shadow-lg rounded-lg">
      <Tippy content="Undo"><button onClick={undo}><Undo className="w-4 h-4" /></button></Tippy>
      <Tippy content="Redo"><button onClick={redo}><Redo className="w-4 h-4" /></button></Tippy>
      <Tippy content="Heading 1"><button onClick={() => onCommandInsert('# ', 0)}><Heading1 className="w-6 h-6" /></button></Tippy>
      <Tippy content="Heading 2"><button onClick={() => onCommandInsert('## ', 0)}><Heading2 className="w-5 h-5" /></button></Tippy>
      <Tippy content="Heading 3"><button onClick={() => onCommandInsert('### ', 0)}><Heading3 className="w-4 h-4" /></button></Tippy>
      <Tippy content="Bold"><button onClick={() => onCommandInsert('**', 0)}><Bold className="w-4 h-4" /></button></Tippy>
      <Tippy content="Italic"><button onClick={() => onCommandInsert('*', 0)}><Italic className="w-4 h-4" /></button></Tippy>
      <Tippy content="Strikethrough"><button onClick={() => onCommandInsert('~~', 0)}><Strikethrough className="w-4 h-4" /></button></Tippy>
      <Tippy content="Twitter Embed"><button onClick={() => onCommandInsert(getTwitterEmbed(), 0)}><Twitter className={`w-5 h-5 ${iconColor(!!currentPost?.tweet?.tweet_id)}`} /></button></Tippy>
      <Tippy content="Image"><button onClick={() => onCommandInsert(getImageEmbed(), 0)}><Image className={`w-5 h-5 ${iconColor(!!(currentPost?.media?.[0]?.type === 'photo'))}`} /></button></Tippy>
      <Tippy content="Link"><button onClick={() => onCommandInsert(getLinkEmbed(), 0)}><Link className="w-5 h-5" /></button></Tippy>
      <Tippy content="Quote"><button onClick={() => onCommandInsert('> ', 0)}><Quote className="w-4 h-4" /></button></Tippy>
      <Tippy content="Code Block"><button onClick={() => onCommandInsert('```\n\n```', 0)}><Code className="w-5 h-5" /></button></Tippy>
      <Tippy content="Inline Code"><button onClick={() => onCommandInsert('`', 0)}><Code2 className="w-5 h-5" /></button></Tippy>
      <Tippy content="Table"><button onClick={() => onCommandInsert('| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |\n', 0)}><Table className="w-5 h-5" /></button></Tippy>
      <Tippy content="Checklist"><button onClick={() => onCommandInsert('- [ ] ', 0)}><Check className="w-5 h-5" /></button></Tippy>
      <Tippy content="Ordered List"><button onClick={() => onCommandInsert('1. ', 0)}><ListOrdered className="w-5 h-5" /></button></Tippy>
      <Tippy content="Unordered List"><button onClick={() => onCommandInsert('- ', 0)}><List className="w-5 h-5" /></button></Tippy>
      <Tippy content="Horizontal Rule"><button onClick={() => onCommandInsert('---\n', 0)}><FileText className="w-5 h-5" /></button></Tippy>
      <Tippy content="Tags"><button onClick={() => onCommandInsert(getTags(), 0)}><Hash className={`w-5 h-5 ${iconColor(!!currentPost?.tags?.length)}`} /></button></Tippy>
      <Tippy content="Video"><button onClick={() => onCommandInsert(getVideoEmbed(), 0)}><Video className={`w-5 h-5 ${iconColor(currentPost?.media?.[0]?.type === 'video')}`} /></button></Tippy>
      <Tippy content="Blog metadata"><button onClick={() => onCommandInsert(getBlogMetadata(), 0)}><Tags className="w-5 h-5 text-green-500" /></button></Tippy>
    </div>
  );
};
