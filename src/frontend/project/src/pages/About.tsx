import React from 'react';
import { Navbar } from '../components/Landing/Navbar';
import { Bot, Users, Code, Globe } from 'lucide-react';

const About: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h1 className="text-4xl font-bold mb-4">About PostBot</h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              We're building the future of content creation, helping creators transform their social media presence into lasting, meaningful content.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg">
              <Bot className="w-12 h-12 text-blue-500 mb-4" />
              <h2 className="text-2xl font-bold mb-4">Our Mission</h2>
              <p className="text-gray-600 dark:text-gray-300">
                To empower content creators by providing intelligent tools that transform casual social media conversations into professional blog content.
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg">
              <Users className="w-12 h-12 text-blue-500 mb-4" />
              <h2 className="text-2xl font-bold mb-4">Our Team</h2>
              <p className="text-gray-600 dark:text-gray-300">
                A passionate group of developers, designers, and content creators working together to build the best content creation tools.
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg">
              <Code className="w-12 h-12 text-blue-500 mb-4" />
              <h2 className="text-2xl font-bold mb-4">Technology</h2>
              <p className="text-gray-600 dark:text-gray-300">
                Built with cutting-edge AI and modern web technologies to provide a seamless content creation experience.
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg">
              <Globe className="w-12 h-12 text-blue-500 mb-4" />
              <h2 className="text-2xl font-bold mb-4">Global Reach</h2>
              <p className="text-gray-600 dark:text-gray-300">
                Supporting content creators worldwide in their journey to reach broader audiences through quality content.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;
