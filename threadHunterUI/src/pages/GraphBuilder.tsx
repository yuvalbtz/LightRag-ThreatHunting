import React, { useState } from 'react';
import FileUpload from '../components/FileUpload';
import FieldSelection from '../components/FieldSelection';
import { GraphVisualization } from '../components/GraphVisualization';

const GraphBuilder: React.FC = () => {
    const [step, setStep] = useState<'upload' | 'select' | 'visualize'>('upload');
    const [file, setFile] = useState<File | null>(null);
    const [fileContent, setFileContent] = useState<string>('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string>('');
    const [graphData, setGraphData] = useState<{
        nodes: any[];
        edges: any[];
    }>({ nodes: [], edges: [] });

    const handleFileUpload = async (uploadedFile: File) => {
        setFile(uploadedFile);
        const content = await uploadedFile.text();
        setFileContent(content);
        setStep('select');
    };

    const handleFieldsSelected = async (fields: {
        sourceColumn: string;
        targetColumn: string;
        relationshipColumns: string[];
    }) => {
        setLoading(true);
        setError('');
        try {
            const formData = new FormData();
            if (file) {
                formData.append('file', file);
            }
            formData.append('source_column', fields.sourceColumn);
            formData.append('target_column', fields.targetColumn);
            fields.relationshipColumns.forEach(column => {
                formData.append('relationship_columns', column);
            });

            // First, build the knowledge graph
            const response = await fetch('http://localhost:8000/build-kg', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Failed to build knowledge graph');
            }

            const buildResult = await response.json();
            console.log('Build result:', buildResult);

            // Then, get the graph data
            const graphResponse = await fetch('http://localhost:8000/graph-data');
            if (!graphResponse.ok) {
                const errorData = await graphResponse.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Failed to fetch graph data');
            }

            const data = await graphResponse.json();
            console.log('Graph data:', data);

            if (!data.nodes || !data.edges) {
                throw new Error('Invalid graph data format');
            }

            setGraphData(data);
            setStep('visualize');
        } catch (error) {
            console.error('Error:', error);
            setError(error instanceof Error ? error.message : 'An unexpected error occurred');
            setStep('select'); // Go back to selection step on error
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold text-center mb-8">Knowledge Graph Builder</h1>

            <div className="max-w-4xl mx-auto">
                {error && (
                    <div className="mb-4 p-4 bg-red-50 rounded-lg">
                        <p className="text-red-700">{error}</p>
                    </div>
                )}

                {step === 'upload' && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-semibold text-center">Upload Your Data</h2>
                        <FileUpload onFileUpload={handleFileUpload} />
                    </div>
                )}

                {step === 'select' && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-semibold text-center">Select Fields</h2>
                        <FieldSelection
                            fileContent={fileContent}
                            onFieldsSelected={handleFieldsSelected}
                        />
                    </div>
                )}

                {step === 'visualize' && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-semibold text-center">Knowledge Graph</h2>
                        <GraphVisualization
                            data={graphData}
                        />
                    </div>
                )}
            </div>
        </div>
    );
};

export default GraphBuilder; 