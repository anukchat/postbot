import React from 'react';
import { ArrowRight, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

const CTASection = () => {
  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-4">
        <div className="bg-[#a8e5e5] rounded-3xl p-16 relative overflow-hidden">
          {/* Content Container */}
          <div className="max-w-3xl">
            <motion.h2 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="text-4xl md:text-5xl font-bold text-[#1a472a] leading-tight"
            >
              Ready to transform your ideas?
            </motion.h2>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1, duration: 0.6, ease: "easeOut" }}
              className="mt-6 text-xl text-[#1a472a]/80 leading-relaxed"
            >
              Join thousands of content creators who are saving time and reaching more readers.
            </motion.p>

            {/* Buttons Container */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6, ease: "easeOut" }}
              className="mt-10 flex flex-col sm:flex-row gap-4"
            >
              <motion.a
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                href="/dashboard"
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white bg-[#1a472a] rounded-lg hover:bg-[#1a472a]/90 transition-colors"
              >
                Start Creating Now
                <ArrowRight className="ml-2 w-5 h-5" />
              </motion.a>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-[#1a472a] bg-transparent border-2 border-[#1a472a] rounded-lg hover:bg-[#1a472a]/10 transition-colors"
              >
                <Sparkles className="w-5 h-5 mr-2" />
                See Examples
              </motion.button>
            </motion.div>
          </div>

          {/* Decorative Image */}
          <div className="absolute right-16 top-1/2 -translate-y-1/2 hidden lg:block">
            <img 
              src="/assets/cta_gif.gif"
              alt="AI Content Generation"
              className="w-64 h-64"
            />
          </div>
        </div>
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
