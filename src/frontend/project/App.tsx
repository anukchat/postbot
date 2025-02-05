import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar/Sidebar';
import { MarkdownEditor } from './components/Editor/MarkdownEditor';
import { CanvasView } from './components/Canvas/CanvasView';
import { useEditorStore } from './store/editorStore';
import { PostDetails } from './components/PostDetails';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './components/Landing/LandingPage';
import Features from './pages/Features';
import Pricing from './pages/Pricing';
import SignIn from './components/Auth/SignIn';
import SignUp from './components/Auth/SignUp';
import About from './pages/About';
import Contact from './pages/Contact';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import Settings from './pages/Settings';
import { Toaster } from 'react-hot-toast';
import AuthCallback from './components/Auth/AuthCallback';
import Modal from 'react-modal';
import { ErrorBoundary } from 'react-error-boundary';
import { SidebarToggle } from './components/Sidebar/SidebarToggle';
import { EditorToolbar } from './components/Sidebar/EditorToolbar';
import { MainMenuBar } from './components/MenuBar/MenuBar';
import { IconMenuBar } from './components/MenuBar/IconMenuBar';

// Set the root element for accessibility
Modal.setAppElement('#root');

// Error Boundary Fallback Component
function ErrorFallback({ error, resetErrorBoundary }: any) {
  return (
    <div role="alert" className="p-4 bg-red-100 text-red-700">
      <p>Something went wrong:</p>
      <pre>{error.message}</pre>
      <button
        onClick={resetErrorBoundary}
        className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
      >
        Try again
      </button>
    </div>
  );
}

