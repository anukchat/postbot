import React from 'react';
import Head from 'next/head';
import { ArrowRight, Bot, Share2, Image, Share, UserCheck, LayoutDashboard, CheckCircle, Target, Search, PenTool } from 'lucide-react';
import { motion } from 'framer-motion';
import { Navbar } from '../components/Landing/Navbar';
import { useAuth } from '../contexts/AuthContext';
import { theme } from '../styles/themes';
import CTASection from '../components/Landing/CTASection';
import EmailSignupSection from '../components/Landing/EmailSignupSection';
import Footer from '../components/Landing/Footer';

const LandingPage: React.FC = () => {
  const { user } = useAuth();  // Removed unused signIn

  const fadeInUp = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6 }
  };

  return (
    <>
      <Head>
        <title>RiteUp - AI-Powered Blog & Social Media Content Creation</title>
        <meta name="description" content="Create thoroughly researched, engaging blog posts and social media content with AI assistance. Deep research meets effortless writing." />
        <meta name="keywords" content="AI blog writing, social media content, content research, blog content creation, AI copywriting, content marketing" />
        <meta property="og:title" content="RiteUp - Deep Research Meets Effortless Writing" />
        <meta property="og:description" content="Create thoroughly researched blog posts and social media content with AI assistance" />
        <meta property="og:image" content="/assets/og-image.png" />
        <meta name="twitter:card" content="summary_large_image" />
        <link rel="canonical" href="https://riteup.ai" />
      </Head>

      <Navbar />
      <main className={`min-h-screen bg-gradient-to-b ${theme.colors.background.main} relative overflow-hidden`}>
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className={`absolute top-0 -left-1/4 w-[800px] h-[800px] rounded-full bg-gradient-to-br ${theme.colors.background.glow.primary} blur-3xl animate-pulse`}></div>
          <div className={`absolute top-1/3 -right-1/4 w-[600px] h-[600px] rounded-full bg-gradient-to-bl ${theme.colors.background.glow.secondary} blur-3xl animate-pulse`} style={{ animationDuration: theme.animation.glow.duration.medium }}></div>
          <div className={`absolute -bottom-32 left-1/2 transform -translate-x-1/2 w-[800px] h-[400px] rounded-full bg-gradient-to-t ${theme.colors.background.glow.tertiary} blur-3xl animate-pulse`} style={{ animationDuration: theme.animation.glow.duration.slow }}></div>
        </div>
        <section className="relative pt-28 sm:pt-32 px-4 mx-auto max-w-7xl sm:px-6 lg:px-8 text-center overflow-hidden" aria-label="Hero section">
          <div className="absolute inset-0 overflow-hidden -z-10">
            <div className="absolute -top-40 -right-40 w-[500px] h-[500px] rounded-full bg-gradient-to-br from-orange-400/30 via-rose-400/30 to-pink-400/30 blur-3xl animate-pulse"></div>
            <div className="absolute -top-20 -left-40 w-[600px] h-[600px] rounded-full bg-gradient-to-br from-amber-300/30 via-orange-400/30 to-rose-400/30 blur-3xl animate-pulse" style={{ animationDuration: '8s' }}></div>
            <div className="absolute bottom-0 right-0 w-[400px] h-[400px] rounded-full bg-gradient-to-tl from-pink-400/30 via-rose-400/30 to-orange-400/30 blur-3xl animate-pulse" style={{ animationDuration: '6s' }}></div>
          </div>
          
          <motion.div {...fadeInUp} className="space-y-6">
            <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl xl:text-7xl tracking-tight">
              Create <span className={`${theme.colors.primary.solid} bg-clip-text text-transparent bg-gradient-to-r ${theme.colors.primary.gradient}`}>Research-Backed Content</span><br className="hidden sm:block" /> at Scale
            </h1>
            <p className="mt-6 text-xl sm:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Transform your ideas into thoroughly researched blog posts and social media content, powered by AI research and expert writing assistance.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-6">
              {user ? (
                <motion.a
                  href="/dashboard"
                  className={`w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white ${theme.colors.primary.button.bg} ${theme.colors.primary.button.hover} rounded-lg transition-colors duration-300 shadow-lg hover:shadow-xl`}
                  whileHover={{ scale: theme.animation.hover.scale }}
                  whileTap={{ scale: 0.98 }}
                >
                  Go to Dashboard <LayoutDashboard className="ml-2 w-5 h-5" />
                </motion.a>
              ) : (
                <motion.a
                  href="/signup"
                  className={`w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white ${theme.colors.primary.button.bg} ${theme.colors.primary.button.hover} rounded-lg transition-colors duration-300 shadow-lg hover:shadow-xl`}
                  whileHover={{ scale: theme.animation.hover.scale }}
                  whileTap={{ scale: 0.98 }}
                >
                  Get Started Free <ArrowRight className="ml-2 w-5 h-5" />
                </motion.a>
              )}
              <motion.a
                href="#demo"
                className={`w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 text-lg font-medium ${theme.colors.primary.solid} border-2 ${theme.colors.primary.border} rounded-lg hover:bg-gray-50 transition-colors duration-300`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Watch Demo
              </motion.a>
            </div>
            <motion.div className="mt-8 flex flex-wrap justify-center gap-4 text-sm text-gray-600">
              <div className="flex items-center">
                <CheckCircle className={`w-5 h-5 ${theme.colors.primary.solid} mr-2`} />
                <span>Deep Research</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className={`w-5 h-5 ${theme.colors.primary.solid} mr-2`} />
                <span>SEO Optimized</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className={`w-5 h-5 ${theme.colors.primary.solid} mr-2`} />
                <span>Review & Edit</span>
              </div>
            </motion.div>
          </motion.div>

          <motion.div
            className="mt-16 max-w-5xl mx-auto rounded-2xl overflow-hidden transform-gpu"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            whileHover={{ 
              scale: theme.animation.hover.scale,
              y: -10,
              transition: { duration: 0.4 }
            }}
          >
            <div className="relative">
              <img
                src="/assets/background_tp.png"
                alt="RiteUp platform interface showcase"
                className="w-full h-auto rounded-2xl shadow-xl transition-transform duration-300"
                loading="lazy"
              />
            </div>
          </motion.div>
        </section>

        <section className="py-24 relative overflow-hidden" aria-label="Features section">
          <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-center mb-20"
            >
              <span className={`${theme.colors.primary.solid} font-semibold text-lg`}>How It Works</span>
              <h2 className="mt-3 text-3xl font-bold text-gray-900 sm:text-4xl lg:text-5xl">
                Research-First Content Creation
              </h2>
              <p className="mt-4 text-xl text-gray-600 max-w-2xl mx-auto">
                Our AI-powered platform handles the heavy lifting of research and writing, while you maintain full creative control
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
              {[
                {
                  step: "1",
                  title: "Deep Research",
                  description: "Our AI scans and analyzes multiple authoritative sources to gather comprehensive data and insights",
                  icon: <Search className={`w-7 h-7 ${theme.colors.primary.solid} transition-all duration-300 transform group-hover:scale-110`} />
                },
                {
                  step: "2",
                  title: "Smart Draft",
                  description: "Transform research into well-structured blog posts and engaging social content",
                  icon: <PenTool className={`w-7 h-7 ${theme.colors.primary.solid} transition-all duration-300 transform group-hover:scale-110`} />
                },
                {
                  step: "3",
                  title: "Review & Publish",
                  description: "Make final edits and refinements before publishing your polished content",
                  icon: <CheckCircle className={`w-7 h-7 ${theme.colors.primary.solid} transition-all duration-300 transform group-hover:scale-110`} />
                }
              ].map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="group relative perspective-1000"
                  whileHover={{ 
                    scale: theme.animation.hover.scale,
                    rotateX: theme.animation.hover.rotate,
                    rotateY: theme.animation.hover.rotate
                  }}
                >
                  <div className={`bg-gradient-to-br ${theme.colors.card.gradient} backdrop-blur-sm p-8 rounded-xl transition-all duration-300 shadow-lg hover:shadow-2xl border ${theme.colors.card.border} transform hover:-translate-y-1`}>
                    <div className={`w-14 h-14 bg-gradient-to-br ${theme.colors.primary.medium} group-hover:${theme.colors.primary.dark} rounded-xl flex items-center justify-center mb-6 transition-all duration-300 shadow-inner`}>
                      {step.icon}
                    </div>
                    <h3 className={`text-2xl font-bold ${theme.colors.primary.text.dark} mb-3 tracking-tight flex items-center gap-3`}>
                      <span className={`${theme.colors.primary.solid} text-xl`}>Step {step.step}:</span> {step.title}
                    </h3>
                    <p className={`${theme.colors.primary.text.dark} text-lg leading-relaxed`}>{step.description}</p>
                  </div>
                  {index < 2 && (
                    <div className="hidden md:block absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2">
                      <ArrowRight className={`w-6 h-6 ${theme.colors.primary.solid}/30`} />
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-24 relative overflow-hidden" aria-label="Features grid section">
          <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-center mb-20"
            >
              <span className={`${theme.colors.primary.solid} font-semibold text-lg`}>Features</span>
              <h2 className="mt-3 text-3xl font-bold text-gray-900 sm:text-4xl lg:text-5xl">
                Everything You Need
              </h2>
              <p className="mt-4 text-xl text-gray-600 max-w-2xl mx-auto">
                Powerful features to help you create outstanding content
              </p>
            </motion.div>

            <div className="grid grid-cols-1 gap-12 sm:grid-cols-2 lg:grid-cols-3">
              {[{
                icon: <Bot className={`w-8 h-8 ${theme.colors.primary.solid}`} />,
                title: "Deep Research",
                description: "Our AI analyzes multiple sources to gather comprehensive, accurate information for your content."
              }, {
                icon: <Share className={`w-8 h-8 ${theme.colors.primary.solid}`} />,
                title: "Smart Writing",
                description: "Transform research into engaging blog posts and social media content that resonates with your audience."
              }, {
                icon: <UserCheck className={`w-8 h-8 ${theme.colors.primary.solid}`} />,
                title: "Expert Review",
                description: "Maintain full control with our intuitive editing interface for final refinements."
              }, {
                icon: <Target className={`w-8 h-8 ${theme.colors.primary.solid}`} />,
                title: "SEO Optimization",
                description: "Built-in SEO tools ensure your content ranks well and reaches your target audience."
              }, {
                icon: <Image className={`w-8 h-8 ${theme.colors.primary.solid}`} />,
                title: "Multi-Format Ready",
                description: "Automatically format your content for blogs, social media, and other platforms."
              }, {
                icon: <Share2 className={`w-8 h-8 ${theme.colors.primary.solid}`} />,
                title: "Easy Publishing",
                description: "Publish directly to your blog or schedule social media posts with one click."
              }].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 50 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="group relative perspective-1000"
                  whileHover={{ 
                    scale: theme.animation.hover.scale,
                    rotateX: theme.animation.hover.rotate,
                    rotateY: theme.animation.hover.rotate 
                  }}
                >
                  <div className={`relative p-8 bg-gradient-to-br ${theme.colors.primary.light} rounded-xl transition-all duration-300 shadow-lg hover:shadow-2xl border-b-4 border-r-4 ${theme.colors.primary.border} transform hover:-translate-y-1 hover:rotate-1`}>
                    <div className={`flex items-center justify-center w-16 h-16 bg-gradient-to-br ${theme.colors.primary.medium} rounded-xl group-hover:${theme.colors.primary.dark} transition-colors duration-300 mb-6 shadow-inner`}>
                      {feature.icon}
                    </div>
                    <h3 className={`text-2xl font-bold ${theme.colors.primary.text.dark} mb-4 tracking-tight`}>{feature.title}</h3>
                    <p className={`${theme.colors.primary.text.dark} leading-relaxed text-lg`}>{feature.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        <CTASection />
        <EmailSignupSection />
        <Footer />
      </main>
    </>
  );
};

export default LandingPage;
