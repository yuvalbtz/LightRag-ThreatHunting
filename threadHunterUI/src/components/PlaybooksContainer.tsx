import React from 'react';
import { Playbooks } from './Playbooks';

interface Playbook {
    id: string;
    name: string;
    type: 'malware' | 'exploit';
    description: string;
    indicators: string[];
    severity: 'low' | 'medium' | 'high' | 'critical';
}

interface PlaybooksContainerProps {
    isDarkMode: boolean;
    onSelectPlaybook: (playbook: Playbook) => void;
    onSearchGraph: (query: string) => void;
}

export const PlaybooksContainer: React.FC<PlaybooksContainerProps> = ({
    isDarkMode,
    onSelectPlaybook,
    onSearchGraph
}) => {
    return (
        <div className={`w-1/3 border-r transition-colors duration-200 ${isDarkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'}`}>
            <div className="h-full overflow-y-auto">
                <Playbooks
                    onSelectPlaybook={onSelectPlaybook}
                    isDarkMode={isDarkMode}
                    onSearchGraph={onSearchGraph}
                />
            </div>
        </div>
    );
}; 