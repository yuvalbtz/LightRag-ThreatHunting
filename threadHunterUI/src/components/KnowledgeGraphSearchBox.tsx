import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Input, Button } from '@heroui/react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { useGraphWorker } from '@/hooks/useGraphWorker';

const KnowledgeGraphSearchBox = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [isSearching, setIsSearching] = useState(false);
    const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const [searchResultsCount, setSearchResultsCount] = useState(0);

    const { searchNodes, clearNodeHighlighting } = useGraphWorker();

    const handleSearch = useCallback(async (e: React.FormEvent) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            setIsSearching(true);
            const matchingNodes = searchNodes(searchQuery.trim());
            setSearchResultsCount(matchingNodes?.length || 0);
            setIsSearching(false);
        }
    }, [searchQuery, searchNodes]);

    const handleClear = useCallback(() => {
        setSearchQuery('');
        setIsTyping(false);
        setIsSearching(false);
        if (debounceTimeoutRef.current) {
            clearTimeout(debounceTimeoutRef.current);
            debounceTimeoutRef.current = null;
        }
        clearNodeHighlighting();
        setSearchResultsCount(0);
    }, [clearNodeHighlighting]);

    const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setSearchQuery(value);
        setIsTyping(true);

        // Clear existing timeout
        if (debounceTimeoutRef.current) {
            clearTimeout(debounceTimeoutRef.current);
        }

        // Set new timeout for debounced search
        debounceTimeoutRef.current = setTimeout(() => {
            setIsTyping(false);
            if (value.trim()) {
                setIsSearching(true);
                const matchingNodes = searchNodes(value.trim());
                setSearchResultsCount(matchingNodes?.length || 0);
                setIsSearching(false);
            } else {
                clearNodeHighlighting();
                setSearchResultsCount(0);
                setIsSearching(false);
            }
        }, 300); // 300ms debounce delay
    }, [searchNodes, clearNodeHighlighting]);

    // Cleanup timeout on unmount
    useEffect(() => {
        return () => {
            if (debounceTimeoutRef.current) {
                clearTimeout(debounceTimeoutRef.current);
            }
        };
    }, []);

    return (
        <div className="absolute top-2 left-2 z-10 w-[50%]">
            <form onSubmit={handleSearch} className="relative">
                <Input
                    type="text"
                    value={searchQuery}
                    variant="flat"
                    onChange={handleInputChange}
                    placeholder="Search nodes (e.g., 192.168, port 80)..."
                    className='relative'
                    classNames={{
                        inputWrapper: [
                            "bg-transparent",
                            "shadow-xl",
                            "backdrop-blur-sm",
                            "dark:bg-transparent",
                            "hover:bg-transparent",
                            "dark:hover:bg-transparent",
                            "dark:group-data-[focus=true]:bg-transparent",
                            "!cursor-text",
                        ],
                    }}
                    startContent={
                        <MagnifyingGlassIcon className="w-4 h-4 text-default-400" />
                    }

                    endContent={
                        searchQuery ? (
                            <Button
                                isIconOnly
                                size="sm"
                                variant="light"
                                onPress={handleClear}
                                className="text-default-400 hover:text-default-600 absolute right-0"
                            >
                                <XMarkIcon className="w-4 h-4" />
                            </Button>
                        ) : (isSearching || isTyping) ? (
                            <div className="text-primary">
                                <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent"></div>
                            </div>
                        ) : null
                    }

                    size="sm"
                />
            </form>

            {/* Search Results Indicator */}
            {searchQuery && searchResultsCount > 0 && !isTyping && !isSearching && (
                <div className="absolute -bottom-6 left-0 text-xs text-success">
                    Found {searchResultsCount} matching node{searchResultsCount !== 1 ? 's' : ''}
                </div>
            )}

            {searchQuery && searchResultsCount === 0 && !isTyping && !isSearching && (
                <div className="absolute -bottom-6 left-0 text-xs text-warning">
                    No matching nodes found
                </div>
            )}
        </div>
    );
};

export default KnowledgeGraphSearchBox; 