import React from 'react';
import { createContext, useContextSelector } from 'use-context-selector';
import { Playbook } from '../types';
import { api } from '../services/api';

interface PlaybookContextType {
    playbooks: Playbook[];
    selectedPlaybook: Playbook | null;
    isLoading: boolean;
    error: string | null;
    loadPlaybooks: () => Promise<void>;
    selectPlaybook: (id: string) => Promise<void>;
    clearSelection: () => void;
}

const PlaybookContext = createContext<PlaybookContextType | null>(null);

export const PlaybookProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [playbooks, setPlaybooks] = React.useState<Playbook[]>([]);
    const [selectedPlaybook, setSelectedPlaybook] = React.useState<Playbook | null>(null);
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);

    const loadPlaybooks = React.useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const data = await api.playbooks.getAll();
            setPlaybooks(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load playbooks');
        } finally {
            setIsLoading(false);
        }
    }, []);

    const selectPlaybook = React.useCallback(async (id: string) => {
        try {
            setIsLoading(true);
            setError(null);
            const playbook = await api.playbooks.getById(id);
            setSelectedPlaybook(playbook);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to select playbook');
        } finally {
            setIsLoading(false);
        }
    }, []);

    const clearSelection = React.useCallback(() => {
        setSelectedPlaybook(null);
    }, []);

    const value = React.useMemo(() => ({
        playbooks,
        selectedPlaybook,
        isLoading,
        error,
        loadPlaybooks,
        selectPlaybook,
        clearSelection
    }), [playbooks, selectedPlaybook, isLoading, error, loadPlaybooks, selectPlaybook, clearSelection]);

    return (
        <PlaybookContext.Provider value={value}>
            {children}
        </PlaybookContext.Provider>
    );
};

export const usePlaybook = () => {
    const context = useContextSelector(PlaybookContext, (state) => state);
    if (!context) {
        throw new Error('usePlaybook must be used within a PlaybookProvider');
    }
    return context;
};

// Selector hooks for specific values
export const usePlaybooks = () => useContextSelector(PlaybookContext, (state) => state?.playbooks);
export const useSelectedPlaybook = () => useContextSelector(PlaybookContext, (state) => state?.selectedPlaybook);
export const usePlaybookLoading = () => useContextSelector(PlaybookContext, (state) => state?.isLoading);
export const usePlaybookError = () => useContextSelector(PlaybookContext, (state) => state?.error); 