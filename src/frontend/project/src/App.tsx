import React, { useState, useEffect, useRef } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { Sidebar } from './components/Sidebar/Sidebar';
import { MarkdownEditor } from './components/Editor/MarkdownEditor';
import { CanvasView } from './components/Canvas/CanvasView';
import { useEditorStore } from './store/editorStore';
import { PostDetails } from './components/PostDetails';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './components/Landing/LandingPage';
import Features from './pages/Features';
import Pricing from './pages/Pricing';
import SignIn from './components/Auth/SignIn';
import SignUp from './components/Auth/SignUp';
import About from './pages/About';
import Contact from './pages/Contact';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/Auth/ProtectedRoute';  // Updated import
import Settings from './pages/Settings';
import { Toaster } from 'react-hot-toast'; // Add Toaster import
import UserMenu from './components/Auth/UserMenu'; // Add this import
import AuthCallback from './components/Auth/AuthCallback';
import Modal from 'react-modal'; // Add Modal import

// Add this line before the App component
Modal.setAppElement('#root');

const MainAppLayout: React.FC = () => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [sidebarSize, setSidebarSize] = useState(20);
  const [isCanvasView, setIsCanvasView] = useState(false);
  const [isPostDetailsView, setIsPostDetailsView] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'blog' | 'twitter' | 'linkedin'>('blog');
  const { currentPost, isDarkMode, updateContent, updateLinkedinPost, updateTwitterPost, fetchContentByThreadId, setCurrentTab } = useEditorStore();
  const contentPanelRef = useRef<any>(null);
  const sidebarPanelRef = useRef<any>(null);

  const handleSidebarToggle = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  useEffect(() => {
    if (isSidebarCollapsed) {
      setSidebarSize(5); // Minimum width when collapsed
      if (contentPanelRef.current) {
        contentPanelRef.current.resize(95); // Adjust content panel size
      }
    } else {
      setSidebarSize(22); // Default width when expanded
      if (contentPanelRef.current) {
        contentPanelRef.current.resize(78); // Adjust content panel size
      }
    }
  }, [isSidebarCollapsed]);

  useEffect(() => {
    const handleWindowResize = () => {
      if (contentPanelRef.current && sidebarPanelRef.current) {
        const currentSidebarSize = sidebarPanelRef.current.getSize();
        const currentContentSize = contentPanelRef.current.getSize();
        const totalSize = currentSidebarSize + currentContentSize;

        const newSidebarSize = (currentSidebarSize / totalSize) * 100;
        const newContentSize = (currentContentSize / totalSize) * 100;

        sidebarPanelRef.current.resize(newSidebarSize);
        contentPanelRef.current.resize(newContentSize);
      }
    };

    window.addEventListener('resize', handleWindowResize);
    return () => window.removeEventListener('resize', handleWindowResize);
  }, []);

  const handleContentChange = (newContent: string) => {
    if (!currentPost) return;

    const updatedPost = { ...currentPost };

    switch (selectedTab) {
      case 'blog':
        updatedPost.content = newContent;
        updateContent(updatedPost.content);
        break;
      case 'twitter':
        updatedPost.twitter_post = newContent;
        updateTwitterPost(updatedPost.twitter_post);
        break;
      case 'linkedin':
        updatedPost.linkedin_post = newContent;
        updateLinkedinPost(updatedPost.linkedin_post);
        break;
    }
  };

  const resetViews = () => {
    setIsCanvasView(false);
    setIsPostDetailsView(false);
  };

  const handleTabClick = (tab: 'blog' | 'twitter' | 'linkedin') => {
    resetViews();
    setCurrentTab(tab);
    
    if (currentPost?.thread_id) {
      const postTypeMap = {
        twitter: 'twitter',
        linkedin: 'linkedin',
        blog: 'blog'
      };
      
      if (tab !== 'blog') {
        fetchContentByThreadId(currentPost.thread_id, postTypeMap[tab]);
      }
    }
    setSelectedTab(tab);
  };

  useEffect(() => {
    resetViews();
  }, [currentPost]);

  const getContent = (): string => {
    if (!currentPost) return '';

    switch (selectedTab) {
      case 'blog':
        return currentPost.content;
      case 'twitter':
        return currentPost.twitter_post || '';
      case 'linkedin':
        return currentPost.linkedin_post || '';
      default:
        return '';
    }
  };


  return (
    <div className={`h-screen ${isDarkMode ? 'dark' : ''}`}>
      <div className="h-full flex dark:bg-gray-900 dark:text-white">
        <PanelGroup direction="horizontal">
          <Panel
            defaultSize={sidebarSize}
            minSize={5}
            ref={sidebarPanelRef}
            order={1}
          >
            <Sidebar
              isCollapsed={isSidebarCollapsed}
              onToggleCollapse={handleSidebarToggle}
            />
          </Panel>
          <PanelResizeHandle className="w-1 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors" />
          <Panel
            defaultSize={80}
            minSize={20}
            order={2}
            ref={contentPanelRef}
          >
            <div className="h-full flex flex-col">
              <div className="border-b p-2 flex justify-between items-center">
                <div className="flex gap-2">
                  <button
                    onClick={() => handleTabClick('blog')}
                    className={`px-4 py-2 rounded ${
                      selectedTab === 'blog'
                        ? 'bg-blue-500 text-white'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    Blog
                  </button>
                  <button
                    onClick={() => handleTabClick('twitter')}
                    className={`px-4 py-2 rounded ${
                      selectedTab === 'twitter'
                        ? 'bg-blue-500 text-white'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    Twitter
                  </button>
                  <button
                    onClick={() => handleTabClick('linkedin')}
                    className={`px-4 py-2 rounded ${
                      selectedTab === 'linkedin'
                        ? 'bg-blue-500 text-white'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    LinkedIn
                  </button>
                  <button
                    onClick={() => {
                      setIsCanvasView(true);
                      setIsPostDetailsView(false);
                    }}
                    className={`px-4 py-2 rounded ${
                      isCanvasView
                        ? 'bg-blue-500 text-white'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    Canvas
                  </button>
                  <button
                    onClick={() => {
                      setIsPostDetailsView(true);
                      setIsCanvasView(false);
                    }}
                    className={`px-4 py-2 rounded ${
                      isPostDetailsView
                        ? 'bg-blue-500 text-white'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    View Details
                  </button>
                </div>
                <div className="z-[100]"> {/* Add z-index wrapper */}
                  <UserMenu />
                </div>
              </div>
              <div className="flex-1 overflow-auto">
                {isCanvasView ? (
                  <CanvasView />
                ) : isPostDetailsView ? (
                  <PostDetails />
                ) : (
                  <MarkdownEditor
                    content={getContent()}
                    onChange={handleContentChange}
                    selectedTab={selectedTab} // Pass selectedTab prop
                  />
                )}
              </div>
            </div>
          </Panel>
        </PanelGroup>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Toaster position="top-right" />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<SignIn />} /> {/* Keep using /login */}
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route
            path="/app/*"
            element={
              <ProtectedRoute>
                <MainAppLayout />
              </ProtectedRoute>
            }
          />
          <Route path="/features" element={<Features />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/settings" element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          } />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};