import React from 'react';
import { Navbar } from '../components/Landing/Navbar';
import { Mail, MessageCircle, Send } from 'lucide-react';
import { motion } from 'framer-motion';
import { theme } from '../styles/themes';

const Contact: React.FC = () => {
  return (
    <div className={`min-h-screen bg-gradient-to-b ${theme.colors.background.main} relative overflow-hidden`}>
      <Navbar />
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute top-0 -right-1/4 w-[600px] h-[600px] rounded-full bg-gradient-to-br ${theme.colors.background.glow.primary} blur-3xl animate-pulse`}></div>
        <div className={`absolute bottom-0 -left-1/4 w-[600px] h-[600px] rounded-full bg-gradient-to-tl ${theme.colors.background.glow.secondary} blur-3xl animate-pulse`} style={{ animationDuration: '8s' }}></div>
      </div>
      <div className="pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <motion.h1 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`text-4xl font-bold mb-4 ${theme.colors.primary.text.dark}`}
            >
              Get in Touch
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-xl text-gray-600"
            >
              Have questions? We'd love to hear from you.
            </motion.p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className={`space-y-8 ${theme.colors.card.gradient} backdrop-blur-sm p-8 rounded-lg shadow-lg ${theme.colors.card.border}`}
            >
              <div className="flex items-start space-x-4">
                <div className={`p-3 ${theme.colors.primary.button.bg} rounded-lg`}>
                  <Mail className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className={`text-lg font-medium ${theme.colors.primary.text.dark}`}>Email Us</h3>
                  <p className="text-gray-600">support@riteup.com</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className={`p-3 ${theme.colors.primary.button.bg} rounded-lg`}>
                  <MessageCircle className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className={`text-lg font-medium ${theme.colors.primary.text.dark}`}>Live Chat</h3>
                  <p className="text-gray-600">Available 24/7</p>
                </div>
              </div>
            </motion.div>

            <motion.form 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className={`space-y-6 ${theme.colors.card.gradient} backdrop-blur-sm p-8 rounded-lg shadow-lg ${theme.colors.card.border}`}
            >
              <div>
                <label htmlFor="name" className={`block text-sm font-medium ${theme.colors.primary.text.dark}`}>Name</label>
                <input
                  type="text"
                  id="name"
                  className={`mt-1 block w-full rounded-md border ${theme.colors.primary.border} bg-white/70 backdrop-blur-sm shadow-sm focus:ring-2 focus:ring-offset-2 ${theme.colors.primary.button.hover} transition-colors`}
                />
              </div>

              <div>
                <label htmlFor="email" className={`block text-sm font-medium ${theme.colors.primary.text.dark}`}>Email</label>
                <input
                  type="email"
                  id="email"
                  className={`mt-1 block w-full rounded-md border ${theme.colors.primary.border} bg-white/70 backdrop-blur-sm shadow-sm focus:ring-2 focus:ring-offset-2 ${theme.colors.primary.button.hover} transition-colors`}
                />
              </div>

              <div>
                <label htmlFor="message" className={`block text-sm font-medium ${theme.colors.primary.text.dark}`}>Message</label>
                <textarea
                  id="message"
                  rows={4}
                  className={`mt-1 block w-full rounded-md border ${theme.colors.primary.border} bg-white/70 backdrop-blur-sm shadow-sm focus:ring-2 focus:ring-offset-2 ${theme.colors.primary.button.hover} transition-colors`}
                ></textarea>
              </div>

              <motion.button
                whileHover={{ scale: theme.animation.hover.scale }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                className={`w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${theme.colors.primary.button.bg} ${theme.colors.primary.button.hover} transition-colors duration-300`}
              >
                Send Message
                <Send className="w-4 h-4 ml-2" />
              </motion.button>
            </motion.form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;
