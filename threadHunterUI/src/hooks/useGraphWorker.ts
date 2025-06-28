import { useDarkMode } from '@/context/ThemeContext';
import { useCallback, useEffect, useRef, useState } from 'react';
import { DataSet, Edge, Network, Node, Options } from 'vis-network/standalone';
import { GraphData, KGSettings } from '../types';

interface GraphWorkerState {
    graphData: GraphData | null;
    isLoading: boolean;
    isRendering: boolean;
    networkInstance: Network | null;
    networkRef: React.RefObject<HTMLDivElement> | null;
    stabilizationProgress: number;
    error: string | null;
    dir_path: string;
    updateState: (newState: Partial<GraphWorkerState>) => void;

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
    stabilizationProgress: 0,
    updateState: () => { }
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

    const buildGraph = useCallback(async (file: File, kg_settings: KGSettings = { max_rows: 2000 }): Promise<{ entity_count: number; relationship_count: number }> => {
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
                data: { file, kg_settings }
            });
        });
    }, [addEventListener, removeEventListener]);
    const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

    const getGraphData = useCallback(async (dir_path: string): Promise<GraphData> => {
        updateState({ isRendering: true, error: null, dir_path: dir_path, stabilizationProgress: 0 });
        return new Promise(async (resolve, reject) => {
            await sleep(1000);
            if (!workerInstance) return reject(new Error('Worker not initialized'));

            const handler = (e: MessageEvent) => {
                if (e.data.type === 'GRAPH_DATA_FETCHED') {
                    removeEventListener('GRAPH_DATA_FETCHED', handler);
                    removeEventListener('GRAPH_DATA_ERROR', handler);
                    const graphData = e.data.data;
                    updateState({ graphData });
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

    const searchNodes = useCallback((query: string) => {
        if (!state.networkInstance || !state.graphData) return [];

        const nodes = state.graphData.nodes;
        const matchingNodes: string[] = [];

        // Search for nodes that match the query (case-insensitive)
        nodes.forEach(node => {
            const label = node.label?.toLowerCase() || '';
            const title = node.title?.toLowerCase() || '';
            const queryLower = query.toLowerCase();

            if (label.includes(queryLower) || title.includes(queryLower)) {
                matchingNodes.push(String(node.id));
            }
        });

        // Get the nodes DataSet from the network
        const nodesDataSet = (state.networkInstance as any).body?.data?.nodes;
        if (!nodesDataSet) return matchingNodes;

        // Reset all nodes to default color
        const allNodes = nodes.map(node => ({
            id: node.id,
            color: {
                background: isDarkMode ? '#4B5563' : '#E5E7EB',
                border: isDarkMode ? '#6B7280' : '#9CA3AF',
                highlight: {
                    background: isDarkMode ? '#60A5FA' : '#3B82F6',
                    border: isDarkMode ? '#93C5FD' : '#60A5FA'
                }
            }
        }));

        // Highlight matching nodes
        matchingNodes.forEach(nodeId => {
            const nodeIndex = allNodes.findIndex(n => String(n.id) === nodeId);
            if (nodeIndex !== -1) {
                allNodes[nodeIndex].color = {
                    background: '#EF4444', // Red background for highlighted nodes
                    border: '#DC2626',
                    highlight: {
                        background: '#F87171',
                        border: '#EF4444'
                    }
                };
            }
        });

        // Update the network with new colors
        nodesDataSet.update(allNodes);

        // Fit the view to show all highlighted nodes if any
        if (matchingNodes.length > 0) {
            state.networkInstance.fit({
                nodes: matchingNodes,
                animation: {
                    duration: 1000,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }

        return matchingNodes;
    }, [state.networkInstance, state.graphData, isDarkMode]);

    const clearNodeHighlighting = useCallback(() => {
        if (!state.networkInstance || !state.graphData) return;

        const nodes = state.graphData.nodes.map(node => ({
            id: node.id,
        }));

        const nodesDataSet = (state.networkInstance as any).body?.data?.nodes;
        if (nodesDataSet) {
            nodesDataSet.update(nodes);
        }
        if (state.networkInstance) {
            state.networkInstance.fit({
                animation: {
                    duration: 1000,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }
    }, [state.networkInstance, state.graphData]);

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



    const setGraphData = useCallback((data: GraphData) => {
        updateState({ graphData: data });
    }, []);



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
        searchNodes,
        clearNodeHighlighting,
        resetGraph,
        setGraphData,
        updateState
    };
} 