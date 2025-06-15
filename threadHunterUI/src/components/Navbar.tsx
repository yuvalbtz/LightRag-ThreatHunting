import React from 'react';
import { Button } from '@heroui/button';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import { useDarkMode } from '../context/ThemeContext';

interface NavbarProps {
    isMenuOpen: boolean;
    onMenuToggle: () => void;
    onThemeToggle: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ isMenuOpen, onMenuToggle, onThemeToggle }) => {
    const isDarkMode = useDarkMode();

    return (
        <nav className={`fixed top-0 left-0 right-0 z-50 transition-colors duration-200 ${isDarkMode ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'} border-b`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center">
                        <button
                            onClick={onMenuToggle}
                            className={`p-2 rounded-md ${isDarkMode ? 'text-gray-300 hover:bg-gray-800' : 'text-gray-500 hover:bg-gray-100'}`}
                        >
                            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        </button>
                        <div className="ml-4 flex items-center">
                            <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                                <div className="flex items-center gap-2">
                                    <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke={isDarkMode ? '#60A5FA' : '#3B82F6'} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                        <path d="M2 17L12 22L22 17" stroke={isDarkMode ? '#60A5FA' : '#3B82F6'} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                        <path d="M2 12L12 17L22 12" stroke={isDarkMode ? '#60A5FA' : '#3B82F6'} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    <span>ThreatHunter AI</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center">
                        <Button
                            isIconOnly
                            variant="light"
                            className={isDarkMode ? 'text-blue-200 hover:bg-gray-800' : 'text-blue-700 hover:bg-blue-100'}
                            onPress={onThemeToggle}
                        >
                            {isDarkMode ? (
                                <SunIcon className="w-6 h-6" />
                            ) : (
                                <MoonIcon className="w-6 h-6" />
                            )}
                        </Button>
                    </div>
                </div>
            </div>
        </nav>
    );
}; 