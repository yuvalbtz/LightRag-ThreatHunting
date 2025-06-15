import {
    ArrowPathIcon,
    ArrowsPointingOutIcon,
    MagnifyingGlassMinusIcon,
    MagnifyingGlassPlusIcon
} from '@heroicons/react/24/outline';
import { Button } from '@heroui/button';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { DataSet } from 'vis-data';
import { Edge, Network, Node } from 'vis-network';
import { createSystemMessage, useChat } from '../context/ChatContext';
import { useDarkMode } from '../context/ThemeContext';
import { useGraphWorker } from '../hooks/useGraphWorker';

const CLUSTER_THRESHOLD = 50; // Adjust this value based on your needs

export const KnowledgeGraphContainer: React.FC = () => {
    const isDarkMode = useDarkMode();
    const { graphData, isLoading, resetGraph, buildGraph, getGraphData, setGraphData } = useGraphWorker();
    const { sendMessage } = useChat();
    const [isRendering, setIsRendering] = useState(false);
    const [stabilizationProgress, setStabilizationProgress] = useState(0);
    const networkRef = useRef<HTMLDivElement>(null);
    const networkInstance = useRef<Network | null>(null);

    useEffect(() => {
        if (networkRef.current && graphData) {
            setIsRendering(true);
            const nodes = new DataSet<Node>(graphData.nodes);
            const edges = new DataSet<Edge>(graphData.edges);

            const options = {
                nodes: {
                    shape: 'dot',
                    size: 16,
                    font: {
                        size: 12,
                        color: isDarkMode ? '#ffffff' : '#000000'
                    },
                    color: {
                        background: isDarkMode ? '#4B5563' : '#E5E7EB',
                        border: isDarkMode ? '#6B7280' : '#9CA3AF',
                        highlight: {
                            background: isDarkMode ? '#60A5FA' : '#3B82F6',
                            border: isDarkMode ? '#93C5FD' : '#60A5FA'
                        }
                    }
                },
                edges: {
                    width: 1,
                    color: {
                        color: isDarkMode ? '#6B7280' : '#9CA3AF',
                        highlight: isDarkMode ? '#93C5FD' : '#60A5FA'
                    },
                    smooth: {
                        enabled: true,
                        type: 'continuous',
                        roundness: 0.5
                    }
                },
                physics: {
                    stabilization: {
                        iterations: 100,
                        updateInterval: 25
                    },
                    barnesHut: {
                        gravitationalConstant: -2000,
                        springLength: 200
                    }
                },
                interaction: {
                    hover: true,
                    tooltipDelay: 200
                },
                groups: {
                    hub: {
                        shape: 'box',
                        borderWidth: 3,
                        color: {
                            background: isDarkMode ? '#374151' : '#D1D5DB',
                            border: isDarkMode ? '#4B5563' : '#9CA3AF'
                        }
                    }
                }
            };

            if (networkInstance.current) {
                networkInstance.current.destroy();
            }

            const network = new Network(networkRef.current, { nodes, edges }, options);
            networkInstance.current = network;

            network.on('stabilizationProgress', (params) => {
                const progress = Math.min(100, Math.round((params.iterations / params.total) * 100));
                setStabilizationProgress(progress);
            });

            network.once('stabilizationIterationsDone', () => {
                setStabilizationProgress(100);
                setIsRendering(false);
                const clusterOptions = {
                    joinCondition: (node: Node) => {
                        return node.value !== undefined && node.value > CLUSTER_THRESHOLD;
                    },
                    processProperties: (clusterNode: any, childNodes: any[]) => {
                        let totalMass = 0;
                        for (const node of childNodes) {
                            totalMass += node.mass || 1;
                        }
                        clusterNode.mass = totalMass;
                        clusterNode.group = 'hub';
                        return clusterNode;
                    },
                    clusterNodeProperties: {
                        id: 'cluster:hub',
                        label: 'Hub Cluster',
                        group: 'hub'
                    }
                };

                network.cluster(clusterOptions);
            });

            network.on('click', (params) => {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    if (nodeId.toString().startsWith('cluster:')) {
                        network.openCluster(nodeId);
                    }
                }
            });

            return () => {
                if (networkInstance.current) {
                    networkInstance.current.destroy();
                }
                setStabilizationProgress(0);
            };
        } else if (!graphData) {
            if (networkInstance.current) {
                networkInstance.current.destroy();
                networkInstance.current = null;
            }
            setIsRendering(false);
            setStabilizationProgress(0);
        }
    }, [graphData]);

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        const file = acceptedFiles[0];
        if (!file) return;

        if (!file.name.endsWith('.csv') && !file.name.endsWith('.pcap')) {
            sendMessage(createSystemMessage('Please upload a CSV or PCAP file'));
            return;
        }

        try {
            await sendMessage(createSystemMessage(`Uploading your file '${file.name}' and building graph...`));
            try {
                await buildGraph(file);
                const newGraphData = await getGraphData();
                setGraphData(newGraphData);
                await sendMessage(createSystemMessage(`Successfully generated graph with ${newGraphData.nodes.length} nodes and ${newGraphData.edges.length} edges.`));
            } catch (error) {
                await sendMessage(createSystemMessage(`Error: Failed to process ${file.name}`));
            }
        } catch (error) {
            sendMessage(createSystemMessage(`Error: ${error instanceof Error ? error.message : 'Failed to process file'}`));
        } finally {
            setIsRendering(false);
        }
    }, [buildGraph, getGraphData, sendMessage, setGraphData]);

    const handleReset = async () => {
        if (networkInstance.current) {
            networkInstance.current.destroy();
            networkInstance.current = null;
        }
        resetGraph();
        setIsRendering(false);
        setStabilizationProgress(0);
        await sendMessage(createSystemMessage('Graph has been reset. You can now drag and drop a new file.'));
    };

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
                <h2 className={`text-lg font-semibold mb-4 transition-colors duration-200 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                    Knowledge Graph
                </h2>
                <div
                    {...getRootProps()}
                    className={`w-full flex-1 border-2 ${isDarkMode ? 'border-gray-700' : 'border-gray-200'} rounded-lg relative overflow-hidden ${graphData ? 'cursor-default' : 'cursor-pointer'}`}
                >
                    <input {...getInputProps()} />
                    <div ref={networkRef} className="w-full h-[100%]" />

                    {isRendering && (
                        <div className="absolute inset-0 flex items-center justify-center z-10">
                            <div className="w-1/3 h-0.5 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-blue-500 rounded-full"
                                    style={{
                                        width: `${stabilizationProgress}%`,
                                        transition: 'width 50ms linear'
                                    }}
                                />
                            </div>
                        </div>
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

                    {!isLoading && !graphData && (
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

                    {graphData && (
                        <div className="absolute m-auto p-1 left-0 right-0 rounded-full bottom-0 w-fit px-4 mb-1 flex gap-4 justify-center items-center z-20 ${isDarkMode ? 'bg-gray-900/80' : 'bg-white/90'} backdrop-blur-md">
                            <Button size="lg" isIconOnly variant="light" title="Zoom In" className={isDarkMode ? 'text-blue-200 hover:bg-gray-800' : 'text-blue-700 hover:bg-blue-100'} onPress={() => {
                                if (networkInstance.current) {
                                    networkInstance.current.moveTo({
                                        scale: networkInstance.current.getScale() * 1.2
                                    });
                                }
                            }}>
                                <MagnifyingGlassPlusIcon className="w-7 h-7" />
                            </Button>
                            <Button size="lg" isIconOnly variant="light" title="Zoom Out" className={isDarkMode ? 'text-blue-200 hover:bg-gray-800' : 'text-blue-700 hover:bg-blue-100'} onPress={() => {
                                if (networkInstance.current) {
                                    networkInstance.current.moveTo({
                                        scale: networkInstance.current.getScale() * 0.8
                                    });
                                }
                            }}>
                                <MagnifyingGlassMinusIcon className="w-7 h-7" />
                            </Button>
                            <Button size="lg" isIconOnly variant="light" title="Fit to View" className={isDarkMode ? 'text-blue-200 hover:bg-gray-800' : 'text-blue-700 hover:bg-blue-100'} onPress={() => {
                                if (networkInstance.current) {
                                    networkInstance.current.fit({
                                        animation: {
                                            duration: 1000,
                                            easingFunction: 'easeInOutQuad'
                                        }
                                    });
                                }
                            }}>
                                <ArrowsPointingOutIcon className="w-7 h-7" />
                            </Button>
                            <Button size="lg" isIconOnly variant="light" title="Reset Graph" className={isDarkMode ? 'text-blue-200 hover:bg-gray-800' : 'text-blue-700 hover:bg-blue-100'} onPress={handleReset}>
                                <ArrowPathIcon className="w-7 h-7" />
                            </Button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}; 