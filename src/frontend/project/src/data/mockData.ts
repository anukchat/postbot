import { Post } from '../types';

export const mockPosts: Post[] = [
  {
    id: '1',
    title: 'Getting Started with Markdown',
    content: '# Welcome to Markdown\n\nThis is a sample document showing basic Markdown syntax:\n\n## Headers\n\n## Lists\n- Item 1\n- Item 2\n\n## Code\n```js\nconsole.log("Hello!");\n```',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    title: 'Project Notes',
    content: '## Project Overview\n\nKey points:\n- Feature A\n- Feature B\n\n### Timeline\n1. Phase 1\n2. Phase 2',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];