import React, { useState } from 'react';
import { ArrowRight, Bot, Share2, Image, FileCode, Share, UserCheck } from 'lucide-react';
import { motion } from 'framer-motion';
import { Navbar } from './Navbar';
import { useAuth } from '../../contexts/AuthContext';
import CTASection from './CTASection';
import EmailSignupSection from './EmailSignupSection';
import Footer from './Footer';

const LandingPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const { signIn } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await signIn('email', { email });
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <>
      <Navbar />
      <div className="min-h-screen pt-48 bg-[#fcfaf5] font-sans"> {/* Changed pt-36 to pt-48 */}
        {/* Hero Section */}
        <section className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center"
          >
        <h1 className="text-5xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-6xl md:text-7xl">
          Transform your <span className="text-blue-600">ideas</span> into 
          <span className="text-blue-600"> engaging content</span>
        </h1>
        <p className="mt-6 text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
          Riteup helps you turn your thoughts into well-structured blog posts using AI. Save time and reach a wider audience.
        </p>

        <div className="mt-10">
          <motion.a
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        href="/dashboard"
        className="inline-flex items-center px-8 py-3 text-lg font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700"
          >
        Get Started Free
        <ArrowRight className="ml-2" />
          </motion.a>
        </div>
          </motion.div>
          {/* Placeholder for Hero Graphics */}
        <motion.div 
        className="mt-12 max-w-4xl mx-auto"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ scale: 1.05 }}
        transition={{ 
          duration: 0.8,
          delay: 0.2,
          ease: "easeOut"
        }}
        >
        <img 
          src="/assets/background_tp.png" 
          alt="Hero Graphic" 
          className="w-full h-auto"
          style={{
          filter: "drop-shadow(0px 10px 20px rgba(0, 0, 0, 0.15))"
          }}
        />
        </motion.div>
        </section>

        {/* Features Grid */}
        <section className="py-20 bg-[#fcfaf5]">
          <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          whileInView={{ opacity: 1, y: 0 }}
          whileHover={{ scale: 1.05 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white sm:text-4xl">
          Everything you need to create amazing content
          </h2>
        </motion.div>
        <div className="grid grid-cols-1 gap-12 sm:grid-cols-2 lg:grid-cols-3">
          {[
          {
          icon: <Bot className="w-8 h-8 text-blue-500" />,
          title: "AI Assisted Content Generation",
          description: "Generate high-quality content with state-of-the-art AI models while maintaining your unique voice"
          },
          {
          icon: <Share className="w-8 h-8 text-blue-500" />,
          title: "Multi-Source Generation",
          description: "Create content from tweets, web URLs, Reddit threads, or custom topics with ease"
          },
          {
          icon: <UserCheck className="w-8 h-8 text-blue-500" />,
          title: "Human-in-the-Loop Validation",
          description: "Review and refine AI-generated content to ensure quality and accuracy"
          },
          {
          icon: <FileCode className="w-8 h-8 text-blue-500" />,
          title: "Markdown Support",
          description: "Edit and export content in Markdown format for maximum flexibility"
          },
          {
          icon: <Image className="w-8 h-8 text-blue-500" />,
          title: "Rich Media Integration",
          description: "Embed images, videos, and other media seamlessly in your content"
          },
          {
          icon: <Share2 className="w-8 h-8 text-blue-500" />,
          title: "Multi-Platform Publishing",
          description: "Publish directly to Twitter, LinkedIn, Medium, or your custom platform"
          }
          ].map((feature, index) => {
          const randomRotation = Math.random() * 6 - 3; // Random rotation between -3 and 3 degrees
          return (
          <motion.div
          key={index}
          initial={{ opacity: 0, y: 50, rotate: randomRotation }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ 
        duration: 0.6,
        delay: index * 0.1,
        type: "spring",
        damping: 12
          }}
          whileHover={{ 
        scale: 1.05,
        rotate: [-2, 2],
        transition: { duration: 0.2, repeat: Infinity, repeatType: "reverse" }
          }}
          className="p-8 bg-yellow-100 rounded-lg shadow-lg transform relative"
          style={{
        clipPath: "polygon(0% 0%, 100% 0%, 100% 95%, 95% 100%, 0% 100%)",
        boxShadow: "2px 3px 10px rgba(0,0,0,0.1), -1px -1px 5px rgba(0,0,0,0.05)"
          }}
          >
          <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-8 h-8 bg-yellow-200 rounded-full opacity-70" />
          <div className="flex items-center justify-center w-12 h-12 bg-white rounded-full mb-4 mx-auto">
        {feature.icon}
          </div>
          <h3 className="text-xl font-handwriting font-bold text-gray-800 text-center">
        {feature.title}
          </h3>
          <p className="mt-2 text-gray-700 font-handwriting text-center">
        {feature.description}
          </p>
          </motion.div>
          )})}
        </div>
          </div>
        </section>

        <CTASection/>

        <EmailSignupSection/>
        <Footer/>
      </div>
    </>
  );
};

export default LandingPage;
