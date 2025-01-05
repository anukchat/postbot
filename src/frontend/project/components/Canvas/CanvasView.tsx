import React from 'react';
import { useEditorStore } from '../../store/editorStore';
import { Bar } from 'react-chartjs-2';
import { TagCloud } from 'react-tagcloud';
import { Tooltip } from 'react-tooltip';

import 'chart.js/auto';
import 'react-tooltip/dist/react-tooltip.css';

export const CanvasView: React.FC = () => {
  const { posts } = useEditorStore();

  // Calculate statistics
  const publishedCount = posts.filter(post => post.status.toLowerCase() === 'published').length;
  const draftCount = posts.filter(post => post.status.toLowerCase() === 'draft').length;

  // Prepare data for charts
  const postsByDate = posts.reduce((acc, post) => {
    const date = new Date(post.createdAt).toLocaleDateString();
    acc[date] = (acc[date] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const chartData = {
    labels: Object.keys(postsByDate),
    datasets: [
      {
        label: 'Number of Posts',
        data: Object.values(postsByDate),
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  const tagCounts = posts.flatMap(post => post.tags || []).reduce((acc, tag) => {
    acc[tag] = (acc[tag] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  const tagCloudData = Object.entries(tagCounts).map(([tag, count]) => ({
    value: tag,
    count,
  }));

  return (
    <div className="overflow-auto h-screen p-6 bg-gray-100 dark:bg-gray-900">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-200 mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300">Published Posts</h2>
          <p className="text-3xl font-bold text-green-500">{publishedCount}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300">Draft Posts</h2>
          <p className="text-3xl font-bold text-yellow-500">{draftCount}</p>
        </div>
      </div>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow mb-6">
        <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-300 mb-4">Posts Over Time</h2>
        <Bar data={chartData} />
      </div>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow mb-6">
        <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-300 mb-4">Tag Cloud</h2>
        <TagCloud
          minSize={12}
          maxSize={35}
          tags={tagCloudData}
          className="w-full h-full"
          renderer={(tag, size, color) => (
            <span
              key={tag.value}
              className="inline-block m-2"
              style={{
                fontSize: `${size}px`,
                color: color,
                cursor: 'pointer',
              }}
              data-tooltip-id="tag-tooltip"
              data-tooltip-content={`Tag: ${tag.value}\nPosts: ${tag.count}`}
            >
              {tag.value}
            </span>
          )}
        />
        <Tooltip
          id="tag-tooltip"
          place="top"
          variant="dark"
        />
      </div>
    </div>
  );
};