const MainAppLayout: React.FC = () => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false); // Ensure this is false initially
  const [sidebarSize, setSidebarSize] = useState(20);
  const [isCanvasView, setIsCanvasView] = useState(false);
  const [isPostDetailsView, setIsPostDetailsView] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'blog' | 'twitter' | 'linkedin'>('blog');
  const [isManuallyExpanded, setIsManuallyExpanded] = useState(false);
  const [isOverlayVisible, setIsOverlayVisible] = useState(false);
  const { currentPost, isDarkMode, updateContent, updateLinkedinPost, updateTwitterPost, fetchContentByThreadId, setCurrentTab } = useEditorStore();
  const [screenWidth, setScreenWidth] = useState(window.innerWidth);


  const handleSidebarToggle = () => {
    if (isSidebarCollapsed) {
      setIsManuallyExpanded(true);
      setIsOverlayVisible(true); // Show overlay when expanding
    } else {
      setIsManuallyExpanded(false);
      setIsOverlayVisible(false); // Hide overlay when collapsing
    }
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };


  useEffect(() => {
    if (isSidebarCollapsed) {
      setSidebarSize(5); // Minimum width when collapsed
    } else {
      setSidebarSize(isManuallyExpanded ? 90 : 22); // Use 90% width if manually expanded, otherwise default width
    }
  }, [isSidebarCollapsed, isManuallyExpanded]);

  useEffect(() => {
    const handleResize = () => {
      const screenWidth = window.innerWidth;
      if (screenWidth < 768 && !isManuallyExpanded) {
        setIsSidebarCollapsed(true); // Collapse sidebar on small screens unless manually expanded
      }

      // Adjust sidebar size based on screen width
      const newSidebarSize = screenWidth < 1024
        ? (isSidebarCollapsed ? 5 : (isManuallyExpanded ? 90 : 30)) // More space on smaller screens if manually expanded
        : (isSidebarCollapsed ? 5 : 22); // Default sizes on larger screens

      setSidebarSize(newSidebarSize);
    };

    window.addEventListener('resize', handleResize);
    handleResize(); // Initial call

    return () => window.removeEventListener('resize', handleResize);
  }, [isSidebarCollapsed, isManuallyExpanded]);

  useEffect(() => {
    const handleResize = () => {
      setScreenWidth(window.innerWidth);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
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

  const handleCommandInsert = (commandText: string, replaceLength: number) => {
    // Handle command insert logic here
    console.log('Command insert:', commandText, replaceLength);
  };

  return (
    <div className={`h-screen ${isDarkMode ? 'dark' : ''}`}>
      <div className="h-full flex dark:bg-gray-900 dark:text-white">
        {/* Vertical Toolbar - always visible, fixed width */}
        <div className="fixed inset-y-0 left-0 w-12 sm:w-16 bg-white dark:bg-gray-800 border-r 
          dark:border-gray-700 z-30">
          <EditorToolbar isCollapsed={true} onToggleCollapse={handleSidebarToggle} />
        </div>

        {/* Hamburger Toggle */}
        <SidebarToggle 
          isCollapsed={isSidebarCollapsed} 
          onClick={handleSidebarToggle} 
        />

        {/* Sidebar Drawer */}
        <div
          className={`fixed inset-y-0 left-0 z-50 bg-white dark:bg-gray-800 
            transition-transform duration-300 ease-in-out border-r dark:border-gray-700 
            ${isSidebarCollapsed ? '-translate-x-full' : 'translate-x-0'}
            w-[280px] sm:w-[320px] md:w-[350px] lg:w-[400px]
            overflow-hidden`}
        >
          <EditorToolbar isCollapsed={false} onToggleCollapse={handleSidebarToggle} />
          <Sidebar
            isCollapsed={isSidebarCollapsed}
            onToggleCollapse={handleSidebarToggle}
          />
        </div>

        {/* Overlay Backdrop */}
        {!isSidebarCollapsed && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={() => setIsSidebarCollapsed(true)}
          />
        )}

        {/* Main Content Area with fixed width */}
        <div className="flex-1 ml-12 sm:ml-16 min-w-0 relative">
          <div className="flex flex-col h-full max-w-full overflow-x-hidden">
            {/* Add MenuBar here */}
            <MainMenuBar />
            {/* Header with contained width */}
            <div className="border-b p-2 sm:p-3 md:p-4 flex justify-between items-center bg-white dark:bg-gray-800 w-full">
              <div className="flex-1 flex justify-center min-w-0">
                <div className="flex gap-1 sm:gap-2 items-center flex-nowrap overflow-x-auto px-2 sm:px-4 scrollbar-hide">
                  {/* Responsive tab buttons */}
                  <div className="flex gap-1 sm:gap-2 items-center">
                    <button
                      onClick={() => handleTabClick('blog')}
                      className={`px-3 py-1 sm:px-4 sm:py-2 rounded text-sm sm:text-base ${
                        selectedTab === 'blog'
                          ? 'bg-blue-500 text-white'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      Blog
                    </button>
                    <button
                      onClick={() => handleTabClick('twitter')}
                      className={`px-3 py-1 sm:px-4 sm:py-2 rounded text-sm sm:text-base ${
                        selectedTab === 'twitter'
                          ? 'bg-blue-500 text-white'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      Twitter
                    </button>
                    <button
                      onClick={() => handleTabClick('linkedin')}
                      className={`px-3 py-1 sm:px-4 sm:py-2 rounded text-sm sm:text-base ${
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
                      className={`px-3 py-1 sm:px-4 sm:py-2 rounded text-sm sm:text-base ${
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
                      className={`px-3 py-1 sm:px-4 sm:py-2 rounded text-sm sm:text-base ${
                        isPostDetailsView
                          ? 'bg-blue-500 text-white'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Add IconMenuBar here */}
            <IconMenuBar selectedTab={selectedTab} onCommandInsert={handleCommandInsert} />
            
            {/* Content area with contained width */}
            <div className="flex-1 overflow-hidden">
              <div className="h-full max-w-full pt-4">
                {isCanvasView ? (
                  <CanvasView />
                ) : isPostDetailsView ? (
                  <PostDetails />
                ) : (
                  <MarkdownEditor
                    content={getContent()}
                    onChange={handleContentChange}
                    selectedTab={selectedTab}
                  />
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Toaster position="top-right" />
        <ErrorBoundary FallbackComponent={ErrorFallback}>
          <Routes>
            {/* Landing and Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<SignIn />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/features" element={<Features />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/auth/callback" element={<AuthCallback />} />

            {/* Protected routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <MainAppLayout />
              </ProtectedRoute>
            } />
            <Route path="/settings" element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            } />

            {/* Catch-all route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ErrorBoundary>
      </AuthProvider>
    </BrowserRouter>
  );
};