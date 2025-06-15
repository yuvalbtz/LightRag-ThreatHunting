import React, { useEffect, useRef, useState } from 'react';
import { Network, DataSet, Edge, Node } from 'vis-network';
import { GraphNode, GraphEdge, GraphData } from '../types';
import { useGraphWorker } from '../hooks/useGraphWorker';

interface GraphVisualizationProps {
    data: GraphData;
    onNodeClick?: (nodeId: string) => void;
    searchQuery?: string;
}

export const GraphVisualization: React.FC<GraphVisualizationProps> = ({
    data,
    onNodeClick,
    searchQuery
}) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const networkRef = useRef<Network | null>(null);
    const [processedData, setProcessedData] = useState<GraphData>(data);
    const { processGraphData, searchNodes } = useGraphWorker();

    // Process graph data using Web Worker
    useEffect(() => {
        const processData = async () => {
            const processed = await processGraphData(data);
            setProcessedData(processed);
        };
        processData();
    }, [data, processGraphData]);

    // Handle search using Web Worker
    useEffect(() => {
        const handleSearch = async () => {
            if (!searchQuery) {
                setProcessedData(data);
                return;
            }

            const searchResults = await searchNodes(data.nodes, searchQuery);
            setProcessedData({
                nodes: searchResults,
                edges: data.edges.filter(edge =>
                    searchResults.some((node: GraphNode) => node.id === edge.from || node.id === edge.to)
                )
            });
        };
        handleSearch();
    }, [searchQuery, data, searchNodes]);

    // Initialize and update network
    useEffect(() => {
        if (!containerRef.current) return;

        const nodes = new DataSet<Node>(processedData.nodes);
        const edges = new DataSet<Edge>(processedData.edges);

        const options = {
            nodes: {
                shape: 'dot',
                size: 16,
                font: {
                    size: 12,
                    color: '#ffffff'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                shadow: true,
                smooth: {
                    enabled: true,
                    type: 'continuous',
                    roundness: 0.5
                }
            },
            physics: {
                stabilization: {
                    iterations: 100
                },
                barnesHut: {
                    gravitationalConstant: -2000,
                    springLength: 200,
                    springConstant: 0.04
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200
            }
        };

        if (!networkRef.current) {
            networkRef.current = new Network(
                containerRef.current,
                { nodes, edges },
                options
            );

            if (onNodeClick) {
                networkRef.current.on('click', (params) => {
                    if (params.nodes.length > 0) {
                        onNodeClick(params.nodes[0]);
                    }
                });
            }
        } else {
            networkRef.current.setData({ nodes, edges });
        }

        return () => {
            if (networkRef.current) {
                networkRef.current.destroy();
                networkRef.current = null;
            }
        };
    }, [processedData, onNodeClick]);

    return (
        <div
            ref={containerRef}
            className="w-full h-full bg-gray-50 dark:bg-gray-900"
            style={{ minHeight: '400px' }}
        />
    );
}; 