import React, { useState, useEffect, useRef } from 'react';
import { useEditorStore } from '../../store/editorStore';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { TemplateActionButton } from './TemplateActionButton';
import { TemplateDialog } from './TemplateDialog';
import { DeleteConfirmationDialog } from './DeleteConfirmationDialog';
import { toast } from 'react-hot-toast';

export const TemplateManagement: React.FC = () => {
  const { 
    templates, 
    parameters,
    parameterValues, 
    isTemplateLoading, 
    isTemplateActionLoading,
    fetchTemplates, 
    fetchParameters,
    createTemplate, 
    updateTemplate, 
    deleteTemplate,
    lastTemplatesFetch 
  } = useEditorStore();

  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedTemplateData, setSelectedTemplateData] = useState<any>(null);
  
  // Keep track of mount status
  const isMounted = useRef(false);
  const hasFetchedInitialData = useRef(false);

  // Check if we need to fetch templates based on cache
  const needsFreshTemplateData = () => {
    // Check if we have templates in state already
    if (templates.length > 0) {
      // If we have templates and they were loaded recently (within 5 minutes), no need to fetch
      const TEMPLATE_REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes
      return Date.now() - lastTemplatesFetch > TEMPLATE_REFRESH_INTERVAL;
    }
    
    // If no templates, we need to fetch
    return true;
  };

  // Load templates and parameters on component mount - optimized to use cache
  useEffect(() => {
    // Mark component as mounted
    isMounted.current = true;
    
    const loadInitialData = async () => {
      // Don't load if we've already loaded or another fetch is in progress
      if (hasFetchedInitialData.current || isTemplateLoading) {
        return;
      }
      
      // Only fetch templates if needed
      if (needsFreshTemplateData()) {
        await fetchTemplates();
      }
      
      // Fetch parameters only once per session
      await fetchParameters();
      
      // Mark as fetched
      if (isMounted.current) {
        hasFetchedInitialData.current = true;
      }
    };
    
    loadInitialData();
    
    // Cleanup function
    return () => {
      isMounted.current = false;
    };
  }, [fetchTemplates, fetchParameters, isTemplateLoading]);

  const handleCreateTemplate = async (templateData: any) => {
    try {
      await createTemplate(templateData);
      toast.success('Template created successfully');
      setIsEditDialogOpen(false);
      setSelectedTemplate(null);
      setSelectedTemplateData(null);
    } catch (error) {
      toast.error('Failed to create template');
      console.error('Error creating template:', error);
    }
  };

  const handleUpdateTemplate = async (templateData: any) => {
    if (selectedTemplate) {
      try {
        await updateTemplate(selectedTemplate, templateData);
        toast.success('Template updated successfully');
        setIsEditDialogOpen(false);
        setSelectedTemplate(null);
        setSelectedTemplateData(null);
      } catch (error) {
        toast.error('Failed to update template');
        console.error('Error updating template:', error);
      }
    }
  };

  const handleDeleteConfirm = async () => {
    if (selectedTemplate) {
      try {
        await deleteTemplate(selectedTemplate);
        toast.success('Template deleted successfully');
        setIsDeleteDialogOpen(false);
        setSelectedTemplate(null);
        setSelectedTemplateData(null);
      } catch (error) {
        toast.error('Failed to delete template');
        console.error('Error deleting template:', error);
      }
    }
  };

  const openEditDialog = (template?: any) => {
    setSelectedTemplateData(template || null);
    setSelectedTemplate(template?.template_id || null);
    setIsEditDialogOpen(true);
  };

  const openDeleteDialog = (template: any) => {
    setSelectedTemplateData(template);
    setSelectedTemplate(template.template_id);
    setIsDeleteDialogOpen(true);
  };

  // Handle manual refresh of templates
  const handleRefreshTemplates = () => {
    fetchTemplates(undefined, undefined, undefined, true);
    toast.success('Templates refreshed');
  };

  return (
    <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      {/* Loading overlays */}
      {isTemplateLoading && (
        <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 flex items-center justify-center z-50">
          <LoadingSpinner size="lg" />
        </div>
      )}

      {/* Header with create button and refresh option */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Template Management</h2>
        <div className="flex gap-2">
          <button 
            onClick={handleRefreshTemplates}
            disabled={isTemplateLoading}
            className="px-3 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg disabled:opacity-50"
          >
            Refresh
          </button>
          <TemplateActionButton
            onClick={() => openEditDialog()}
            isLoading={isTemplateActionLoading}
            variant="primary"
            className="px-4 py-2 text-white bg-blue-600 hover:bg-blue-700 rounded-lg"
          >
            Create Template
          </TemplateActionButton>
        </div>
      </div>

      {/* Template list */}
      <div className="space-y-4">
        {templates.map(template => (
          <div 
            key={template.template_id} 
            className="flex p-4 border dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="flex-shrink-0 w-24 h-24 mr-4">
              {template.template_image_url && (
                <img 
                  src={template.template_image_url} 
                  alt={template.name}
                  className="w-full h-full object-cover rounded"
                />
              )}
            </div>
            <div className="flex-grow">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{template.name}</h3>
                  <p className="text-gray-600 dark:text-gray-300">{template.description}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Type: {template.template_type}</p>
                </div>
                <div className="flex gap-2">
                  <TemplateActionButton
                    onClick={() => openEditDialog(template)}
                    isLoading={isTemplateActionLoading && selectedTemplate === template.template_id}
                    variant="secondary"
                  >
                    Edit
                  </TemplateActionButton>
                  <TemplateActionButton
                    onClick={() => openDeleteDialog(template)}
                    isLoading={isTemplateActionLoading && selectedTemplate === template.template_id}
                    variant="danger"
                  >
                    Delete
                  </TemplateActionButton>
                </div>
              </div>
              {/* Display parameters */}
              <div className="mt-2">
                <p className="text-sm text-gray-500 dark:text-gray-300">Parameters:</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {template.parameters?.sort((a: any, b: any) => 
                  a.display_name.localeCompare(b.display_name)
                  ).map((param: any) => (
                  <span key={param.parameter_id} className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-2 py-1 rounded">
                    {param.display_name}: {param.values?.value || (param.values && param.values.length > 0 ? param.values.value : 'N/A')}
                  </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {templates.length === 0 && !isTemplateLoading && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-300">
          No templates found. Create your first template to get started.
        </div>
      )}

      {/* Edit/Create Dialog */}
      {isEditDialogOpen && (
        <TemplateDialog
          isOpen={isEditDialogOpen}
          onClose={() => {
            setIsEditDialogOpen(false);
            setSelectedTemplate(null);
            setSelectedTemplateData(null);
          }}
          onSubmit={selectedTemplate ? handleUpdateTemplate : handleCreateTemplate}
          template={selectedTemplateData}
          parameters={parameters}
          parameterValues={parameterValues}
          isLoading={isTemplateActionLoading}
        />
      )}

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmationDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => {
          setIsDeleteDialogOpen(false);
          setSelectedTemplate(null);
          setSelectedTemplateData(null);
        }}
        onConfirm={handleDeleteConfirm}
        isLoading={isTemplateActionLoading}
        templateName={selectedTemplateData?.name || ''}
      />
    </div>
  );
};