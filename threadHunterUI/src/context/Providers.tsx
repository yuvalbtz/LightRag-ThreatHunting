import React from 'react';
import { GraphWorkerProvider } from './GraphWorkerContext';
import { ChatProvider } from './ChatContext';
import { PlaybookProvider } from './PlaybookContext';

export const Providers: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
        <GraphWorkerProvider>
            <ChatProvider>
                <PlaybookProvider>
                    {children}
                </PlaybookProvider>
            </ChatProvider>
        </GraphWorkerProvider>
    );
}; 