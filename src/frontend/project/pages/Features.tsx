import React from 'react';
import { Navbar } from '../components/Landing/Navbar';
import { Bot, Twitter, Brain, Sparkles, Zap, Share2 } from 'lucide-react';

const Features: React.FC = () => {
  const features = [
    {
      icon: <Bot className="w-12 h-12 text-blue-500" />,
      title: "AI-Powered Conversion",
      description: "Advanced AI algorithms that understand context and maintain your unique voice while converting tweets to blog posts."
    },
    // Add more detailed features...
  ];

  return (
    <div className="min-h-screen bg-[#fcfaf5] dark:bg-gray-900">
      <Navbar />
      <div className="pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold text-center mb-12">Powerful Features for Content Creators</h1>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-300">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Features;
