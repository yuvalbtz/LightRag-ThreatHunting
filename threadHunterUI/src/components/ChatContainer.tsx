import { useTheme } from '@/context/ThemeContext';
import { FolderIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline';
import { Button } from '@heroui/button';
import { Card } from '@heroui/card';
import { Textarea } from '@heroui/input';
import { Chip } from '@heroui/react';
import React, { useEffect, useRef, useState } from 'react';
import { createUserMessage, useChatLoading, useMessages, useSendMessage } from '../context/ChatContext';
import { useGraphWorker } from '../hooks/useGraphWorker';

const formatMessage = (content: string) => {
    // If content is too short or doesn't contain expected patterns, return simple formatting
    if (content.length < 50 || !content.includes('###')) {
        return (
            <div className="whitespace-pre-wrap text-gray-700 dark:text-gray-300">
                {content}
            </div>
        );
    }

    // Clean up the content first - remove extra # symbols and normalize spacing
    let cleanedContent = content
        .replace(/#{5,}/g, '####') // Replace 5+ # with ####
        .replace(/#{3,4}/g, '###') // Replace 3-4 # with ###
        .replace(/\n{3,}/g, '\n\n') // Replace multiple newlines with double newlines
        .trim();

    const sections = cleanedContent.split(/(?=###|\*\*|#\s*\d+\.|-\s*[A-Z][^:]*:|References|Recommended Investigation Steps|---)/);

    return sections.map((section, index) => {
        // Handle numbered sections (e.g., "#### 1. **High-Risk External Communications**")
        if (section.match(/^####\s*\d+\.\s*\*\*/)) {
            const numberMatch = section.match(/^####\s*(\d+)\.\s*\*\*(.*?)\*\*/);
            if (numberMatch) {
                return (
                    <div key={index} className="mt-2 mb-1">
                        <h3 className="text-lg font-semibold text-blue-600 dark:text-blue-400 mb-1">
                            {numberMatch[1]}. {numberMatch[2]}
                        </h3>
                    </div>
                );
            }
        }

        // Handle main section headers (e.g., "### Threat Hunting Observations")
        if (section.startsWith('###')) {
            const cleanHeader = section.replace(/^###+/, '').trim();
            if (cleanHeader && !cleanHeader.match(/^\d+\./)) {
                return (
                    <h2 key={index} className="text-xl font-bold mt-3 mb-2 text-gray-800 dark:text-gray-200">
                        {cleanHeader}
                    </h2>
                );
            }
        }

        // Handle subsection headers with arrows (e.g., "Internal ↔ External Interactions:")
        if (section.match(/^-\s*[A-Z][^:]*:/)) {
            const cleanSection = section.replace(/^-\s*/, '').trim();
            return (
                <h4 key={index} className="text-md font-semibold mt-1 mb-1 text-gray-700 dark:text-gray-300">
                    {cleanSection}
                </h4>
            );
        }

        // Handle "Recommended Investigation Steps"
        if (section.startsWith('Recommended Investigation Steps')) {
            return (
                <div key={index} className="mt-3 p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-l-4 border-blue-500">
                    <h4 className="font-semibold mb-1 text-blue-800 dark:text-blue-300">Recommended Investigation Steps</h4>
                    <div className="text-sm text-blue-700 dark:text-blue-200">
                        {section.replace('Recommended Investigation Steps', '').split('\n').filter(line => line.trim()).map((line, i) => (
                            <p key={i}>{line.trim()}</p>
                        ))}
                    </div>
                </div>
            );
        }

        // Handle bold text
        if (section.startsWith('**')) {
            return (
                <p key={index} className="font-semibold my-0.5 text-gray-800 dark:text-gray-200">
                    {section.replace(/\*\*/g, '').trim()}
                </p>
            );
        }

        // Handle bullet points with specific threat level formatting
        if (section.includes('- ')) {
            const items = section.split('- ').filter(item => item.trim());
            return (
                <ul key={index} className="list-disc pl-6 my-0.5 space-y-0">
                    {items.map((item, i) => {
                        const trimmedItem = item.trim();
                        // Check for threat level indicators
                        if (trimmedItem.includes('HIGH threat level') || trimmedItem.includes('High threat level') ||
                            trimmedItem.includes('High-Risk') || trimmedItem.includes('high-threat')) {
                            return (
                                <li key={i} className="text-red-600 dark:text-red-400 font-medium">
                                    {trimmedItem}
                                </li>
                            );
                        }
                        if (trimmedItem.includes('MEDIUM-HIGH') || trimmedItem.includes('Medium threat level') ||
                            trimmedItem.includes('MEDIUM-threat') || trimmedItem.includes('MEDIUM threat')) {
                            return (
                                <li key={i} className="text-yellow-600 dark:text-yellow-400 font-medium">
                                    {trimmedItem}
                                </li>
                            );
                        }
                        if (trimmedItem.includes('Low threat level') || trimmedItem.includes('low threat')) {
                            return (
                                <li key={i} className="text-green-600 dark:text-green-400 font-medium">
                                    {trimmedItem}
                                </li>
                            );
                        }
                        // Check for suspicious/anomalous indicators
                        if (trimmedItem.includes('suspicious') || trimmedItem.includes('anomalous') ||
                            trimmedItem.includes('irregular_timing') || trimmedItem.includes('high_syn_count') ||
                            trimmedItem.includes('port_scanning') || trimmedItem.includes('data exfiltration') ||
                            trimmedItem.includes('command-and-control') || trimmedItem.includes('C2') ||
                            trimmedItem.includes('lateral movement')) {
                            return (
                                <li key={i} className="text-orange-600 dark:text-orange-400 font-medium">
                                    {trimmedItem}
                                </li>
                            );
                        }
                        return (
                            <li key={i} className="text-gray-700 dark:text-gray-300">
                                {trimmedItem}
                            </li>
                        );
                    })}
                </ul>
            );
        }

        // Handle References section - be more flexible for streaming
        if (section.startsWith('References') || section.includes('References')) {
            const referencesContent = section.replace('References', '').trim();
            // Handle both numbered and unnumbered references
            const referenceItems = referencesContent.split(/\d+\.\s*\[KG\]/).filter(item => item.trim());

            if (referenceItems.length > 0) {
                return (
                    <div key={index} className="mt-3 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <h4 className="font-semibold mb-1 text-gray-800 dark:text-gray-200">References</h4>
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                            {referenceItems.map((item, i) => {
                                const trimmedItem = item.trim();
                                if (trimmedItem) {
                                    return (
                                        <div key={i} className="mb-2">
                                            <span className="font-medium">{i + 1}.</span> [KG] {trimmedItem}
                                        </div>
                                    );
                                }
                                return null;
                            }).filter(Boolean)}
                        </div>
                    </div>
                );
            } else {
                // Fallback for incomplete references
                return (
                    <div key={index} className="mt-3 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <h4 className="font-semibold mb-1 text-gray-800 dark:text-gray-200">References</h4>
                        <div className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                            {referencesContent}
                        </div>
                    </div>
                );
            }
        }

        // Handle [KG] citations
        if (section.includes('[KG]')) {
            return (
                <div key={index} className="text-sm text-gray-500 mt-1 p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    {section.split('\n').filter(line => line.trim()).map((line, i) => (
                        <p key={i}>{line.trim()}</p>
                    ))}
                </div>
            );
        }

        // Handle technical details with IP addresses, flow IDs, and protocol information
        if ((section.includes('`') && section.includes('→')) ||
            (section.includes('Flow ID') && section.includes('192.168.')) ||
            section.match(/\d+\.\d+\.\d+\.\d+:\d+/) ||
            section.includes('Protocol 6') ||
            section.includes('SMB port') ||
            section.includes('UDP flows') ||
            section.includes('packets/sec') ||
            section.includes('duration')) {
            return (
                <div key={index} className="my-0.5 p-2 bg-gray-100 dark:bg-gray-700 rounded font-mono text-sm">
                    {section.trim()}
                </div>
            );
        }

        // Handle numbered investigation steps
        if (section.match(/^\d+\.\s*\*\*/)) {
            const stepMatch = section.match(/^(\d+)\.\s*\*\*(.*?)\*\*/);
            if (stepMatch) {
                return (
                    <div key={index} className="my-0.5">
                        <span className="font-semibold text-blue-600 dark:text-blue-400">
                            {stepMatch[1]}. {stepMatch[2]}:
                        </span>
                        <span className="text-gray-700 dark:text-gray-300 ml-1">
                            {section.replace(/^\d+\.\s*\*\*.*?\*\*/, '').trim()}
                        </span>
                    </div>
                );
            }
        }

        // Default paragraph - only render if there's actual content
        const trimmedSection = section.trim();
        if (trimmedSection && !trimmedSection.startsWith('#') && !trimmedSection.startsWith('---')) {
            return (
                <p key={index} className="my-0.5 text-gray-700 dark:text-gray-300">
                    {trimmedSection}
                </p>
            );
        }

        return null;
    }).filter(Boolean); // Remove null elements
};

export const ChatContainer = () => {
    const messages = useMessages();
    const sendMessage = useSendMessage();
    const isLoading = useChatLoading();
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);
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
        if (!input.trim()) return;
        const message = input.trim();
        setInput('');
        await sendMessage(createUserMessage(message, state.dir_path), state.dir_path);
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
                {!state.graphData && (
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
                            className={`max-w-[80%]  transition-colors duration-200 ${message.role === 'user'
                                ? `${isDarkMode ? 'bg-blue-800 text-blue-100' : 'bg-blue-100 text-blue-900'}`
                                : message.isError
                                    ? 'bg-dark text-red-700'
                                    : isDarkMode
                                        ? 'bg-dark text-white'
                                        : 'bg-white text-gray-900'
                                }`}
                        >
                            <div className="p-4 flex flex-col">
                                {message.file && (
                                    <div className={`text-xs opacity-50 mb-2 transition-colors duration-200 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'
                                        }`}>
                                        📎 {message.file.name}
                                    </div>
                                )}
                                <div className="flex justify-end transition-colors duration-200">
                                    <Chip
                                        variant="flat"
                                        startContent={<FolderIcon className="w-5 h-5" />}
                                    >
                                        {message.graph_dir_path || 'No graph selected'}
                                    </Chip>
                                </div>
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
                <div className="flex space-x-4 items-end">
                    <Textarea
                        value={input}
                        minRows={1}
                        maxRows={10}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder={state.graphData ? "Ask about potential threats..." : "Upload a file to enable chat..."}
                        className={`flex-1 transition-colors duration-200 focus:outline-violet-500 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}
                        variant='underlined'
                        disabled={isLoading || !state.graphData}
                    />
                    <Button
                        type="submit"
                        isIconOnly
                        spinner={<div className="flex items-center justify-center">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        </div>}
                        isLoading={isLoading}
                        disabled={!input.trim() || isLoading || !state.graphData}
                        className={`min-w-[40px] h-10 transition-colors duration-200 ${!input.trim() || isLoading || !state.graphData
                            ? isDarkMode
                                ? 'bg-gray-600 text-gray-400 cursor-not-allowed opacity-50'
                                : 'bg-gray-300 text-gray-500 cursor-not-allowed opacity-50'
                            : isDarkMode
                                ? 'bg-gray-700 text-white hover:bg-gray-600'
                                : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
                            }`}
                        title={state.graphData ? "Send message" : "Upload a file to enable chat"}
                    >
                        <PaperAirplaneIcon className="h-5 w-5" />
                    </Button>
                </div>
            </form>
        </div>
    );
}; 