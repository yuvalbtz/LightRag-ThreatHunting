import { useEffect, useRef, useCallback, useState } from 'react';
import { GraphData, GraphNode } from '../types';

interface GraphWorkerState {
    graphData: GraphData | null;
    isLoading: boolean;
    error: string | null;
}

// Singleton instance
let workerInstance: Worker | null = null;
let stateInstance: GraphWorkerState = {
    graphData: null,
    isLoading: false,
    error: null
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

    useEffect(() => {
        // Initialize worker
        initializeWorker();

        // Subscribe to state updates
        stateSubscribers.add(setState);

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
        updateState({ isLoading: true, error: null });

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

    const getGraphData = useCallback(async (): Promise<GraphData> => {
        updateState({ isLoading: true, error: null });

        return new Promise((resolve, reject) => {
            if (!workerInstance) return reject(new Error('Worker not initialized'));

            const handler = (e: MessageEvent) => {
                if (e.data.type === 'GRAPH_DATA_FETCHED') {
                    removeEventListener('GRAPH_DATA_FETCHED', handler);
                    removeEventListener('GRAPH_DATA_ERROR', handler);
                    const graphData = e.data.data;
                    updateState({
                        isLoading: false,
                        graphData
                    });
                    resolve(graphData);
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
                type: 'GET_GRAPH_DATA'
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
        updateState({
            graphData: null,
            isLoading: false,
            error: null
        });
    }, []);

    const setGraphData = useCallback((data: GraphData) => {
        updateState({ graphData: data });
    }, []);

    return {
        ...state,
        buildGraph,
        getGraphData,
        searchGraph,
        resetGraph,
        setGraphData
    };
} 