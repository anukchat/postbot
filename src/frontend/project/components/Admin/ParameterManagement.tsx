import { useState, useEffect } from 'react';
import { useEditorStore, Parameter, ParameterValue } from '../../store/editorStore';
import { PlusCircle, Edit, Trash2, Plus } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { Dialog } from '@headlessui/react';

export const ParameterManagement = () => {
  const { 
    parameters, 
    parameterValues,
    createParameter,
    updateParameter,
    deleteParameter,
    createParameterValue,
    updateParameterValue,
    deleteParameterValue,
    fetchParameters,
    isParametersLoading,
    parametersError
  } = useEditorStore();
  
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingParameter, setEditingParameter] = useState<Parameter | null>(null);
  const [newParameter, setNewParameter] = useState<Omit<Parameter, 'parameter_id' | 'created_at'>>({
    name: '',
    display_name: '',
    description: '',
    is_required: false,
    values: []
  });
  
  const [isValueModalOpen, setIsValueModalOpen] = useState(false);
  const [selectedParameterId, setSelectedParameterId] = useState<string | null>(null);
  const [editingValue, setEditingValue] = useState<ParameterValue | null>(null);
  const [newValue, setNewValue] = useState<Omit<ParameterValue, 'value_id' | 'created_at'>>({
    value: '',
    display_order: 0
  });

  // Update the useEffect to properly handle parameter fetching
  useEffect(() => {
    // Immediately fetch parameters when component mounts
    fetchParameters().catch(error => {
      console.error('Error fetching parameters:', error);
      toast.error('Failed to load parameters');
    });
  }, []); // Empty dependency array since we want to fetch only on mount

  const handleCreateParameter = async () => {
    try {
      if (!newParameter.name || !newParameter.display_name) {
        toast.error('Name and Display Name are required');
        return;
      }
      await createParameter(newParameter);
      // Don't need to fetch parameters again since createParameter updates the local state
      setIsCreateModalOpen(false);
      setNewParameter({ name: '', display_name: '', description: '', is_required: false, values: [] });
      toast.success('Parameter created successfully');
    } catch (error) {
      console.error('Error creating parameter:', error);
      toast.error('Failed to create parameter');
    }
  };

  const handleUpdateParameter = async () => {
    if (!editingParameter) return;
    try {
      if (!newParameter.name || !newParameter.display_name) {
        toast.error('Name and Display Name are required');
        return;
      }
      await updateParameter(editingParameter.parameter_id, newParameter);
      // Don't need to fetch parameters again since updateParameter updates the local state
      setEditingParameter(null);
      // setNewParameter({ name: '', display_name: '', description: '', is_required: false, values: [] });
      toast.success('Parameter updated successfully');
    } catch (error) {
      console.error('Error updating parameter:', error);
      toast.error('Failed to update parameter');
    }
  };

  const handleDeleteParameter = async (parameterId: string) => {
    try {
      await deleteParameter(parameterId);
      // Don't need to fetch parameters again since deleteParameter updates the local state
      toast.success('Parameter deleted successfully');
    } catch (error) {
      console.error('Error deleting parameter:', error);
      toast.error('Failed to delete parameter');
    }
  };

  const handleCreateValue = async () => {
    if (!selectedParameterId) return;
    try {
      if (!newValue.value) {
        toast.error('Value is required');
        return;
      }
      await createParameterValue(selectedParameterId, newValue);
      // Don't need to fetch parameters again since createParameterValue updates the local state
      setIsValueModalOpen(false);
      setNewValue({ value: '', display_order: 0 });
      toast.success('Value added successfully');
    } catch (error) {
      console.error('Error creating value:', error);
      toast.error('Failed to add value');
    }
  };

  const handleUpdateValue = async () => {
    if (!selectedParameterId || !editingValue) return;
    try {
      if (!newValue.value) {
        toast.error('Value is required');
        return;
      }
      await updateParameterValue(selectedParameterId, editingValue.value_id, newValue);
      // Don't need to fetch parameters again since updateParameterValue updates the local state
      setEditingValue(null);
      setIsValueModalOpen(false);
      setNewValue({ value: '', display_order: 0 });
      toast.success('Value updated successfully');
    } catch (error) {
      console.error('Error updating value:', error);
      toast.error('Failed to update value');
    }
  };

  const handleDeleteValue = async (parameterId: string, valueId: string) => {
    try {
      await deleteParameterValue(parameterId, valueId);
      // Don't need to fetch parameters again since deleteParameterValue updates the local state
      toast.success('Value deleted successfully');
    } catch (error) {
      console.error('Error deleting value:', error);
      toast.error('Failed to delete value');
    }
  };

  // Add a loading indicator that shows during initial load
  if (isParametersLoading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // Show error state if there's an error
  if (parametersError) {
    return (
      <div className="flex flex-col items-center justify-center h-48 text-red-500">
        <p className="mb-4">{parametersError}</p>
        <button 
          onClick={() => fetchParameters()}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    );
  }

  // Rest of the component remains unchanged
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Parameters</h2>
        <button 
          onClick={() => setIsCreateModalOpen(true)}
          className="inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          <PlusCircle className="w-4 h-4 mr-2" />
          Create Parameter
        </button>
      </div>

      {/* Parameter list */}
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {parameters
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .map((parameter) => (
          <div key={parameter.parameter_id} className="p-6">
            <div className="mb-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{parameter.display_name}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{parameter.description}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-gray-400">ID: {parameter.parameter_id}</span>
                    {parameter.is_required && (
                      <span className="px-2 py-0.5 text-xs rounded-full bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300">
                        Required
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-gray-700 dark:text-gray-300"
                    onClick={() => {
                      setEditingParameter(parameter);
                      setNewParameter({
                        name: parameter.name,
                        display_name: parameter.display_name,
                        description: parameter.description || '',
                        is_required: parameter.is_required,
                        values: parameter.values || []
                      });
                    }}
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-red-600"
                    onClick={() => handleDeleteParameter(parameter.parameter_id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
            
            {/* Parameter values table */}
            <div className="mt-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Parameter Values</h4>
                <button
                  onClick={() => {
                    setSelectedParameterId(parameter.parameter_id);
                    setIsValueModalOpen(true);
                    // Calculate next display order by finding max and adding 1
                    const maxDisplayOrder = Math.max(
                      0,
                      ...(parameter.values || []).map(v => v.display_order)
                    );
                    setNewValue({
                      value: '',
                      display_order: maxDisplayOrder + 1
                    });
                  }}
                  className="inline-flex items-center px-3 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Value
                </button>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
                  <thead className="bg-gray-100 dark:bg-gray-700">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Value</th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Display Order</th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Created At</th>
                      <th scope="col" className="px-6 py-3 relative">
                        <span className="sr-only">Actions</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {(parameter.values || []).map((value) => (
                      <tr key={value.value_id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{value.value}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{value.display_order}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{new Date(value.created_at).toLocaleDateString()}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex justify-end gap-2">
                            <button
                              className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                              onClick={() => {
                                setSelectedParameterId(parameter.parameter_id);
                                setEditingValue(value);
                                setNewValue({
                                  value: value.value,
                                  display_order: value.display_order
                                });
                                setIsValueModalOpen(true);
                              }}
                            >
                              Edit
                            </button>
                            <button 
                              className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                              onClick={() => handleDeleteValue(parameter.parameter_id, value.value_id)}
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    
                    {/* Show empty state if no values */}
                    {(!parameter.values || parameter.values.length === 0) && (
                      <tr>
                        <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                          No values added yet
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ))}
        
        {/* Empty state for no parameters */}
        {parameters.length === 0 && !isParametersLoading && (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            No parameters found. Create your first parameter to get started.
          </div>
        )}
      </div>

      {/* Modals */}
      {/* Parameter Create/Edit Modal */}
      <Dialog 
        as="div"
        className="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto"
        open={isCreateModalOpen || !!editingParameter} 
        onClose={() => {
          setIsCreateModalOpen(false);
          setEditingParameter(null);
        }}
      >
        <Dialog.Panel className="w-full max-w-md bg-white dark:bg-gray-800 rounded-lg shadow-xl">
          <div className="p-6">
            <Dialog.Title className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
              {editingParameter ? 'Edit Parameter' : 'Create Parameter'}
            </Dialog.Title>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-900 dark:text-gray-100">Name</label>
                <input
                  type="text"
                  value={newParameter.name}
                  onChange={(e) => setNewParameter({ ...newParameter, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-900 dark:text-gray-100">Display Name</label>
                <input
                  type="text"
                  value={newParameter.display_name}
                  onChange={(e) => setNewParameter({ ...newParameter, display_name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-900 dark:text-gray-100">Description</label>
                <textarea
                  value={newParameter.description}
                  onChange={(e) => setNewParameter({ ...newParameter, description: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                  rows={3}
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="isRequired"
                  checked={newParameter.is_required}
                  onChange={(e) => setNewParameter({ ...newParameter, is_required: e.target.checked })}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="isRequired" className="ml-2 text-sm text-gray-900 dark:text-gray-100">Required</label>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => {
                  setIsCreateModalOpen(false);
                  setEditingParameter(null);
                }}
                className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={editingParameter ? handleUpdateParameter : handleCreateParameter}
                className="px-4 py-2 text-sm text-white bg-blue-500 hover:bg-blue-600 rounded-lg"
              >
                {editingParameter ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </Dialog.Panel>
      </Dialog>

      {/* Value Create/Edit Modal */}
      <Dialog 
        as="div"
        className="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto"
        open={isValueModalOpen} 
        onClose={() => {
          setIsValueModalOpen(false);
          setEditingValue(null);
          setSelectedParameterId(null);
          setNewValue({ value: '', display_order: 0 });
        }}
      >
        <Dialog.Panel className="w-full max-w-md bg-white dark:bg-gray-800 rounded-lg shadow-xl">
          <div className="p-6">
            <Dialog.Title className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
              {editingValue ? 'Edit Value' : 'Add Value'}
            </Dialog.Title>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-900 dark:text-gray-100">Value</label>
                <input
                  type="text"
                  value={newValue.value}
                  onChange={(e) => setNewValue({ ...newValue, value: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter value"
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-900 dark:text-gray-100">Display Order</label>
                <input
                  type="number"
                  value={newValue.display_order}
                  onChange={(e) => setNewValue({ ...newValue, display_order: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                  min="0"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => {
                  setIsValueModalOpen(false);
                  setEditingValue(null);
                  setSelectedParameterId(null);
                  setNewValue({ value: '', display_order: 0 });
                }}
                className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={editingValue ? handleUpdateValue : handleCreateValue}
                disabled={!newValue.value.trim()}
                className="px-4 py-2 text-sm text-white bg-blue-500 hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg"
              >
                {editingValue ? 'Update' : 'Add'}
              </button>
            </div>
          </div>
        </Dialog.Panel>
      </Dialog>
    </div>
  );
};