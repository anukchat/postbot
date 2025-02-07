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
import { IconMenuBar } from './components/MenuBar/IconMenuBar';
import { FloatingTabs } from './components/MenuBar/FloatingTabs';
import UserMenu from './components/Auth/UserMenu';

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
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isCanvasView, setIsCanvasView] = useState(false);
  const [isPostDetailsView, setIsPostDetailsView] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'blog' | 'twitter' | 'linkedin'>('blog');
  const [isManuallyExpanded, setIsManuallyExpanded] = useState(false);
  const { currentPost, isDarkMode, updateContent, updateLinkedinPost, updateTwitterPost, fetchContentByThreadId, setCurrentTab } = useEditorStore();

  const handleSidebarToggle = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
    setIsManuallyExpanded(isSidebarCollapsed);
  };

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768 && !isManuallyExpanded) {
        setIsSidebarCollapsed(true);
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize();

    return () => window.removeEventListener('resize', handleResize);
  }, [isSidebarCollapsed, isManuallyExpanded]);

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

  const handleTabChange = (tab: 'blog' | 'twitter' | 'linkedin') => {
    resetViews();
    setCurrentTab(tab);
    setSelectedTab(tab);
    
    if (currentPost?.thread_id && tab !== 'blog') {
      fetchContentByThreadId(currentPost.thread_id, tab);
    }
  };

  const handleViewChange = (view: 'canvas' | 'details') => {
    setIsCanvasView(view === 'canvas');
    setIsPostDetailsView(view === 'details');
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
            {/* User Menu - Floating */}
            <div className="fixed top-0 right-0 z-30">
              <div className="flex-shrink-0 px-4 py-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
                <UserMenu />
              </div>
            </div>

            {/* IconMenuBar - Floating */}
            <div className="fixed top-0 left-12 sm:left-16 right-16 z-20">
              <div className="flex items-center w-full bg-white dark:bg-gray-800 border-b">
                <IconMenuBar selectedTab={selectedTab} onCommandInsert={handleCommandInsert} />
              </div>
            </div>
            
            {/* FloatingTabs - Floating */}
            <div className="fixed top-12 left-12 sm:left-16 right-0 z-20">
              <FloatingTabs 
                selectedTab={selectedTab}
                onTabChange={handleTabChange}
                onViewChange={handleViewChange}
                currentView={isCanvasView ? 'canvas' : isPostDetailsView ? 'details' : 'editor'}
              />
            </div>
            
            {/* Content area with contained width and proper padding for floating elements */}
            <div className="flex-1 overflow-hidden">
              <div className="h-full max-w-full">
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