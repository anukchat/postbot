import React, { useState } from 'react';
import { ArrowRight, Sparkles, Mail, Linkedin, Twitter, Instagram } from 'lucide-react';
import { motion } from 'framer-motion';

const BottomSections = () => {
  const [email, setEmail] = useState('');

  const handleSubmit = (e: { preventDefault: () => void; }) => {
    e.preventDefault();
  };

  return (
    <>
      {/* Email Signup Section with curved transition */}
      <section className="relative bg-gradient-to-b from-[#fcfaf5] to-[#f0f7f7] pt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="bg-gradient-to-br from-yellow-50 to-yellow-100/80 rounded-t-3xl px-6 py-16 sm:px-12"
          >
            {/* Icon */}
            <motion.div
              initial={{ scale: 0 }}
              whileInView={{ scale: 1 }}
              transition={{ type: "spring", bounce: 0.5 }}
              className="mb-8"
            >
              <div className="w-16 h-16 bg-yellow-200 rounded-2xl flex items-center justify-center transform rotate-12">
                <Mail className="w-8 h-8 text-yellow-600 transform -rotate-12" />
              </div>
            </motion.div>

            {/* Text Content */}
            <div className="max-w-2xl">
              <motion.h2 
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                className="text-4xl font-bold text-gray-900"
              >
                Join Our Creative Community
              </motion.h2>
              
              <motion.p 
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="mt-4 text-xl text-gray-600"
              >
                Get exclusive content tips, early access to new features, and weekly inspiration delivered straight to your inbox.
              </motion.p>
            </div>

            {/* Email Form */}
            <motion.form 
              onSubmit={handleSubmit}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mt-8 max-w-xl"
            >
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1 relative">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    className="w-full px-6 py-4 rounded-xl border-2 border-yellow-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-300 outline-none text-lg bg-white/80"
                    required
                  />
                  <Mail className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none" />
                </div>
                <motion.button
                  type="submit"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="px-8 py-4 bg-blue-600 text-white rounded-xl font-medium text-lg hover:bg-blue-700 transition-all duration-300 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
                >
                  Subscribe
                  <ArrowRight className="w-5 h-5" />
                </motion.button>
              </div>
            </motion.form>

            {/* Social Proof */}
            <motion.div 
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="mt-6 flex items-center gap-2 text-gray-600"
            >
              <Sparkles className="w-4 h-4 text-yellow-500" />
              <span>Join 10,000+ content creators already using RiteUp</span>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Footer Section */}
      <footer className="bg-white">
        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 py-6">
          {/* Top Navigation */}
          <div className="flex flex-col md:flex-row justify-between items-center mb-12">
            <div className="flex items-center space-x-8">
              <a href="/terms" className="text-gray-600 hover:text-gray-900">Terms of Use</a>
              <a href="/privacy" className="text-gray-600 hover:text-gray-900">Privacy Policy</a>
            </div>

            <div className="text-gray-600 my-4 md:my-0">
              2025 © RiteUp. All rights reserved - Designed by{' '}
              <a href="#" className="text-blue-600 hover:text-blue-700">HustleJar</a>
            </div>

            <div className="flex items-center space-x-6">
              <a href="#" className="text-gray-600 hover:text-gray-900 transition-colors">
                <Linkedin className="w-6 h-6" />
              </a>
              <a href="#" className="text-gray-600 hover:text-gray-900 transition-colors">
                <Twitter className="w-6 h-6" />
              </a>
              <a href="#" className="text-gray-600 hover:text-gray-900 transition-colors">
                <Instagram className="w-6 h-6" />
              </a>
            </div>
          </div>

          {/* Bottom Illustration */}
          <div className="w-full">
            <svg viewBox="0 0 1200 200" className="w-full h-auto">
              <defs>
                <linearGradient id="fadeGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#fcfaf5" stopOpacity="0.2" />
                  <stop offset="100%" stopColor="#fcfaf5" stopOpacity="0" />
                </linearGradient>
              </defs>
              
              {/* Background fade effect */}
              <rect width="100%" height="100%" fill="url(#fadeGradient)" />
              
              {/* Decorative line */}
              <path
                d="M0 100C200 100 400 150 600 100C800 50 1000 100 1200 100"
                stroke="#DDD"
                strokeWidth="2"
                strokeDasharray="5 5"
                className="opacity-50"
              />
              
              {/* Placeholder for custom illustration - you would replace this */}
              <g transform="translate(0, 50)">
                {/* Simple placeholder shapes */}
                <circle cx="300" cy="50" r="20" fill="#f0f0f0" />
                <circle cx="900" cy="50" r="20" fill="#f0f0f0" />
              </g>
            </svg>
          </div>
        </div>
      </footer>
    </>
  );
};

export default BottomSections;