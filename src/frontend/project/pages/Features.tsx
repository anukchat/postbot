import React from 'react';
import { Navbar } from '../components/Landing/Navbar';
import { Bot, Search, FileText, LayoutGrid, Zap, Globe, Users, Shield } from 'lucide-react';
import { motion } from 'framer-motion';
import { theme } from '../styles/themes';

const Features: React.FC = () => {
  const features = [
    {
      icon: <Bot className="w-12 h-12 text-blue-500" />,
      title: "AI-Powered Conversion",
      description: "Advanced AI algorithms that understand context and maintain your unique voice while converting tweets to blog posts."
    },
    {
      icon: <Search className="w-12 h-12 text-blue-500" />,
      title: "Deep Research",
      description: "Our AI analyzes multiple authoritative sources to gather comprehensive insights for your content."
    },
    {
      icon: <FileText className="w-12 h-12 text-blue-500" />,
      title: "Smart Writing",
      description: "Transform research into well-structured, engaging blog posts optimized for your audience."
    },
    {
      icon: <LayoutGrid className="w-12 h-12 text-blue-500" />,
      title: "Multi-Platform Publishing",
      description: "Publish your content directly to multiple platforms with automatic format optimization."
    },
    {
      icon: <Zap className="w-12 h-12 text-blue-500" />,
      title: "Real-Time Processing",
      description: "Convert and publish content quickly with our high-performance processing engine."
    },
    {
      icon: <Globe className="w-12 h-12 text-blue-500" />,
      title: "SEO Optimization",
      description: "Built-in tools ensure your content ranks well and reaches your target audience effectively."
    },
    {
      icon: <Users className="w-12 h-12 text-blue-500" />,
      title: "Team Collaboration",
      description: "Work together seamlessly with role-based access and shared workspaces."
    },
    {
      icon: <Shield className="w-12 h-12 text-blue-500" />,
      title: "Content Protection",
      description: "Advanced security measures to keep your content and data safe and private."
    }
  ];

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
            <h1 className={`text-4xl font-bold mb-4 ${theme.colors.primary.text.dark}`}>Powerful Features for Content Creators</h1>
            <p className="text-xl text-gray-600">Everything you need to create outstanding content</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ scale: theme.animation.hover.scale }}
                className={`${theme.colors.card.gradient} backdrop-blur-sm rounded-lg p-6 shadow-lg ${theme.colors.card.border} ${theme.colors.card.hover} transition-all duration-300`}
              >
                <div className={`mb-4 p-3 ${theme.colors.primary.button.bg} rounded-lg inline-block`}>
                  {React.cloneElement(feature.icon, { className: `w-8 h-8 text-white` })}
                </div>
                <h3 className={`text-xl font-semibold mb-2 ${theme.colors.primary.text.dark}`}>{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Features;
