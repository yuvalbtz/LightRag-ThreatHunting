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
                    'Accept': 'text/event-stream',
                },
                body: JSON.stringify({
                    query: message,
                    dir_path: dir_path,
                    conversation_history: []
                }),
            });


            if (!response.ok) {
                throw new Error('Failed to send message');
            }

            // Check if response is streaming
            const contentType = response.headers.get('content-type');
            console.log('Response content-type:', contentType);

            if (!contentType?.includes('text/event-stream')) {
                console.warn('Response is not streaming, falling back to regular response');
                const text = await response.text();
                return {
                    id: crypto.randomUUID(),
                    role: 'assistant',
                    content: text,
                    timestamp: new Date(),
                    graph_dir_path: dir_path
                };
            }


            // Check if response body is actually a readable stream
            if (!(response.body instanceof ReadableStream)) {
                console.error('Response body is not a ReadableStream!');

                // Try to get the full response text
                const text = await response.text();


                // Try to parse the response as SSE
                const lines = text.split('\n');
                console.log('Response lines:', lines);

                let currentResponse = '';
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') {
                            console.log('Found [DONE] in text response');
                            continue;
                        }
                        try {
                            const parsedData = JSON.parse(data);
                            if (parsedData.token) {
                                console.log('Found token in text response:', parsedData.token);
                                currentResponse += parsedData.token;
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
                            }
                        } catch (e) {
                            console.error('Error parsing token from text:', e, 'Data:', data);
                        }
                    }
                }

                if (!currentResponse.trim()) {
                    currentResponse = 'Sorry, I was unable to generate a response. Please try again.';
                }

                return {
                    id: crypto.randomUUID(),
                    role: 'assistant',
                    content: currentResponse,
                    timestamp: new Date(),
                    graph_dir_path: dir_path
                };
            }

            const reader = response.body?.getReader();
            console.log('Reader created:', !!reader);
            console.log('Reader type:', typeof reader);

            const decoder = new TextDecoder();
            let currentResponse = '';
            let buffer = '';

            if (!reader) {
                throw new Error('Failed to get response reader');
            }

            try {
                let chunkCount = 0;
                console.log('Starting to read chunks...');
                while (true) {
                    console.log(`About to read chunk #${chunkCount + 1}...`);
                    const { done, value } = await reader.read();
                    chunkCount++;
                    console.log(`Chunk #${chunkCount} - done: ${done}, value length: ${value?.length || 0}`);
                    console.log(`Value type: ${typeof value}, Value:`, value);
                    console.log(`Value as Uint8Array:`, value instanceof Uint8Array ? Array.from(value) : 'Not Uint8Array');

                    if (done) {
                        console.log('Stream reader done');
                        break;
                    }

                    const chunk = decoder.decode(value, { stream: true });
                    console.log('Received chunk:', JSON.stringify(chunk));
                    console.log('Chunk length:', chunk.length);
                    console.log('Chunk contains [DONE]:', chunk.includes('[DONE]'));
                    console.log('Chunk contains data: :', chunk.includes('data: '));

                    // Add to buffer and process complete lines
                    buffer += chunk;

                    while (true) {
                        const newlineIndex = buffer.indexOf('\n');
                        if (newlineIndex === -1) {
                            // No complete line yet, wait for more data
                            console.log('No complete line found, waiting for more data');
                            break;
                        }

                        const line = buffer.substring(0, newlineIndex).trim();
                        buffer = buffer.substring(newlineIndex + 1);

                        console.log('Processing line:', JSON.stringify(line));
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6);
                            console.log('Processing data line:', data);

                            if (data === '[DONE]') {
                                console.log('Received [DONE] signal');
                                // Don't break here, continue processing any remaining tokens
                                continue;
                            }

                            try {
                                const parsedData = JSON.parse(data);
                                console.log('Parsed data:', parsedData);

                                // Handle error tokens from server
                                if (parsedData.error) {
                                    console.error('Received error from server:', parsedData.error);
                                    throw new Error(parsedData.error);
                                }

                                // Handle regular tokens
                                if (parsedData.token) {
                                    console.log('Adding token to response:', parsedData.token);
                                    currentResponse += parsedData.token;
                                    console.log('Current response so far:', currentResponse);
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
                                } else {
                                    console.log('No token found in parsed data:', parsedData);
                                }
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

            // Check if we got any response
            if (!currentResponse.trim()) {
                console.warn('No response content received from server');
                currentResponse = 'Sorry, I was unable to generate a response. Please try again.';
            }

            return {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: currentResponse,
                timestamp: new Date(),
                graph_dir_path: dir_path
            };
        },

        getGraphLLMConversations: async (dir_path: string): Promise<Message[]> => {
            try {
                const response = await fetch(`${API_BASE_URL}/graph-llm-conversations?dir_path=${dir_path}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch graph LLM conversations');
                }
                return response.json();
            } catch (error) {
                console.error('Error fetching graph LLM conversations:', error);
                throw error;
            }
        },
    },
    // Playbook related API calls
    playbooks: {
        getAll: async (state: { type: "link" | "yearAndCount", queryParamsString: string }): Promise<MTAPlayBook[]> => {
            const response = await fetch(`${API_BASE_URL}/fetch-all-playbooks?type=${state.type}&${state.queryParamsString}`);
            if (!response.ok) {
                throw new Error('Failed to fetch playbooks');
            }
            return response.json();
        }
    }
}; 