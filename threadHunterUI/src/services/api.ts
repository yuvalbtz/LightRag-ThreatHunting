import { createAssistantMessage } from '@/context/ChatContext';
import { GraphData, GraphFoldersNamesResponse, Message, MTAPlayBook, Playbook } from '../types';


const API_BASE_URL = '/api';

export const api = {
    // Graph related API calls
    graph: {
        build: async (file: File): Promise<{ entity_count: number; relationship_count: number }> => {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('source_column', 'Source');
            formData.append('target_column', 'Destination');
            formData.append('working_dir', './AppDbStore/' + file.name?.split('.')[0]);
            const response = await fetch(`${API_BASE_URL}/build-kg`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Failed to build knowledge graph');
            }

            return response.json();
        },

        getData: async (dir_path?: string): Promise<GraphData> => {
            const headers: Record<string, string> = {};
            if (dir_path) {
                headers['dir_path'] = dir_path;
            }

            const response = await fetch(`${API_BASE_URL}/graph-data`, {
                headers
            });
            if (!response.ok) {
                throw new Error('Failed to fetch graph data');
            }
            return response.json();
        },

        search: async (query: string): Promise<GraphData> => {
            const response = await fetch(`${API_BASE_URL}/search-graph?query=${encodeURIComponent(query)}`);
            if (!response.ok) {
                throw new Error('Failed to search graph');
            }
            return response.json();
        },
        getGraphFoldersNames: async (): Promise<GraphFoldersNamesResponse> => {
            const response = await fetch(`${API_BASE_URL}/graph-folders-names`);
            if (!response.ok) {
                throw new Error('Failed to fetch graph folders names');
            }
            return response.json();
        }
    },

    // Chat related API calls
    chat: {
        sendMessage: async (message: string, setMessages: (updater: (prev: Message[]) => Message[]) => void, dir_path: string): Promise<Message> => {

            const response = await fetch(`${API_BASE_URL}/query/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: message,
                    dir_path: './AppDbStore/' + dir_path,
                    conversation_history: []
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to send message');
            }

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();
            let currentResponse = '';

            if (!reader) {
                throw new Error('Failed to get response reader');
            }

            try {
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6);

                            if (data === '[DONE]') {
                                break;
                            }

                            try {
                                const { token } = JSON.parse(data);
                                currentResponse += token;
                                setMessages((prev: Message[]) => {
                                    const newMessages = [...prev];
                                    const lastMessage = newMessages[newMessages.length - 1];
                                    if (lastMessage && lastMessage.role === 'assistant') {
                                        lastMessage.content = currentResponse;
                                    } else {
                                        newMessages.push(createAssistantMessage(currentResponse, dir_path));
                                    }
                                    return newMessages;
                                });
                            } catch (e) {
                                console.error('Error parsing token:', e, 'Data:', data);
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Streaming error:', error);
                throw error;
            }

            return {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: currentResponse,
                timestamp: new Date(),
                graph_dir_path: dir_path
            };
        }
    },

    // Playbook related API calls
    playbooks: {
        getAll: async (year: string, max_samples: number): Promise<MTAPlayBook[]> => {
            const response = await fetch(`${API_BASE_URL}/fetch-all-playbooks?year=${year}&max_samples=${max_samples}`);
            if (!response.ok) {
                throw new Error('Failed to fetch playbooks');
            }
            return response.json();
        }
    }
}; 