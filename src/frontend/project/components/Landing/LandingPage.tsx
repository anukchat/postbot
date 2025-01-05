import React, { useState } from 'react';
import { ArrowRight, Bot, Sparkles, Twitter, Brain, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import { Navbar } from './Navbar';
import { useAuth } from '../../contexts/AuthContext';

const LandingPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const { signIn } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // You'll need to add magic link signin to your AuthContext
      await signIn('magic-link', { email });
      // Show success message
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <>
      <Navbar />
      <div className="min-h-screen pt-28 bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
        {/* Hero Section */}
        <section className="px-4 py-20 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-5xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-6xl md:text-7xl">
              Transform your <span className="text-blue-600">tweets</span> into 
              <span className="text-blue-600"> engaging blogs</span>
            </h1>
            <p className="mt-6 text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              PostBot helps you turn your Twitter threads into well-structured blog posts using AI. Save time and reach a wider audience.
            </p>
            <div className="mt-10">
              <motion.a
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                href="/app"
                className="inline-flex items-center px-8 py-3 text-lg font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700"
              >
                Get Started Free
                <ArrowRight className="ml-2" />
              </motion.a>
            </div>
          </motion.div>
        </section>

        {/* Features Grid */}
        <section className="py-20 bg-white dark:bg-gray-800">
          <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white sm:text-4xl">
                Everything you need to create amazing content
              </h2>
            </div>
            <div className="grid grid-cols-1 gap-12 mt-12 sm:grid-cols-2 lg:grid-cols-3">
              {[
                {
                  icon: <Bot className="w-8 h-8 text-blue-500" />,
                  title: "AI-Powered Conversion",
                  description: "Automatically convert your Twitter threads into well-structured blog posts"
                },
                {
                  icon: <Sparkles className="w-8 h-8 text-blue-500" />,
                  title: "Smart Formatting",
                  description: "Maintain your writing style while improving structure and readability"
                },
                {
                  icon: <Twitter className="w-8 h-8 text-blue-500" />,
                  title: "Twitter Integration",
                  description: "Seamlessly import your Twitter threads and media content"
                },
                {
                  icon: <Brain className="w-8 h-8 text-blue-500" />,
                  title: "Content Enhancement",
                  description: "AI suggestions to improve your content and engagement"
                },
                {
                  icon: <Zap className="w-8 h-8 text-blue-500" />,
                  title: "Quick Publishing",
                  description: "Publish to your blog platform with one click"
                }
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-8 bg-gray-50 dark:bg-gray-700 rounded-2xl"
                >
                  <div className="flex items-center justify-center w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-xl">
                    {feature.icon}
                  </div>
                  <h3 className="mt-4 text-xl font-medium text-gray-900 dark:text-white">
                    {feature.title}
                  </h3>
                  <p className="mt-2 text-gray-600 dark:text-gray-300">
                    {feature.description}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-blue-600">
          <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-white sm:text-4xl">
                Ready to transform your content?
              </h2>
              <p className="mt-4 text-xl text-blue-100">
                Join thousands of content creators who are saving time and reaching more readers.
              </p>
              <motion.a
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                href="/app"
                className="inline-flex items-center px-8 py-3 mt-8 text-lg font-medium text-blue-600 bg-white rounded-lg hover:bg-gray-50"
              >
                Start Creating Now
                <ArrowRight className="ml-2" />
              </motion.a>
            </div>
          </div>
        </section>

        {/* Email Signup Section */}
        <section className="py-20 bg-gray-50 dark:bg-gray-900">
          <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white sm:text-4xl">
                Stay Updated
              </h2>
              <p className="mt-4 text-xl text-gray-600 dark:text-gray-300">
                Sign up with your email to receive the latest updates and features.
              </p>
              <form onSubmit={handleSubmit} className="max-w-md mx-auto mt-8">
                <div className="flex gap-2">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    className="flex-1 px-4 py-2 rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                    required
                  />
                  <button
                    type="submit"
                    className="bg-blue-500 text-white px-6 py-2 rounded-md hover:bg-blue-600"
                  >
                    Sign Up
                  </button>
                </div>
              </form>
            </div>
          </div>
        </section>
      </div>
    </>
  );
};

export default LandingPage;
