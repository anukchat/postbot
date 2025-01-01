import React, { useState, useEffect } from 'react';
import { BrainCircuit } from 'lucide-react';

const funnyMessages = [
  "Teaching AI to be funny... 🤔",
  "Brainstorming with digital neurons... 🧠",
  "Converting coffee into content... ☕",
  "Unleashing creative chaos... 🎨",
  "Making your content go viral... 🚀",
  "Sprinkling social media magic... ✨",
  "Crafting the perfect post... 📝",
  "Training pigeons to deliver tweets... 🐦",
  "Consulting the meme lords... 😎",
  "Channeling Shakespeare... but cooler 🎭",
  "Mining for engagement gold... ⭐",
  "Loading personality module... 🤖",
  "Charging creative batteries... 🔋",
  "Brewing engagement potion... 🧪",
  "Summoning viral potential... 🔮"
];

interface GenerateLoaderProps {
  platform: 'twitter' | 'linkedin';
}

export const GenerateLoader: React.FC<GenerateLoaderProps> = ({ platform }) => {
  const [message, setMessage] = useState(funnyMessages[0]);

  useEffect(() => {
    const interval = setInterval(() => {
      const randomIndex = Math.floor(Math.random() * funnyMessages.length);
      setMessage(funnyMessages[randomIndex]);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-xl max-w-md w-full mx-4">
        <div className="flex flex-col items-center space-y-4">
          <BrainCircuit className="w-12 h-12 text-blue-500 animate-pulse" />
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            Generating {platform === 'twitter' ? 'Tweet' : 'LinkedIn Post'}
          </h3>
          <p className="text-gray-500 dark:text-gray-300 text-center animate-fade-in">
            {message}
          </p>
        </div>
      </div>
    </div>
  );
};
