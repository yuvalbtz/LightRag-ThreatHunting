import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Card } from '@heroui/card';
import { GraphData } from '../types';
import { PaperAirplaneIcon } from '@heroicons/react/24/outline';
import { useMessages, useSendMessage, useChatLoading, createUserMessage } from '../context/ChatContext';
import { useGraphWorker } from '../hooks/useGraphWorker';
import { useTheme } from '@/context/ThemeContext';

interface ChatContainerProps {
    isDarkMode: boolean;
    graphData: GraphData | null;
}

const formatMessage = (content: string) => {
    const sections = content.split(/(?=###|\*\*)/);

    return sections.map((section, index) => {
        if (section.startsWith('###')) {
            return (
                <h3 key={index} className="text-lg font-semibold mt-4 mb-2">
                    {section.replace('###', '').trim()}
                </h3>
            );
        }

        if (section.startsWith('**')) {
            return (
                <p key={index} className="font-semibold my-2">
                    {section.replace(/\*\*/g, '').trim()}
                </p>
            );
        }

        if (section.includes('- ')) {
            const items = section.split('- ').filter(item => item.trim());
            return (
                <ul key={index} className="list-disc pl-6 my-2">
                    {items.map((item, i) => (
                        <li key={i} className="mb-1">{item.trim()}</li>
                    ))}
                </ul>
            );
        }

        if (section.includes('[KG]')) {
            return (
                <div key={index} className="text-sm text-gray-500 mt-4">
                    {section.split('\n').map((line, i) => (
                        <p key={i}>{line.trim()}</p>
                    ))}
                </div>
            );
        }

        return (
            <p key={index} className="my-2">
                {section.trim()}
            </p>
        );
    });
};

export const ChatContainer = () => {
    const messages = useMessages();
    const sendMessage = useSendMessage();
    const isLoading = useChatLoading();
    const [input, setInput] = useState('');
    const [file, setFile] = useState<File | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const { graphData } = useGraphWorker();
    const state = useGraphWorker();

    console.log("graphData !!!", state);
    const { isDarkMode } = useTheme();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() && !file) return;
        const message = input.trim();
        setInput('');
        await sendMessage(createUserMessage(message));
    };

    return (
        <div className="flex-1 flex flex-col relative overflow-hidden">
            <svg
                className="absolute inset-0 w-full h-full pointer-events-none z-0"
                aria-hidden="true"
                focusable="false"
                viewBox="0 0 100 100"
                preserveAspectRatio="none"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
            >
                <defs>
                    <radialGradient id="th-bg-light" cx="50%" cy="50%" r="80%">
                        <stop offset="0%" stopColor="#a5b4fc" stopOpacity="0.12" />
                        <stop offset="100%" stopColor="#f0f9ff" stopOpacity="0" />
                    </radialGradient>
                    <radialGradient id="th-bg-dark" cx="50%" cy="50%" r="80%">
                        <stop offset="0%" stopColor="#0ea5e9" stopOpacity="0.08" />
                        <stop offset="100%" stopColor="#0f172a" stopOpacity="0" />
                    </radialGradient>
                </defs>
                <rect width="100" height="100" fill={isDarkMode ? 'url(#th-bg-dark)' : 'url(#th-bg-light)'} />

                <g opacity="0.6">
                    {/* Knowledge Graph Nodes */}
                    <circle cx="20" cy="20" r="2" fill={isDarkMode ? "#0ea5e9" : "#a5b4fc"} opacity="0.15" />
                    <circle cx="40" cy="30" r="2.5" fill={isDarkMode ? "#0ea5e9" : "#a5b4fc"} opacity="0.12" />
                    <circle cx="60" cy="40" r="2" fill={isDarkMode ? "#0ea5e9" : "#a5b4fc"} opacity="0.15" />
                    <circle cx="80" cy="30" r="2.5" fill={isDarkMode ? "#0ea5e9" : "#a5b4fc"} opacity="0.12" />
                    <circle cx="30" cy="60" r="2" fill={isDarkMode ? "#0ea5e9" : "#a5b4fc"} opacity="0.15" />
                    <circle cx="50" cy="70" r="2.5" fill={isDarkMode ? "#0ea5e9" : "#a5b4fc"} opacity="0.12" />
                    <circle cx="70" cy="60" r="2" fill={isDarkMode ? "#0ea5e9" : "#a5b4fc"} opacity="0.15" />

                    {/* Connections between nodes */}
                    <line x1="20" y1="20" x2="40" y2="30" stroke={isDarkMode ? "#0ea5e9" : "#a5b4fc"} strokeWidth="0.3" opacity="0.08" />
                    <line x1="40" y1="30" x2="60" y2="40" stroke={isDarkMode ? "#0ea5e9" : "#a5b4fc"} strokeWidth="0.3" opacity="0.08" />
                    <line x1="60" y1="40" x2="80" y2="30" stroke={isDarkMode ? "#0ea5e9" : "#a5b4fc"} strokeWidth="0.3" opacity="0.08" />
                    <line x1="20" y1="20" x2="30" y2="60" stroke={isDarkMode ? "#0ea5e9" : "#a5b4fc"} strokeWidth="0.3" opacity="0.08" />
                    <line x1="30" y1="60" x2="50" y2="70" stroke={isDarkMode ? "#0ea5e9" : "#a5b4fc"} strokeWidth="0.3" opacity="0.08" />
                    <line x1="50" y1="70" x2="70" y2="60" stroke={isDarkMode ? "#0ea5e9" : "#a5b4fc"} strokeWidth="0.3" opacity="0.08" />
                    <line x1="70" y1="60" x2="80" y2="30" stroke={isDarkMode ? "#0ea5e9" : "#a5b4fc"} strokeWidth="0.3" opacity="0.08" />

                    {/* Central RAG node */}
                    <circle cx="50" cy="50" r="3" fill={isDarkMode ? "#0ea5e9" : "#a5b4fc"} opacity="0.2" />
                    <line x1="50" y1="50" x2="40" y2="30" stroke={isDarkMode ? "#0ea5e9" : "#a5b4fc"} strokeWidth="0.3" opacity="0.08" />
                    <line x1="50" y1="50" x2="60" y2="40" stroke={isDarkMode ? "#0ea5e9" : "#a5b4fc"} strokeWidth="0.3" opacity="0.08" />
                    <line x1="50" y1="50" x2="30" y2="60" stroke={isDarkMode ? "#0ea5e9" : "#a5b4fc"} strokeWidth="0.3" opacity="0.08" />
                    <line x1="50" y1="50" x2="70" y2="60" stroke={isDarkMode ? "#0ea5e9" : "#a5b4fc"} strokeWidth="0.3" opacity="0.08" />
                </g>
            </svg>
            <div className={`flex-1 overflow-y-auto p-4 space-y-4 transition-colors duration-200 z-10`}>
                {!graphData && (
                    <div className={`text-center p-2 mb-2 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'} text-sm`}>
                        Please upload a file to enable chat functionality
                    </div>
                )}
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <Card
                            className={`max-w-[80%] transition-colors duration-200 ${message.role === 'user'
                                ? `${isDarkMode ? 'bg-blue-800 text-blue-100' : 'bg-blue-100 text-blue-900'}`
                                : message.isError
                                    ? 'bg-dark text-red-700'
                                    : isDarkMode
                                        ? 'bg-dark text-white'
                                        : 'bg-white text-gray-900'
                                }`}
                        >
                            <div className="p-4">
                                {message.file && (
                                    <div className={`text-xs opacity-50 mb-2 transition-colors duration-200 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'
                                        }`}>
                                        📎 {message.file.name}
                                    </div>
                                )}
                                <div className={`text-sm opacity-70 mb-1 transition-colors duration-200 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'
                                    }`}>
                                    {message.role === 'user' ? 'You' : 'ThreatHunter AI'}
                                </div>
                                <div className="prose prose-sm max-w-none">
                                    {formatMessage(message.content)}
                                </div>
                                <div className={`text-xs mt-1 opacity-70 transition-colors duration-200 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'
                                    }`}>
                                    {new Date(message.timestamp).toLocaleTimeString()}
                                </div>
                            </div>
                        </Card>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                        <Card className={`transition-colors duration-200 ${isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'
                            }`}>
                            <div className="p-4">
                                <div className="flex space-x-2">
                                    <div className="w-2 h-2 bg-current rounded-full animate-bounce" />
                                    <div className="w-2 h-2 bg-current rounded-full animate-bounce delay-100" />
                                    <div className="w-2 h-2 bg-current rounded-full animate-bounce delay-200" />
                                </div>
                            </div>
                        </Card>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSubmit} className={`p-4 border-t transition-colors duration-200 ${isDarkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'}`}>
                <div className="flex space-x-4">
                    <Input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder={graphData ? "Ask about potential threats..." : "Upload a file to enable chat..."}
                        className={`flex-1 transition-colors duration-200 focus:outline-violet-500`}
                        variant='underlined'
                        disabled={isLoading || !graphData}
                    />
                    <Button
                        type="submit"
                        disabled={!input.trim() || isLoading || !graphData}
                        className={`min-w-[40px] h-10 transition-colors duration-200 ${isDarkMode
                            ? 'bg-gray-700 text-white hover:bg-gray-600'
                            : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
                            }`}
                        title={graphData ? "Send message" : "Upload a file to enable chat"}
                    >
                        {isLoading ? (
                            <div className="flex items-center">
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                            </div>
                        ) : (
                            <PaperAirplaneIcon className="h-5 w-5" />
                        )}
                    </Button>
                </div>
            </form>
        </div>
    );
}; 