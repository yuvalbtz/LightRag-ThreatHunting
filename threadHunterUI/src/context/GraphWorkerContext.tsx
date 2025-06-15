import React, { createContext, useContext, useRef, useCallback, useState, useEffect } from 'react';
import { GraphData, GraphNode } from '../types';

interface GraphWorkerState {
    graphData: GraphData | null;
    isLoading: boolean;
    error: string | null;
}

interface GraphWorkerContextType extends GraphWorkerState {
    buildGraph: (file: File) => Promise<{ entity_count: number; relationship_count: number }>;
    getGraphData: () => Promise<GraphData>;
    searchGraph: (query: string) => Promise<void>;
    resetGraph: () => void;
    setGraphData: (data: GraphData) => void;
}

const GraphWorkerContext = createContext<GraphWorkerContextType | null>(null);

export const GraphWorkerProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const workerRef = useRef<Worker | null>(null);
    const [state, setState] = useState<GraphWorkerState>({
        graphData: null,
        isLoading: false,
        error: null
    });

    useEffect(() => {
        // Create worker
        workerRef.current = new Worker(new URL('../workers/graphWorker.ts', import.meta.url), {
            type: 'module'
        });

        // Cleanup
        return () => {
            workerRef.current?.terminate();
        };
    }, []);

    const buildGraph = useCallback(async (file: File): Promise<{ entity_count: number; relationship_count: number }> => {
        setState(prev => ({ ...prev, isLoading: true, error: null }));

        return new Promise((resolve, reject) => {
            if (!workerRef.current) return reject(new Error('Worker not initialized'));

            const handler = (e: MessageEvent) => {
                if (e.data.type === 'GRAPH_BUILT') {
                    workerRef.current?.removeEventListener('message', handler);
                    setState(prev => ({ ...prev, isLoading: false }));
                    resolve(e.data.data);
                } else if (e.data.type === 'GRAPH_BUILD_ERROR') {
                    workerRef.current?.removeEventListener('message', handler);
                    setState(prev => ({ ...prev, isLoading: false, error: e.data.error }));
                    reject(new Error(e.data.error));
                }
            };

            workerRef.current.addEventListener('message', handler);
            workerRef.current.postMessage({
                type: 'BUILD_GRAPH',
                data: { file }
            });
        });
    }, []);

    const getGraphData = useCallback(async (): Promise<GraphData> => {
        setState(prev => ({ ...prev, isLoading: true, error: null }));

        return new Promise((resolve, reject) => {
            if (!workerRef.current) return reject(new Error('Worker not initialized'));

            const handler = (e: MessageEvent) => {
                if (e.data.type === 'GRAPH_DATA_FETCHED') {
                    workerRef.current?.removeEventListener('message', handler);
                    const graphData = e.data.data;
                    setState(prev => ({
                        ...prev,
                        isLoading: false,
                        graphData
                    }));
                    resolve(graphData);
                } else if (e.data.type === 'GRAPH_DATA_ERROR') {
                    workerRef.current?.removeEventListener('message', handler);
                    setState(prev => ({ ...prev, isLoading: false, error: e.data.error }));
                    reject(new Error(e.data.error));
                }
            };

            workerRef.current.addEventListener('message', handler);
            workerRef.current.postMessage({
                type: 'GET_GRAPH_DATA'
            });
        });
    }, []);

    const searchGraph = useCallback(async (query: string): Promise<void> => {
        setState(prev => ({ ...prev, isLoading: true, error: null }));

        return new Promise((resolve, reject) => {
            if (!workerRef.current) return reject(new Error('Worker not initialized'));

            const handler = (e: MessageEvent) => {
                if (e.data.type === 'GRAPH_DATA_FETCHED') {
                    workerRef.current?.removeEventListener('message', handler);
                    setState(prev => ({
                        ...prev,
                        isLoading: false,
                        graphData: e.data.data
                    }));
                    resolve();
                } else if (e.data.type === 'GRAPH_DATA_ERROR') {
                    workerRef.current?.removeEventListener('message', handler);
                    setState(prev => ({ ...prev, isLoading: false, error: e.data.error }));
                    reject(new Error(e.data.error));
                }
            };

            workerRef.current.addEventListener('message', handler);
            workerRef.current.postMessage({
                type: 'SEARCH_GRAPH',
                data: { query }
            });
        });
    }, []);

    const resetGraph = useCallback(() => {
        setState({
            graphData: null,
            isLoading: false,
            error: null
        });
    }, []);

    const setGraphData = useCallback((data: GraphData) => {
        setState(prev => ({ ...prev, graphData: data }));
    }, []);

    const value = {
        ...state,
        buildGraph,
        getGraphData,
        searchGraph,
        resetGraph,
        setGraphData
    };

    return (
        <GraphWorkerContext.Provider value={value}>
            {children}
        </GraphWorkerContext.Provider>
    );
};

export const useGraphWorker = () => {
    const context = useContext(GraphWorkerContext);
    if (!context) {
        throw new Error('useGraphWorker must be used within a GraphWorkerProvider');
    }
    return context;
};