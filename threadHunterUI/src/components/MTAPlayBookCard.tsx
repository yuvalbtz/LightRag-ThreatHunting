import { Button, Card, CardBody } from "@heroui/react";
import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { MTAPlayBook } from "@/types";
import { useTheme } from "@/context/ThemeContext";
import { SearchIcon } from './icons';
import { api } from "@/services/api";
import { createUserMessage, useChat, useChatLoading } from "@/context/ChatContext";
import { useGraphWorker } from "@/hooks/useGraphWorker";
import { useState } from "react";

const severityColors = {
    critical: {
        light: 'bg-red-500 text-white',
        dark: 'bg-red-600 text-white'
    },
    high: {
        light: 'bg-orange-500 text-white',
        dark: 'bg-orange-600 text-white'
    },
    medium: {
        light: 'bg-yellow-500 text-white',
        dark: 'bg-yellow-600 text-white'
    },
    low: {
        light: 'bg-green-500 text-white',
        dark: 'bg-green-600 text-white'
    }
};



const MTAPlayBookCard = ({ playbook, onSelectPlaybook, handleSearchGraph }: { playbook: MTAPlayBook, onSelectPlaybook: (playbook: MTAPlayBook) => void, handleSearchGraph: (playbook: MTAPlayBook) => void }) => {
    const { isDarkMode } = useTheme();
    const { sendMessage } = useChat();
    const { dir_path } = useGraphWorker()
    const [loading, setLoading] = useState(false);
    const isChatLoading = useChatLoading();

    const sendPlaybookToAgent = async (playbook: MTAPlayBook) => {
        setLoading(true);
        try {
            const prompt = playbook.generated_prompt.split('\n').map(line => {
                return `- ${line}`;
            }).join('\n');
            const fullMessage = `${playbook.hunt_goal}\n\nfollow the next instructions:\n\n${prompt}`
            await sendMessage(createUserMessage(fullMessage, dir_path), dir_path);

        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }
    // Generate a unique key for the card
    const cardKey = `${playbook.sample_url}-${Array.isArray(playbook.malware_name) ? playbook.malware_name.join('-') : playbook.malware_name}`;

    // Extract malware name for display
    const malwareName = Array.isArray(playbook.malware_name) ? playbook.malware_name.join(', ') : playbook.malware_name;

    return <Card
        key={cardKey}
        className={`cursor-pointer transition-all duration-200  ${isDarkMode
            ? 'bg-gray-700 hover:bg-gray-600'
            : 'bg-white hover:bg-gray-50'
            }`}
        onPress={() => onSelectPlaybook(playbook)}
    >
        <CardBody>
            <div className="flex justify-between items-start">
                <div>
                    <h3 className={`text-lg font-semibold mb-2 ${isDarkMode ? 'text-white' : 'text-gray-900'
                        }`}>
                        {malwareName}
                    </h3>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${isDarkMode
                        ? 'bg-gray-600 text-gray-200'
                        : 'bg-gray-100 text-gray-700'
                        }`}>
                        MTA
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${isDarkMode
                        ? severityColors.medium.dark
                        : severityColors.medium.light
                        }`}>
                        Medium
                    </span>
                    <Button
                        isLoading={loading}
                        isDisabled={isChatLoading}
                        isIconOnly
                        size="sm"
                        variant="light"
                        className={`${isDarkMode
                            ? 'text-gray-400 hover:text-white hover:bg-gray-600'
                            : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'
                            }`}
                        onPress={(e: any) => sendPlaybookToAgent(playbook)}
                    >
                        <SearchIcon className="w-4 h-4" />
                    </Button>
                </div>
            </div>
            <div className="flex flex-wrap items-center gap-2 justify-between mt-2">
                <div className="flex flex-wrap gap-2">
                     <p className={`text-sm mb-4 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'
                        }`}>
                        {playbook.hunt_goal}
                    </p>
                    <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${isDarkMode
                            ? 'bg-gray-600 text-gray-200'
                            : 'bg-gray-100 text-gray-700'
                            }`}
                    >
                        {playbook.sample_url}
                    </span>
                </div>
                <Button
                    size="sm"
                    variant="light"
                    className={`${isDarkMode
                        ? 'bg-blue-900/10 text-blue-300 hover:bg-blue-900/20'
                        : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                        } px-3 py-1 rounded-full text-xs font-medium shadow-none border-none ml-2`}
                    onPress={(e: any) => {
                        e.stopPropagation();
                        alert(`View details for: ${malwareName}`);
                    }}
                >
                    View Details
                </Button>
            </div>
        </CardBody>
    </Card>
};

export default MTAPlayBookCard;
