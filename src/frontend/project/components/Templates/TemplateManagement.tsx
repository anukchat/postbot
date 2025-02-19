import React, { useState, useEffect } from 'react';
import { useEditorStore } from '../../store/editorStore';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { TemplateActionButton } from './TemplateActionButton';

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
    deleteTemplate 
  } = useEditorStore();

  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);

  // Load templates on component mount
  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  const handleCreateTemplate = async (templateData: any) => {
    await createTemplate(templateData);
    setSelectedTemplate(null);
  };

  const handleUpdateTemplate = async (templateId: string, templateData: any) => {
    await updateTemplate(templateId, templateData);
    setSelectedTemplate(null);
  };

  const handleDeleteTemplate = async (templateId: string) => {
    await deleteTemplate(templateId);
    setSelectedTemplate(null);
  };

  return (
    <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      {/* Loading overlays */}
      {isTemplateLoading && (
        <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 flex items-center justify-center z-50">
          <LoadingSpinner size="lg" />
        </div>
      )}

      {/* Header with create button */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">Template Management</h2>
        <TemplateActionButton
          onClick={() => setSelectedTemplate('new')}
          isLoading={false}
          variant="primary"
        >
          Create Template
        </TemplateActionButton>
      </div>

      {/* Template list */}
      <div className="space-y-4">
        {templates.map(template => (
          <div 
            key={template.template_id} 
            className="p-4 border rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-semibold">{template.name}</h3>
                <p className="text-gray-600 dark:text-gray-300">{template.description}</p>
              </div>
              <div className="flex gap-2">
                <TemplateActionButton
                  onClick={() => setSelectedTemplate(template.template_id)}
                  isLoading={isTemplateActionLoading && selectedTemplate === template.template_id}
                  variant="secondary"
                >
                  Edit
                </TemplateActionButton>
                <TemplateActionButton
                  onClick={() => handleDeleteTemplate(template.template_id)}
                  isLoading={isTemplateActionLoading && selectedTemplate === template.template_id}
                  variant="danger"
                >
                  Delete
                </TemplateActionButton>
              </div>
            </div>
          </div>
        ))}
      </div>

      {templates.length === 0 && !isTemplateLoading && (
        <div className="text-center py-8 text-gray-500">
          No templates found. Create your first template to get started.
        </div>
      )}
    </div>
  );
};