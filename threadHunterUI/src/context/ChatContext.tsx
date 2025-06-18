import React, { useState, useCallback } from 'react';
import { createContext, useContextSelector } from 'use-context-selector';
import { Message } from '../types';
import { api } from '@/services/api';

interface ChatContextType {
    messages: Message[];
    sendMessage: (message: Message, dir_path: string) => Promise<void>;
    isLoading: boolean;
}

const ChatContext = createContext<ChatContextType | null>(null);

// Message creation helpers
const createMessage = (content: string, role: 'user' | 'system' | 'assistant', isError?: boolean, graph_dir_path?: string): Message => ({
    id: crypto.randomUUID(),
    role,
    content,
    timestamp: new Date(),
    isError,
    graph_dir_path: graph_dir_path || ''
});

export const createUserMessage = (content: string, graph_dir_path: string): Message => createMessage(content, 'user', false, graph_dir_path);
export const createSystemMessage = (content: string, isError?: boolean, graph_dir_path?: string): Message => createMessage(content, 'system', isError, graph_dir_path || '');
export const createAssistantMessage = (content: string, graph_dir_path: string): Message => createMessage(content, 'assistant', false, graph_dir_path);

export const useChat = () => {
    const context = useContextSelector(ChatContext, (state) => state);
    if (!context) {
        throw new Error('useChat must be used within a ChatProvider');
    }
    return context;
};

export const useMessages = () => {
    const messages = useContextSelector(ChatContext, (state) => state?.messages);
    if (!messages) {
        throw new Error('useMessages must be used within a ChatProvider');
    }
    return messages;
};

export const useChatLoading = () => {
    const isLoading = useContextSelector(ChatContext, (state) => state?.isLoading);
    if (isLoading === undefined) {
        throw new Error('useChatLoading must be used within a ChatProvider');
    }
    return isLoading;
};

export const useSendMessage = () => {
    const sendMessage = useContextSelector(ChatContext, (state) => state?.sendMessage);
    if (!sendMessage) {
        throw new Error('useSendMessage must be used within a ChatProvider');
    }
    return sendMessage;
};

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const sendMessage = useCallback(async (message: Message, dir_path: string) => {
        setIsLoading(true);
        console.log("dir_path", dir_path);
        try {
            if (message.content && message.role !== 'user') {
                setMessages(prev => [...prev, message]);
            } else if (message.content && message.role === 'user') {
                setMessages(prev => [...prev, message]);
                await api.chat.sendMessage(message.content, setMessages, dir_path);
            }
        } catch (error) {
            console.error('Error:', error);
            setMessages(prev => [...prev, createSystemMessage(
                `Error: ${error instanceof Error ? error.message : 'Failed to get response'}`,
                true
            )])
        } finally {
            setIsLoading(false);
        }
    }, []);

    return (
        <ChatContext.Provider value={{ messages, sendMessage, isLoading }}>
            {children}
        </ChatContext.Provider>
    );
}; 