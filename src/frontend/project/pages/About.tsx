import React from 'react';
import { Navbar } from '../components/Landing/Navbar';
import { Bot, Users, Code, Globe, BookOpen, Shield, Zap, Target } from 'lucide-react';
import { motion } from 'framer-motion';
import { theme } from '../styles/themes';

const About: React.FC = () => {
  const infoCards = [
    {
      icon: <Bot className="w-12 h-12 text-white" />,
      title: "Our Mission",
      description: "To empower content creators by providing intelligent tools that transform casual social media conversations into professional blog content."
    },
    {
      icon: <Users className="w-12 h-12 text-white" />,
      title: "Our Team",
      description: "A passionate group of developers, designers, and content creators working together to build the best content creation tools."
    },
    {
      icon: <Code className="w-12 h-12 text-white" />,
      title: "Technology",
      description: "Built with cutting-edge AI and modern web technologies to provide a seamless content creation experience."
    },
    {
      icon: <Globe className="w-12 h-12 text-white" />,
      title: "Global Reach",
      description: "Supporting content creators worldwide in their journey to reach broader audiences through quality content."
    }
  ];

  const values = [
    {
      icon: <BookOpen className="w-8 h-8 text-white" />,
      title: "Knowledge Sharing",
      description: "We believe in making knowledge accessible and engaging."
    },
    {
      icon: <Shield className="w-8 h-8 text-white" />,
      title: "Trust & Security",
      description: "Your content and data security is our top priority."
    },
    {
      icon: <Zap className="w-8 h-8 text-white" />,
      title: "Innovation",
      description: "Constantly pushing the boundaries of what's possible."
    },
    {
      icon: <Target className="w-8 h-8 text-white" />,
      title: "User Focus",
      description: "Everything we build starts with user needs."
    }
  ];

  return (
    <div className={`min-h-screen bg-gradient-to-b ${theme.colors.background.main} relative overflow-hidden`}>
      <Navbar />
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute top-0 -left-1/4 w-[800px] h-[800px] rounded-full bg-gradient-to-br ${theme.colors.background.glow.primary} blur-3xl animate-pulse`}></div>
        <div className={`absolute bottom-0 -right-1/4 w-[600px] h-[600px] rounded-full bg-gradient-to-tl ${theme.colors.background.glow.secondary} blur-3xl animate-pulse`} style={{ animationDuration: '8s' }}></div>
      </div>

      <div className="pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16 relative">
            <motion.h1 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`text-4xl font-bold mb-4 ${theme.colors.primary.text.dark}`}
            >
              About RITE UP
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-xl text-gray-600 max-w-3xl mx-auto"
            >
              We're building the future of content creation, helping creators transform their social media presence into lasting, meaningful content.
            </motion.p>
            {/* Add a new section for mission statement */}
            <motion.h2 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className={`text-2xl font-semibold mt-8 ${theme.colors.primary.text.dark}`}
            >
              Our Mission
            </motion.h2>
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="text-lg text-gray-600 mt-2"
            >
              To empower content creators by providing intelligent tools that transform casual conversations into professional content.
            </motion.p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
            {infoCards.map((card, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ scale: theme.animation.hover.scale }}
                className={`${theme.colors.card.gradient} backdrop-blur-sm p-8 rounded-lg shadow-lg ${theme.colors.card.border} ${theme.colors.card.hover}`}
              >
                <div className={`${theme.colors.primary.button.bg} rounded-lg p-4 inline-block mb-4`}>
                  {card.icon}
                </div>
                <h2 className={`text-2xl font-bold mb-4 ${theme.colors.primary.text.dark}`}>{card.title}</h2>
                <p className="text-gray-600">{card.description}</p>
              </motion.div>
            ))}
          </div>

          <div className="mt-20">
            <motion.h2 
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className={`text-3xl font-bold text-center mb-12 ${theme.colors.primary.text.dark}`}
            >
              Our Values
            </motion.h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
              {values.map((value, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  whileHover={{ scale: theme.animation.hover.scale }}
                  className={`${theme.colors.card.gradient} backdrop-blur-sm p-6 rounded-lg shadow-lg ${theme.colors.card.border} ${theme.colors.card.hover}`}
                >
                  <div className={`${theme.colors.primary.button.bg} rounded-lg p-3 inline-block mb-4`}>
                    {value.icon}
                  </div>
                  <h3 className={`text-xl font-bold mb-2 ${theme.colors.primary.text.dark}`}>{value.title}</h3>
                  <p className="text-gray-600">{value.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;
