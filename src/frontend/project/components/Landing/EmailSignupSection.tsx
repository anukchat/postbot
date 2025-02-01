import React, { useState } from 'react';
import { ArrowRight, Sparkles, Mail } from 'lucide-react';
import { motion } from 'framer-motion';

const EmailSignupSection = () => {
  const [email, setEmail] = useState('');

  const handleSubmit = (e: { preventDefault: () => void; }) => {
    e.preventDefault();
  };

  return (
    <section className="bg-[#fcfaf5] w-full flex justify-center items-center">
      <motion.div 
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="w-full bg-gradient-to-b from-transparent via-yellow-100/80 to-transparent backdrop-blur-sm"
      >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 flex flex-col items-center text-center">
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
      className="mt-8 max-w-xl w-full"
      >
      <div className="flex flex-col sm:flex-row gap-4">
      <div className="flex-1 relative">
      <input
      type="email"
      value={email}
      onChange={(e) => setEmail(e.target.value)}
      placeholder="Enter your email"
      className="w-full px-6 py-4 rounded-xl border-2 border-yellow-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-300 outline-none text-lg bg-white/80 backdrop-blur-sm"
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
      </div>
      </motion.div>
    </section>
  );
};

export default EmailSignupSection;