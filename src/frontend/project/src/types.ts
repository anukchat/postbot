export interface Media {
  id?: string;
  url: string;
  type: 'image' | 'video' | 'gif';
  title?: string;
  alt_text?: string;
  width?: number;
  height?: number;
  duration?: number;
  thumbnail_url?: string;
  original_url?: string;
  final_url?: string;
  size?: number;
  mime_type?: string;
  is_selected?: boolean;
  created_at?: string;
}

export interface Url {
  url: string;
  type: string;
  domain: string;
  title?: string;
  description?: string;
  thumbnail?: string;
  original_url: string;
  final_url?: string;
  meta?: {
    og_title?: string;
    og_description?: string;
    og_image?: string;
    og_site_name?: string;
    twitter_card?: string;
    twitter_image?: string;
  };
  is_selected?: boolean;
}

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
  source_identifier: string;
  thread_id: string;
  title: string;
  content: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  status: 'Draft' | 'Published' | 'Scheduled' | 'Archived' | 'Rejected' | 'Deleted';
  twitter_post?: string;
  linkedin_post?: string;
  source_type?: 'web_url' | 'twitter' | 'rss' | 'manual';
  blog_category?: string;
  tweet?: {
    tweet_id: string;
    full_text: string;
    created_at: string;
    screen_name: string;
    user_name: string;
  };
  urls: Url[];
  media: Media[];
  metadata?: PostMetadata;
  selected_media?: string[]; // Array of media IDs that are used in the post
}

export interface Node {
  id: string;
  type: 'post' | 'note';
  title: string;
  content: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
}

export interface Connection {
  id: string;
  sourceId: string;
  targetId: string;
}

export interface SlashCommand {
  id: string;
  title: string;
  description: string;
  icon?: React.ReactNode;
  action: () => string;
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
  status: 'Draft' | 'Published' | 'Scheduled' | 'Archived' | 'Rejected' | 'Deleted';
  url: string;
}


export interface Source {

  source_id: string;
  source_identifier: string;
  type: 'twitter' | 'web_url';
  metadata?: any;
  created_at: string;
  preview?: {
    title: string;
    description: string;
    image?: string;
  };
  existing_blog?: {
    thread_id: string;
    title: string;
  };
}
