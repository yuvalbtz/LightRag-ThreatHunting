import { useDarkMode } from '@/context/ThemeContext';
import { useCallback, useEffect, useRef, useState } from 'react';
import { DataSet, Edge, Network, Node, Options } from 'vis-network/standalone';
import { GraphData } from '../types';
const CLUSTER_THRESHOLD = 50; // Adjust this value based on your needs

interface GraphWorkerState {
    graphData: GraphData | null;
    isLoading: boolean;
    isRendering: boolean;
    networkInstance: Network | null;
    networkRef: React.RefObject<HTMLDivElement> | null;
    stabilizationProgress: number;
    error: string | null;
    dir_path: string;
}

// Singleton instance
let workerInstance: Worker | null = null;
let stateInstance: GraphWorkerState = {
    graphData: null,
    isLoading: false,
    isRendering: false,
    dir_path: '',
    error: null,
    networkInstance: null,
    networkRef: null,
    stabilizationProgress: 0
};

// Event listeners for the worker
const eventListeners = new Map<string, Set<(e: MessageEvent) => void>>();

// State subscribers
const stateSubscribers = new Set<(state: GraphWorkerState) => void>();

// Initialize worker if not exists
const initializeWorker = () => {
    if (!workerInstance) {
        workerInstance = new Worker(new URL('../workers/graphWorker.ts', import.meta.url), {
            type: 'module'
        });

        workerInstance.addEventListener('message', (e: MessageEvent) => {
            const listeners = eventListeners.get(e.data.type);
            if (listeners) {
                listeners.forEach(listener => listener(e));
            }
        });
    }
    return workerInstance;
};

// Update state and notify all subscribers
const updateState = (newState: Partial<GraphWorkerState>) => {
    stateInstance = { ...stateInstance, ...newState };
    stateSubscribers.forEach(subscriber => subscriber(stateInstance));
};

