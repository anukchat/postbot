import React, { useState, useEffect } from 'react';
import { MarkdownEditor } from './components/Editor/MarkdownEditor';
import { CanvasView } from './components/Canvas/CanvasView';
import { useEditorStore } from './store/editorStore';
import { PostDetails } from './components/PostDetails';
import { BrowserRouter, Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
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
import { TemplatesView } from './components/Templates/TemplatesView';
import { NewBlogModal } from './components/Modals/NewBlogModal';
import { Bell, Settings as SettingsIcon } from 'lucide-react';
import Tippy from '@tippyjs/react';
import 'tippy.js/dist/tippy.css';
import { AdminLayout } from './components/Admin/AdminLayout';

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
  const [showSourceModal, setShowSourceModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<{
    id: string;
    title: string;
    description: string;
    category: string;
  } | null>(null);
  const location = useLocation();
  
  const { 
    currentPost, 
    isDarkMode, 
    updateContent, 
    updateLinkedinPost, 
    updateTwitterPost, 
    fetchContentByThreadId, 
    setCurrentTab,
    currentTemplate
  } = useEditorStore();

  // Handle template selection from location state
  useEffect(() => {
    const state = location.state as { showSourceModal?: boolean };
    if (state?.showSourceModal) {
      setShowSourceModal(true);
      // Clear the state after using it
      window.history.replaceState({}, document.title);
    }
  }, [location]);

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

  const onTemplateSelect = (template: any) => {
    console.log('Selected template:', template);
    setSelectedTemplate({
      id: template.id, // Changed from template.id
      title: template.title,    // Changed from template.title
      description: template.description,
      category: template.category // Changed from template.category
    }); 
    setShowSourceModal(true);
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
          onNavigateToEditor={() => {
            // Navigate to dashboard if not already there
            if (location.pathname !== '/dashboard') {
              window.location.href = '/dashboard';
            }
          }}
        />

        {/* Main Content Area */}
        <div className="flex-1 min-w-0 relative ml-16">
          {/* User Menu - Adjusted positioning */}
          <div className="fixed top-2 right-0 z-[60]">
            <div className="flex items-center gap-3 px-4">
              <Tippy content="Notifications">
                <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                  <Bell className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                </button>
              </Tippy>
              <Tippy content="Settings">
                <Link to="/settings" className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                  <SettingsIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                </Link>
              </Tippy>
              <UserMenu />
            </div>
        </div>

          {/* Content wrapper with adjusted padding */}
          <div className="flex flex-col h-full max-w-full overflow-x-hidden">
            {currentPost ? (
              <>
                {/* IconMenuBar - Floating */}
                <div className="fixed top-0 right-16 left-0 z-20">
                  <div className="flex items-center w-full bg-white dark:bg-gray-800 border-b">
            <IconMenuBar selectedTab={selectedTab} onCommandInsert={handleCommandInsert} />
                  </div>
                </div>
            
                {/* FloatingTabs - Floating */}
                <div className="fixed top-12 right-0 left-0 z-20">
            <FloatingTabs 
              selectedTab={selectedTab}
              onTabChange={handleTabChange}
              onViewChange={handleViewChange}
              currentView={isCanvasView ? 'canvas' : isPostDetailsView ? 'details' : 'editor'}
            />
                </div>
            
                {/* Content area */}
                <div className="flex-1 overflow-y-auto overflow-x-hidden">
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
              </>
            ) : (
              <TemplatesView onTemplateSelect={onTemplateSelect} />
            )}
          </div>
        </div>
      </div>

      {/* Source Selection Modal */}
      <NewBlogModal
        isOpen={showSourceModal}
        onClose={() => {
          setShowSourceModal(false);
          setSelectedTemplate(null); // Clear the template when modal closes
        }}
        onGenerate={async () => {}} // Implement generation logic
        selectedTemplate={selectedTemplate || undefined}  // Pass the selected template
      />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#333',
              color: '#fff',
            },
          }}
        />
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
            <Route path="/admin" element={
              <ProtectedRoute>
                <AdminLayout />
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