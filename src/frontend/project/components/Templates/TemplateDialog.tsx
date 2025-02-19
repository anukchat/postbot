import React, { useEffect, useState } from 'react';
import { Dialog } from '@headlessui/react';
import { Parameter, ParameterValue, Template, TemplateParameter } from '../../store/editorStore';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useEditorStore } from '../../store/editorStore';

interface TemplateDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (templateData: any) => Promise<void>;
  template: Template | null;
  parameters: Parameter[];
  parameterValues: Record<string, ParameterValue[]>;
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
  const { fetchParameterValues } = useEditorStore();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    template_type: 'default',
    template_image_url: '',
    parameters: [] as TemplateParameter[],
  });

  // Load parameter values for each parameter on mount
  useEffect(() => {
    parameters.forEach(param => {
      if (!parameterValues[param.parameter_id]) {
        fetchParameterValues(param.parameter_id);
      }
    });
  }, [parameters, parameterValues, fetchParameterValues]);

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
                  value: { parameter_id: parameterId, value_id: valueId, value }
                }
              : p
          )
        : [
            ...prev.parameters,
            {
              parameter_id: parameterId,
              name: parameters.find(p => p.parameter_id === parameterId)?.name || '',
              display_name: parameters.find(p => p.parameter_id === parameterId)?.display_name || '',
              value: { parameter_id: parameterId, value_id: valueId, value }
            }
          ]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  return (
    <Dialog open={isOpen} onClose={onClose} className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen">
        <div className="fixed inset-0 bg-black opacity-30" />

        <div className="relative bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full mx-4 p-6">
          <Dialog.Title className="text-xl font-semibold mb-4">
            {template ? 'Edit Template' : 'Create Template'}
          </Dialog.Title>

          <form onSubmit={handleSubmit} className="space-y-4">
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
              <label className="block text-sm font-medium mb-1">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                rows={3}
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

            <div>
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
                  className="mt-2 max-h-32 rounded"
                />
              )}
            </div>

            {/* Parameters */}
            <div className="space-y-4">
              <h3 className="font-medium">Parameters</h3>
              {parameters.map(param => (
                <div key={param.parameter_id} className="space-y-2">
                  <label className="block text-sm font-medium">
                    {param.display_name}
                    {param.is_required && <span className="text-red-500 ml-1">*</span>}
                  </label>
                  <select
                    value={formData.parameters.find(p => p.parameter_id === param.parameter_id)?.value.value_id || ''}
                    onChange={(e) => {
                      const selectedValue = parameterValues[param.parameter_id]?.find(v => v.value_id === e.target.value);
                      if (selectedValue) {
                        handleParameterChange(param.parameter_id, selectedValue.value_id, selectedValue.value);
                      }
                    }}
                    className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
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

            {/* Actions */}
            <div className="flex justify-end gap-2 mt-6">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg flex items-center"
                disabled={isLoading}
              >
                {isLoading && <LoadingSpinner size="sm" className="mr-2" />}
                {template ? 'Update' : 'Create'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Dialog>
  );
};