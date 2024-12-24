export interface PostMetadata {
  blogpost: boolean;
  category: string;
  date: string;
  author: string;
  tags: string[];
  language: string;
  excerpt?: string;
}

export interface Post {
  id: string;
  title: string;
  content: string;
  blog_category: string[];
  tags: string[];
  createdAt: string;
  updatedAt: string;
  status: string;
  twitter_post?: string;
  linkedin_post?: string;
  tweet?: {
    tweet_id: string;
    full_text: string;
    created_at: string;
    screen_name: string;
    user_name: string;
  };
  urls?: Array<{
    original_url: string;
    type: string;
    domain: string;
  }>;
  media?: Array<{
    original_url: string;
    type: string;
  }>;
}

export interface SlashCommand {
  id: string;
  title: string;
  description: string;
  icon?: React.ReactNode;
  action: () => string;  // Changed to return string
}

export interface Position {
  x: number;
  y: number;
}

export interface ScrollPosition {
  x: number;
  y: number;
}

export interface EmbedType {
  type: 'twitter' | 'image' | 'video';
  url: string;
}

export interface BlogStatus {
  status: 'Draft'| 'Published'| 'Scheduled'| 'Archived'| 'Rejected' | 'Deleted';
  url: string;
}

