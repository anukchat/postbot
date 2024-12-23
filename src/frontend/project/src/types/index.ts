export interface Post {
  id: string;
  title: string;
  content: string;
  status: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  blog_category?: string; // Add blog_category (optional)
  tweet?: any; // Add tweet (optional, type as needed)
  urls?: { original_url: string }[]; // Add urls (optional, type as needed)
  media?: { final_url: string }[]; // Add media (optional, type as needed)
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