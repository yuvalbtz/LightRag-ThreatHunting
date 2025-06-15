import React, { useState, useEffect } from 'react';

interface FieldSelectionProps {
    fileContent: string;
    onFieldsSelected: (fields: {
        sourceColumn: string;
        targetColumn: string;
        relationshipColumns: string[];
    }) => void;
}

const FieldSelection: React.FC<FieldSelectionProps> = ({ fileContent, onFieldsSelected }) => {
    const [availableFields, setAvailableFields] = useState<string[]>([]);
    const [selectedFields, setSelectedFields] = useState({
        sourceColumn: '',
        targetColumn: '',
        relationshipColumns: [] as string[]
    });

    useEffect(() => {
        // Parse CSV header to get available fields
        const lines = fileContent.split('\n');
        if (lines.length > 0) {
            const headers = lines[0].split(',').map(header => header.trim());
            setAvailableFields(headers);
        }
    }, [fileContent]);

    const handleFieldChange = (fieldType: 'source' | 'target', value: string) => {
        setSelectedFields(prev => ({
            ...prev,
            [fieldType === 'source' ? 'sourceColumn' : 'targetColumn']: value
        }));
    };

    const handleRelationshipChange = (field: string) => {
        setSelectedFields(prev => {
            const newRelationships = prev.relationshipColumns.includes(field)
                ? prev.relationshipColumns.filter(f => f !== field)
                : [...prev.relationshipColumns, field];

            return {
                ...prev,
                relationshipColumns: newRelationships
            };
        });
    };

    const handleSubmit = () => {
        onFieldsSelected(selectedFields);
    };

    return (
        <div className="w-full max-w-xl mx-auto space-y-6">
            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Source Column</label>
                    <select
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        value={selectedFields.sourceColumn}
                        onChange={(e) => handleFieldChange('source', e.target.value)}
                    >
                        <option value="">Select source column</option>
                        {availableFields.map(field => (
                            <option key={field} value={field}>{field}</option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700">Target Column</label>
                    <select
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        value={selectedFields.targetColumn}
                        onChange={(e) => handleFieldChange('target', e.target.value)}
                    >
                        <option value="">Select target column</option>
                        {availableFields.map(field => (
                            <option key={field} value={field}>{field}</option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700">Relationship Columns</label>
                    <div className="mt-2 space-y-2">
                        {availableFields.map(field => (
                            <div key={field} className="flex items-center">
                                <input
                                    type="checkbox"
                                    id={field}
                                    checked={selectedFields.relationshipColumns.includes(field)}
                                    onChange={() => handleRelationshipChange(field)}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <label htmlFor={field} className="ml-2 block text-sm text-gray-900">
                                    {field}
                                </label>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <button
                onClick={handleSubmit}
                disabled={!selectedFields.sourceColumn || !selectedFields.targetColumn}
                className={`w-full py-2 px-4 rounded-md text-white font-medium
          ${(!selectedFields.sourceColumn || !selectedFields.targetColumn)
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 hover:bg-blue-700'}`}
            >
                Generate Graph
            </button>
        </div>
    );
};

export default FieldSelection; 