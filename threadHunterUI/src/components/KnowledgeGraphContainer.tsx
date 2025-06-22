import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { createSystemMessage, useChat } from '../context/ChatContext';
import { useDarkMode } from '../context/ThemeContext';
import { useGraphWorker } from '../hooks/useGraphWorker';
import KnowledgeGraphControls from './KnowledgeGraphControls';
import KnowledgeGraphNetwork from './KnowledgeGraphNetwork';
import SelectionGraphFolder from './SelectionGraphFolder';
import KnowledgeGraphRenderingLoader from './KnowledgeGraphRenderingLoader';
import GraphSearchBox from './KnowledgeGraphSearchBox';
import KnowledgeGraphSearchBox from './KnowledgeGraphSearchBox';

export const KnowledgeGraphContainer: React.FC = () => {
    const isDarkMode = useDarkMode();
    const {
        graphData,
        isLoading,
        isRendering,
        dir_path,
        buildGraph,
        getGraphData,
        setGraphData,
        searchNodes,
        clearNodeHighlighting,
    } = useGraphWorker();
    const { sendMessage } = useChat();

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        const file = acceptedFiles[0];
        if (!file) return;

        if (!file.name.endsWith('.csv') && !file.name.endsWith('.pcap')) {
            sendMessage(createSystemMessage('Please upload a CSV or PCAP file'), dir_path);
            return;
        }

        try {
            await sendMessage(createSystemMessage(`Uploading your file '${file.name}' and building graph...`, false, dir_path), dir_path);
            try {
                await buildGraph(file);
                const newGraphData = await getGraphData(`./AppDbStore/${file.name.split('.')[0]}`);
                setGraphData(newGraphData);
                await sendMessage(createSystemMessage(`Successfully generated graph with ${newGraphData.nodes.length} nodes and ${newGraphData.edges.length} edges.`, false, dir_path), dir_path);
            } catch (error) {
                await sendMessage(createSystemMessage(`Error: Failed to process ${file.name}`, true, dir_path), dir_path);
            }
        } catch (error) {
            sendMessage(createSystemMessage(`Error: ${error instanceof Error ? error.message : 'Failed to process file'}`, true, dir_path), dir_path);
        } finally {
        }
    }, [buildGraph, getGraphData, sendMessage, setGraphData]);


    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'text/csv': ['.csv'],
            'application/vnd.tcpdump.pcap': ['.pcap']
        },
        noClick: !!graphData,
        noKeyboard: !!graphData
    });

    return (
        <div className={`w-1/3 border-r transition-colors duration-200 h-[100%] flex flex-col ${isDarkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'}`}>
            <div className="relative p-4 flex flex-col h-[100%]">
                <div className="flex flex-row items-center justify-between mb-2">
                    <h2 className={`text-lg font-semibold transition-colors duration-200 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                        Knowledge Graph
                    </h2>
                    <SelectionGraphFolder />
                </div>



                <div
                    {...getRootProps()}
                    className={`w-full flex-1 border-2 ${isDarkMode ? 'border-gray-700' : 'border-gray-200'} rounded-lg relative overflow-hidden ${graphData ? 'cursor-default' : 'cursor-pointer'}`}
                >
                    {/* Search Box - only show when graph data is available */}
                    {graphData && !isRendering && (
                        <KnowledgeGraphSearchBox />
                    )}
                    <input {...getInputProps()} />
                    <KnowledgeGraphNetwork />

                    {isRendering && (
                        <KnowledgeGraphRenderingLoader />
                    )}

                    {isLoading && (
                        <div className="absolute inset-0 bg-gray-900/50 backdrop-blur-sm flex items-center justify-center z-50">
                            <div className="text-center">
                                <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
                                <p className="text-white font-medium">Building Knowledge Graph...</p>
                                <p className="text-gray-300 text-sm mt-2">This may take a few moments</p>
                            </div>
                        </div>
                    )}

                    {!isLoading && !graphData && !isRendering && (
                        <div className={`absolute inset-0 flex flex-col items-center justify-center ${isDragActive
                            ? `${isDarkMode ? 'bg-blue-900/20' : 'bg-blue-500/10'}`
                            : `${isDarkMode ? 'bg-gray-800/50' : 'bg-gray-50/50'}`
                            } backdrop-blur-sm transition-all duration-200`}>
                            <div className={`text-center p-8 rounded-lg ${isDragActive
                                ? `${isDarkMode ? 'bg-gray-800/90 shadow-lg shadow-blue-500/20' : 'bg-white/90 shadow-lg'}`
                                : `${isDarkMode ? 'bg-gray-800/80' : 'bg-white/80'}`
                                } max-w-md`}>
                                <div className={`text-5xl mb-4 ${isDarkMode ? 'text-blue-400' : 'text-blue-500'}`}>📊</div>
                                <h3 className={`text-xl font-semibold mb-3 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                                    Upload Network Data
                                </h3>
                                <p className={`text-sm mb-4 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                                    Drag and drop your network data file here to visualize the knowledge graph
                                </p>
                                <div className={`p-4 border-2 border-dashed rounded-lg transition-colors duration-200 ${isDragActive
                                    ? `${isDarkMode ? 'border-blue-500 bg-blue-900/30' : 'border-blue-500 bg-blue-50'}`
                                    : `${isDarkMode ? 'border-gray-700 bg-gray-700/50' : 'border-gray-300 bg-gray-100'}`
                                    }`}>
                                    <div className={`text-4xl mb-2 ${isDarkMode ? 'text-blue-400' : 'text-blue-500'}`}>📁</div>
                                    {isDragActive ? (
                                        <p className={`font-medium ${isDarkMode ? 'text-blue-400' : 'text-blue-500'}`}>
                                            Drop your file here...
                                        </p>
                                    ) : (
                                        <div>
                                            <p className={`${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                                                Drag and drop your file here
                                            </p>
                                            <p className={`text-sm mt-1 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                                                Supported formats: CSV, PCAP
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    <KnowledgeGraphControls />
                </div>
            </div>
        </div>
    );
}; 