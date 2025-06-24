import { Card, CardBody, Button } from '@heroui/react';
import { Playbook } from '@/types';
import { SearchIcon } from './icons';
import { useTheme } from '@heroui/use-theme';
import { useChatLoading } from '@/context/ChatContext';

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



const PlayBookCard = ({ playbook, onSelectPlaybook, handleSearchGraph }: { playbook: Playbook, onSelectPlaybook: (playbook: Playbook) => void, handleSearchGraph: (playbook: Playbook) => void }) => {
    const { theme } = useTheme();
    const isDarkMode = theme === 'dark';
    return <Card
        key={playbook.id}
        className={`cursor-pointer transition-all duration-200  ${isDarkMode
            ? 'bg-gray-700 hover:bg-gray-600'
            : 'bg-white hover:bg-gray-50'
            }`}
        onClick={() => onSelectPlaybook(playbook)}
    >
        <CardBody>
            <div className="flex justify-between items-start">
                <div>
                    <h3 className={`text-lg font-semibold mb-2 ${isDarkMode ? 'text-white' : 'text-gray-900'
                        }`}>
                        {playbook.name}
                    </h3>
                    <p className={`text-sm mb-4 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'
                        }`}>
                        {playbook.description}
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${isDarkMode
                        ? 'bg-gray-600 text-gray-200'
                        : 'bg-gray-100 text-gray-700'
                        }`}>
                        {playbook.type}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${isDarkMode
                        ? severityColors[playbook.severity].dark
                        : severityColors[playbook.severity].light
                        }`}>
                        {playbook.severity}
                    </span>
                    <Button
                        isIconOnly
                        size="sm"
                        variant="light"
                        className={`${isDarkMode
                            ? 'text-gray-400 hover:text-white hover:bg-gray-600'
                            : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'
                            }`}
                        onPress={(e: any) => {
                            e.stopPropagation();
                            handleSearchGraph(playbook);
                        }}
                    >
                        <SearchIcon className="w-4 h-4" />
                    </Button>
                </div>
            </div>
            <div className="flex flex-wrap items-center gap-2 justify-between mt-2">
                <div className="flex flex-wrap gap-2">
                    {playbook.indicators.map((indicator, index) => (
                        <span
                            key={index}
                            className={`px-2 py-1 rounded-full text-xs font-medium ${isDarkMode
                                ? 'bg-gray-600 text-gray-200'
                                : 'bg-gray-100 text-gray-700'
                                }`}
                        >
                            {indicator}
                        </span>
                    ))}
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
                        alert(`View details for: ${playbook.name}`);
                    }}
                >
                    View Details
                </Button>
            </div>
        </CardBody>
    </Card>
};

export default PlayBookCard;