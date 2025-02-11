import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, LayoutDashboard } from 'lucide-react';
import { theme } from '../../styles/themes';
import { useAuth } from '../../contexts/AuthContext';

const CTASection: React.FC = () => {
  const { user } = useAuth();

  return (
    <section className="py-20 relative overflow-hidden">
      <div className={`absolute inset-0 bg-gradient-to-br ${theme.colors.background.main} -z-10`}></div>
      <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8 relative">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl lg:text-5xl">
            Experience the Power of <br />
            <span className={`${theme.colors.primary.solid} bg-clip-text text-transparent bg-gradient-to-r ${theme.colors.primary.gradient}`}>
              AI-Assisted Research and Writing
            </span>
          </h2>
          <p className="mt-6 text-xl text-gray-600 max-w-2xl mx-auto">
            Join thousands of content creators who trust RiteUp to deliver thoroughly researched, engaging content
          </p>
          {user ? (
            <motion.a
              href="/dashboard"
              className={`mt-8 inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white ${theme.colors.primary.button.bg} ${theme.colors.primary.button.hover} rounded-lg transition-colors duration-300 shadow-lg hover:shadow-xl`}
              whileHover={{ scale: theme.animation.hover.scale }}
              whileTap={{ scale: 0.98 }}
            >
              Go to Dashboard <LayoutDashboard className="ml-2 w-5 h-5" />
            </motion.a>
          ) : (
            <motion.a
              href="/signup"
              className={`mt-8 inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white ${theme.colors.primary.button.bg} ${theme.colors.primary.button.hover} rounded-lg transition-colors duration-300 shadow-lg hover:shadow-xl`}
              whileHover={{ scale: theme.animation.hover.scale }}
              whileTap={{ scale: 0.98 }}
            >
              Start Creating Now <ArrowRight className="ml-2 w-5 h-5" />
            </motion.a>
          )}

          {/* Decorative Image */}
          <div className="absolute right-16 top-1/2 -translate-y-1/2 hidden lg:block">
            <img 
              src="/assets/cta_gif.gif"
              alt="AI Content Generation"
              className="w-64 h-64"
            />
          </div>
        </motion.div>
      </div>

      {/* Footer Image Section */}
      <div className="w-full mx-auto px-4 pt-20">
        <div className="relative w-full h-96 md:h-96">
          {/* Make sure the image is on top using a higher z-index */}
          <motion.img 
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            whileHover={{ 
              scale: 1.05,
              rotate: 0,
              filter: "brightness(1.1)",
              transition: {
                duration: 0.4,
                ease: [0.25, 0.1, 0.25, 1] // Smooth easeInOut
              }
            }}
            src="/assets/footer_image.png"
            alt="Footer Illustration"
            className="relative z-10 w-full h-full object-contain"
          />

          {/* Decorative Elements behind the image */}
          <div className="absolute inset-0 z-0 flex items-end justify-center pointer-events-none">
            <motion.svg
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ delay: 0.3, duration: 1 }}
              viewBox="0 0 1200 200"
              className="w-full h-auto"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <motion.path
                initial={{ pathLength: 0 }}
                whileInView={{ pathLength: 1 }}
                transition={{ duration: 1.5, delay: 0.5 }}
                d="M0 100C200 100 400 150 600 100C800 50 1000 100 1200 100"
                stroke="#DDD"
                strokeWidth="2"
                strokeDasharray="5 5"
                className="opacity-50"
              />
            </motion.svg>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTASection;
