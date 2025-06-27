import { DataSet, Options, Node, Edge, Network } from "vis-network/standalone";
import { useGraphWorker } from "../hooks/useGraphWorker";
import { useTheme } from "@/context/ThemeContext";
import { useEffect, useRef } from "react";
const CLUSTER_THRESHOLD = 50; // Adjust this value based on your needs

const KnowledgeGraphNetwork = () => {
    const state = useGraphWorker();
    const { isDarkMode } = useTheme();
    const { updateState } = state;
    const networkRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!networkRef.current || !state.graphData) return;

        const nodes = new DataSet<Node>(state.graphData.nodes);
        const edges = new DataSet<Edge>(state.graphData.edges);

        const options: Options = {
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
                },
                font: {
                    size: 12,
                    color: isDarkMode ? '#ffffff' : '#000000',
                    align: 'middle'
                },
                selectionWidth: 2,
                arrows: {
                    to: { enabled: true, scaleFactor: 1 }
                }
            },
            physics: {
                stabilization: {
                    iterations: 400,
                    updateInterval: 25,
                    fit: true,
                    onlyDynamicEdges: false,
                },
                barnesHut: {
                    gravitationalConstant: -2000,
                    avoidOverlap: 0,
                },

                maxVelocity: 30,     // Lower max to reduce chaotic movements
                minVelocity: 0.75,   // Stop movement earlier
            },
            interaction: {
                hover: true,
                tooltipDelay: 200,
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

        if (state.networkInstance) {
            state.networkInstance.destroy();
        }

        const network = new Network(networkRef.current, { nodes, edges }, options);
        updateState({ networkInstance: network, isRendering: true, stabilizationProgress: 0 });

        network.on('stabilizationProgress', (params) => {
            const progress = Math.min(100, Math.round((params.iterations / params.total) * 100));
            updateState({ stabilizationProgress: progress });
        });
        let isNodeBeingDragged = false;
        let draggedNodeId = null;
        network.on("dragStart", (params) => {
            if (params.nodes.length > 0) {
                // Enable physics while dragging a node
                isNodeBeingDragged = true;
                draggedNodeId = params.nodes[0];
                network.setOptions({ physics: { enabled: true } });
            }
        });
        network.on("dragEnd", (params) => {
            if (isNodeBeingDragged) {
                isNodeBeingDragged = false;
                draggedNodeId = null;

                // Disable physics after dragging
                network.setOptions({ physics: { enabled: false } });
            }
        });
        network.once('stabilizationIterationsDone', () => {
            updateState({ stabilizationProgress: 100, isRendering: false });
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
            network.setOptions({
                physics: {
                    enabled: false
                }
            });
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
            if (network) {
                network.destroy();
            }
            updateState({ stabilizationProgress: 0 });
        };
    }, [state.graphData]);



    return (
        <div ref={networkRef} className="w-full h-[100%]" />
    );
};

export default KnowledgeGraphNetwork;