export function useGraphWorker() {
    const [state, setState] = useState<GraphWorkerState>(stateInstance);
    const isDarkMode = useDarkMode();
    const networkRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Initialize worker
        initializeWorker();

        // Subscribe to state updates
        stateSubscribers.add(setState);

        // Update state with ref
        updateState({ networkRef });

        // Cleanup
        return () => {
            stateSubscribers.delete(setState);
        };
    }, []);

    const addEventListener = useCallback((type: string, handler: (e: MessageEvent) => void) => {
        if (!eventListeners.has(type)) {
            eventListeners.set(type, new Set());
        }
        eventListeners.get(type)?.add(handler);
    }, []);

    const removeEventListener = useCallback((type: string, handler: (e: MessageEvent) => void) => {
        eventListeners.get(type)?.delete(handler);
    }, []);

    const buildGraph = useCallback(async (file: File): Promise<{ entity_count: number; relationship_count: number }> => {
        updateState({ isLoading: true, error: null, dir_path: './AppDbStore/' + file.name.split('.')[0] });

        return new Promise((resolve, reject) => {
            if (!workerInstance) return reject(new Error('Worker not initialized'));

            const handler = (e: MessageEvent) => {
                if (e.data.type === 'GRAPH_BUILT') {
                    removeEventListener('GRAPH_BUILT', handler);
                    removeEventListener('GRAPH_BUILD_ERROR', handler);
                    updateState({ isLoading: false });
                    resolve(e.data.data);
                } else if (e.data.type === 'GRAPH_BUILD_ERROR') {
                    removeEventListener('GRAPH_BUILT', handler);
                    removeEventListener('GRAPH_BUILD_ERROR', handler);
                    updateState({ isLoading: false, error: e.data.error });
                    reject(new Error(e.data.error));
                }
            };

            addEventListener('GRAPH_BUILT', handler);
            addEventListener('GRAPH_BUILD_ERROR', handler);
            workerInstance.postMessage({
                type: 'BUILD_GRAPH',
                data: { file }
            });
        });
    }, [addEventListener, removeEventListener]);

    const getGraphData = useCallback(async (dir_path: string): Promise<GraphData> => {
        updateState({ isRendering: true, error: null, dir_path: dir_path, stabilizationProgress: 0 });

        return new Promise((resolve, reject) => {
            if (!workerInstance) return reject(new Error('Worker not initialized'));

            const handler = (e: MessageEvent) => {
                if (e.data.type === 'GRAPH_DATA_FETCHED') {
                    removeEventListener('GRAPH_DATA_FETCHED', handler);
                    removeEventListener('GRAPH_DATA_ERROR', handler);
                    const graphData = e.data.data;
                    updateState({
                        graphData,
                    });
                    resolve(graphData);
                } else if (e.data.type === 'GRAPH_DATA_ERROR') {
                    removeEventListener('GRAPH_DATA_FETCHED', handler);
                    removeEventListener('GRAPH_DATA_ERROR', handler);
                    updateState({ isLoading: false, isRendering: false, stabilizationProgress: 0, error: e.data.error });
                    reject(new Error(e.data.error));
                }
            };

            addEventListener('GRAPH_DATA_FETCHED', handler);
            addEventListener('GRAPH_DATA_ERROR', handler);
            workerInstance.postMessage({
                type: 'GET_GRAPH_DATA',
                data: { dir_path }
            });
        });
    }, [addEventListener, removeEventListener]);

    const searchGraph = useCallback(async (query: string): Promise<void> => {
        updateState({ isLoading: true, error: null });

        return new Promise((resolve, reject) => {
            if (!workerInstance) return reject(new Error('Worker not initialized'));

            const handler = (e: MessageEvent) => {
                if (e.data.type === 'GRAPH_DATA_FETCHED') {
                    removeEventListener('GRAPH_DATA_FETCHED', handler);
                    removeEventListener('GRAPH_DATA_ERROR', handler);
                    updateState({
                        isLoading: false,
                        graphData: e.data.data
                    });
                    resolve();
                } else if (e.data.type === 'GRAPH_DATA_ERROR') {
                    removeEventListener('GRAPH_DATA_FETCHED', handler);
                    removeEventListener('GRAPH_DATA_ERROR', handler);
                    updateState({ isLoading: false, error: e.data.error });
                    reject(new Error(e.data.error));
                }
            };

            addEventListener('GRAPH_DATA_FETCHED', handler);
            addEventListener('GRAPH_DATA_ERROR', handler);
            workerInstance.postMessage({
                type: 'SEARCH_GRAPH',
                data: { query }
            });
        });
    }, [addEventListener, removeEventListener]);

    const resetGraph = useCallback(() => {
        if (state.networkInstance) {
            state.networkInstance.destroy();
        }

        // Clear the network container
        if (networkRef.current) {
            networkRef.current.innerHTML = '';
        }

        updateState({
            graphData: null,
            isLoading: false,
            isRendering: false,
            error: null,
            dir_path: '',
            stabilizationProgress: 0,
            networkInstance: null
        });
    }, [state.networkInstance]);

    const initializeNetwork = useCallback(() => {
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
                    iterations: 300,
                    updateInterval: 25,
                    fit: true
                },
                barnesHut: {
                    gravitationalConstant: -2000,
                    springLength: 200
                }
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

    const setGraphData = useCallback((data: GraphData) => {
        updateState({ graphData: data });
        initializeNetwork();
    }, [initializeNetwork]);

    // Add effect to initialize network when ref is available
    useEffect(() => {
        if (networkRef.current && state.graphData) {
            initializeNetwork();
        }
    }, [state.graphData]);

    // Cleanup effect
    useEffect(() => {
        if (!state.graphData && state.networkInstance) {
            state.networkInstance.destroy();
            updateState({
                networkInstance: null,
                isRendering: false,
                stabilizationProgress: 0
            });
        }
    }, [state.graphData]);

    return {
        ...state,
        networkRef,
        buildGraph,
        getGraphData,
        searchGraph,
        resetGraph,
        setGraphData
    };
} 