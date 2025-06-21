import React from 'react';
import { createContext, useContextSelector } from 'use-context-selector';
import { GraphData } from '../types';
import { api } from '../services/api';

interface GraphContextType {
    graphData: GraphData | null;
    isLoading: boolean;
    error: string | null;
    buildGraph: (file: File) => Promise<{ entity_count: number; relationship_count: number }>;
    searchGraph: (query: string) => Promise<void>;
    resetGraph: () => void;
    getGraphData: (dir_path?: string) => Promise<void>;
    setGraphData: (data: GraphData) => void;
}

const GraphContext = createContext<GraphContextType | null>(null);

export const GraphProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [graphData, setGraphData] = React.useState<GraphData | null>(null);
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);
    const buildGraph = async (file: File) => {
        setIsLoading(true);
        setError(null);
        try {
            // build the knowledge graph
            const buildResult = await api.graph.build(file);

            return buildResult;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to build graph');
            throw err;
        } finally {
            setIsLoading(false);
        }
    };



    const getGraphData = async (dir_path?: string) => {
        setIsLoading(true);
        setError(null);
        try {

            // Wait a bit for the graph to be fully built
            await new Promise(resolve => setTimeout(resolve, 3000));

            // Then, get the graph data
            const data = await api.graph.getData(dir_path);
            setGraphData(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to get graph data');
            throw err;
        } finally {
            setIsLoading(false);
        }
    };


    const searchGraph = async (query: string) => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await api.graph.search(query);
            setGraphData(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to search graph');
        } finally {
            setIsLoading(false);
        }
    };

    const resetGraph = () => {
        setGraphData(null);
        setError(null);
    };


    return (
        <GraphContext.Provider value={{
            graphData,
            isLoading,
            error,
            buildGraph,
            getGraphData,
            searchGraph,
            resetGraph,
            setGraphData
        }}>
            {children}
        </GraphContext.Provider>
    );
};

export const useGraph = () => {
    const context = useContextSelector(GraphContext, (state) => state);
    if (!context) {
        throw new Error('useGraph must be used within a GraphProvider');
    }
    return context;
};

// Selector hooks for specific values
export const useGraphData = () => useContextSelector(GraphContext, (state) => state?.graphData);
export const useGraphLoading = () => useContextSelector(GraphContext, (state) => state?.isLoading);
export const useGraphError = () => useContextSelector(GraphContext, (state) => state?.error); 