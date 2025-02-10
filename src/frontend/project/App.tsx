import React, { useState, useEffect } from 'react';
import { MarkdownEditor } from './components/Editor/MarkdownEditor';
import { CanvasView } from './components/Canvas/CanvasView';
import { useEditorStore } from './store/editorStore';
import { PostDetails } from './components/PostDetails';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
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
import { IconMenuBar } from './components/MenuBar/IconMenuBar';
import { FloatingTabs } from './components/MenuBar/FloatingTabs';
import UserMenu from './components/Auth/UserMenu';
import { FloatingNav } from './components/Navigation/FloatingNav';
import { NavigationDrawer } from './components/Navigation/NavigationDrawer';

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
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isCanvasView, setIsCanvasView] = useState(false);
  const [isPostDetailsView, setIsPostDetailsView] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'blog' | 'twitter' | 'linkedin'>('blog');
  const { currentPost, isDarkMode, updateContent, updateLinkedinPost, updateTwitterPost, fetchContentByThreadId, setCurrentTab } = useEditorStore();

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
    console.log('Command insert:', commandText, replaceLength);
  };

  return (
    <div className={`h-screen ${isDarkMode ? 'dark' : ''}`}>
      <div className="h-full flex dark:bg-gray-900 dark:text-white">
        {/* Icon Navigation */}
        <FloatingNav 
          onToggleDrawer={() => setIsDrawerOpen(!isDrawerOpen)} 
          isDrawerOpen={isDrawerOpen} 
        />

        {/* Posts Navigation Drawer */}
        <NavigationDrawer 
          isOpen={isDrawerOpen} 
          onClose={() => setIsDrawerOpen(false)} 
        />

        {/* Main Content Area - adjusted left margin to account for icon lane */}
        <div className="flex-1 min-w-0 relative ml-16">
          <div className="flex flex-col h-full max-w-full overflow-x-hidden">
            {/* User Menu - Floating */}
            <div className="fixed top-0 right-0 z-30">
              <div className="flex-shrink-0 px-4 py-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
                <UserMenu />
              </div>
            </div>

            {/* IconMenuBar - Floating - adjusted left spacing */}
            <div className="fixed top-0 right-16 left-0 z-20">
              <div className="flex items-center w-full bg-white dark:bg-gray-800 border-b">
                <IconMenuBar selectedTab={selectedTab} onCommandInsert={handleCommandInsert} />
              </div>
            </div>
            
            {/* FloatingTabs - Floating - adjusted left spacing */}
            <div className="fixed top-12 right-0 left-0 z-20">
              <FloatingTabs 
                selectedTab={selectedTab}
                onTabChange={handleTabChange}
                onViewChange={handleViewChange}
                currentView={isCanvasView ? 'canvas' : isPostDetailsView ? 'details' : 'editor'}
              />
            </div>
            
            {/* Content area */}
            <div className="flex-1 overflow-hidden pt-24">
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