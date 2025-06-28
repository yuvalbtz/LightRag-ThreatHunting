import { createUserMessage, useChat } from "@/context/ChatContext";
import { useDarkMode } from "@/context/ThemeContext";
import { useGraphWorker } from "@/hooks/useGraphWorker";
import { PaperAirplaneIcon } from "@heroicons/react/24/outline";
import { Button, Textarea } from "@heroui/react";
import { useState } from "react";


const ChatFormPrompt = () => {
    const [input, setInput] = useState("");
    const { isLoading, sendMessage } = useChat();
    const isDarkMode = useDarkMode();
    const state = useGraphWorker();
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;
        const message = input.trim();
        setInput('');
        await sendMessage(createUserMessage(message, state.dir_path), state.dir_path);
    };

    return (
        <form onSubmit={handleSubmit} className={`p-4 border-t transition-colors duration-200 ${isDarkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'}`}>
            <div className="flex space-x-4 items-end">
                <Textarea
                    value={input}
                    minRows={1}
                    maxRows={10}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder={state.graphData ? "Ask about potential threats..." : "Upload a file or select a graph to enable chat..."}
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
    )
}

export default ChatFormPrompt;