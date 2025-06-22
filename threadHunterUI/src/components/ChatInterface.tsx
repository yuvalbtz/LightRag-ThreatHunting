import React, { useState } from 'react';
import { Navbar } from './navigation/Navbar';
import { KnowledgeGraphContainer } from './KnowledgeGraphContainer';
import { ChatContainer } from './ChatContainer';
import { PlaybooksContainer } from './PlaybooksContainer';
import { useTheme } from '../context/ThemeContext';

export const ChatInterface: React.FC = () => {
    const { isDarkMode, toggleTheme } = useTheme();
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const handlePlaybookSelect = () => {
        // sendMessage(`Selected playbook: ${playbook.name}`, null);
    };

    const handleGraphSearch = () => {
        // sendMessage(`Searching graph for: ${query}`, null);
    };

    return (
        <div className={`flex flex-col flex-1 h-screen transition-colors duration-200 ${isDarkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
            <Navbar
                isDarkMode={isDarkMode}
                onThemeToggle={toggleTheme}
                isMenuOpen={isMenuOpen}
                onMenuToggle={() => setIsMenuOpen(!isMenuOpen)}
            />
            <div className="flex-1 flex overflow-hidden">
                <KnowledgeGraphContainer />
                <PlaybooksContainer />
                <ChatContainer />
            </div>
        </div>
    );
};  