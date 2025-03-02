import React, { useEffect, useState } from 'react';
import { Dialog } from '@headlessui/react';
import { Template, TemplateParameter, TemplateParameterValue } from '../../store/editorStore';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useEditorStore } from '../../store/editorStore';

interface TemplateDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (templateData: Partial<Template>) => Promise<void>;
  template: Template | null;
  parameters: TemplateParameter[];
  parameterValues: Record<string, TemplateParameterValue[]>;
  isLoading: boolean;
}

export const TemplateDialog: React.FC<TemplateDialogProps> = ({
  isOpen,
  onClose,
  onSubmit,
  template,
  parameters,
  parameterValues,
  isLoading,
}) => {
  const { fetchParameters } = useEditorStore();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    template_type: 'default',
    template_image_url: '',
    parameters: [] as TemplateParameter[],
  });
  
  // Load all parameters with their values at once when needed
  useEffect(() => {
    // Only fetch parameters if we don't have data for all parameters
    const missingParameterValues = parameters.some(param => 
      !parameterValues[param.parameter_id] || parameterValues[param.parameter_id].length === 0
    );
    
    if (missingParameterValues) {
      fetchParameters();
    }
  }, [parameters, parameterValues, fetchParameters]);

  // Initialize form with template data if editing
  useEffect(() => {
    if (template) {
      setFormData({
        name: template.name,
        description: template.description || '',
        template_type: template.template_type,
        template_image_url: template.template_image_url || '',
        parameters: template.parameters,
      });
    } else {
      setFormData({
        name: '',
        description: '',
        template_type: 'default',
        template_image_url: '',
        parameters: [],
      });
    }
  }, [template]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleParameterChange = (parameterId: string, valueId: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      parameters: prev.parameters.some(p => p.parameter_id === parameterId)
        ? prev.parameters.map(p => 
            p.parameter_id === parameterId 
              ? {
                  ...p,
                  values: { 
                    value_id: valueId, 
                    value: value
                  }
                }
              : p
          )
        : [
            ...prev.parameters,
            {
              parameter_id: parameterId,
              name: parameters.find(p => p.parameter_id === parameterId)?.name || '',
              display_name: parameters.find(p => p.parameter_id === parameterId)?.display_name || '',
              is_required: parameters.find(p => p.parameter_id === parameterId)?.is_required || false,
              values: {
                value_id: valueId,
                value: value
              }
            }
          ]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  // Helper function to get parameter value ID from template parameters
  const getParameterValueId = (parameterId: string) => {
    const parameter = formData.parameters.find(p => p.parameter_id === parameterId);
    return parameter?.values?.value_id || '';
  };

  return (
    <Dialog 
      open={isOpen} 
      onClose={onClose} 
      className="fixed inset-0 z-50"
    >
      <div className="fixed inset-0 flex items-center justify-center">
        <div className="fixed inset-0 bg-black/30 backdrop-blur-sm" aria-hidden="true" />

        <div className="relative bg-white dark:bg-gray-800 rounded-lg w-[90vw] max-w-4xl max-h-[90vh] overflow-hidden">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <Dialog.Title className="text-xl font-semibold">
              {template ? 'Edit Template' : 'Create Template'}
            </Dialog.Title>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full"
              aria-label="Close dialog"
            >
              <svg
                className="w-5 h-5 text-gray-500 dark:text-gray-400"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="overflow-auto p-6 max-h-[calc(90vh-140px)]">
            <div className="grid grid-cols-2 gap-6 mb-6">
              {/* Basic Info */}
              <div>
                <label className="block text-sm font-medium mb-1">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Template Type</label>
                <select
                  value={formData.template_type}
                  onChange={(e) => handleInputChange('template_type', e.target.value)}
                  className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                  required
                >
                  <option value="default">Default</option>
                  <option value="custom">Custom</option>
                </select>
              </div>

              <div className="col-span-2">
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                  rows={2}
                />
              </div>

              <div className="col-span-2">
                <label className="block text-sm font-medium mb-1">Image URL</label>
                <input
                  type="url"
                  value={formData.template_image_url}
                  onChange={(e) => handleInputChange('template_image_url', e.target.value)}
                  className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                />
                {formData.template_image_url && (
                  <img
                    src={formData.template_image_url}
                    alt="Template preview"
                    className="mt-2 h-20 rounded object-cover"
                  />
                )}
              </div>
            </div>

            {/* Parameters Grid */}
            <div className="space-y-4">
              <h3 className="font-medium text-lg">Parameters</h3>
              
              {parameters.length === 0 && (
                <div className="flex items-center justify-center p-4 text-gray-500">
                  <LoadingSpinner size="md" className="mr-2" />
                  <span>Loading parameters...</span>
                </div>
              )}
              
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {parameters.map(param => (
                  <div key={param.parameter_id} className="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg">
                    <label className="block text-sm font-medium mb-2">
                      {param.display_name}
                      {param.is_required && <span className="text-red-500 ml-1">*</span>}
                    </label>
                    <select
                      value={getParameterValueId(param.parameter_id)}
                      onChange={(e) => {
                        const selectedValue = parameterValues[param.parameter_id]?.find(v => v.value_id === e.target.value);
                        if (selectedValue) {
                          handleParameterChange(param.parameter_id, selectedValue.value_id, selectedValue.value);
                        }
                      }}
                      className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600 text-sm"
                      required={param.is_required}
                    >
                      <option value="">Select a value</option>
                      {parameterValues[param.parameter_id]?.map(value => (
                        <option key={value.value_id} value={value.value_id}>
                          {value.value}
                        </option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>
            </div>
          </form>

          {/* Fixed Footer */}
          <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-800/90 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg flex items-center"
              disabled={isLoading}
            >
              {isLoading && <LoadingSpinner size="sm" className="mr-2" />}
              {template ? 'Update' : 'Create'}
            </button>
          </div>
        </div>
      </div>
    </Dialog>
  );
};