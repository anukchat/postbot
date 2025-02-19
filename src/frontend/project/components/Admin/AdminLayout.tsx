import React, { useEffect } from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/Tabs';
import { TemplateManagement } from '../Templates/TemplateManagement';
import { ParameterManagement } from './ParameterManagement';
import { Settings, BookIcon } from 'lucide-react';
import { SharedLayout } from '../Layout/SharedLayout';
import { useEditorStore } from '../../store/editorStore';

export const AdminLayout: React.FC = () => {
  const isDarkMode = useEditorStore(state => state.isDarkMode);
  const { setIsAdminView } = useEditorStore();

  useEffect(() => {
    // Set admin view flag when component mounts
    setIsAdminView(true);

    // Reset admin view flag when component unmounts
    return () => {
      setIsAdminView(false);
    };
  }, [setIsAdminView]);

  return (
    <div className={`h-screen ${isDarkMode ? 'dark' : ''}`}>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pl-16">
        <div className="h-full container mx-auto py-6 px-4">

          <div className="flex items-center mb-6">
            <h1 className="text-2xl font-bold">Admin Dashboard</h1>
          </div>

          <SharedLayout />
          
          
          <Tabs defaultValue="templates" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="templates" className="flex items-center gap-2">
                <BookIcon className="w-4 h-4" />
                Template Management
              </TabsTrigger>
              <TabsTrigger value="parameters" className="flex items-center gap-2">
                <Settings className="w-4 h-4" />
                Parameter Settings
              </TabsTrigger>
            </TabsList>

            <TabsContent value="templates">
              <TemplateManagement />
            </TabsContent>

            <TabsContent value="parameters">
              <ParameterManagement />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};