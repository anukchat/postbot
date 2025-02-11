import React from 'react';
import { motion } from 'framer-motion';
import { Send } from 'lucide-react';
import { theme } from '../../styles/themes';

const EmailSignupSection: React.FC = () => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle email signup logic
  };

  return (
    <section className="py-16 relative overflow-hidden">
      <div className={`absolute inset-0 bg-gradient-to-br ${theme.colors.card.gradient} -z-10`}></div>
      <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <h2 className={`text-2xl font-bold ${theme.colors.primary.text.dark} sm:text-3xl`}>
            Stay Updated with Content Creation Tips
          </h2>
          <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
            Get the latest insights on content creation and AI writing delivered to your inbox
          </p>
          <form onSubmit={handleSubmit} className="mt-8 max-w-md mx-auto">
            <div className="flex gap-4">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <motion.button
                type="submit"
                className={`px-6 py-3 ${theme.colors.primary.button.bg} ${theme.colors.primary.button.hover} text-white rounded-lg transition-colors duration-300 flex items-center gap-2`}
                whileHover={{ scale: theme.animation.hover.scale }}
                whileTap={{ scale: 0.98 }}
              >
                Subscribe
                <Send className="w-4 h-4" />
              </motion.button>
            </div>
          </form>
        </motion.div>
      </div>
    </section>
  );
};

export default EmailSignupSection;