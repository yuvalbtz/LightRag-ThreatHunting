import React from 'react';
import {
    Navbar as HeroUINavbar,
    NavbarBrand,
    NavbarContent,
    NavbarItem,
    NavbarMenu,
    NavbarMenuItem,
    NavbarMenuToggle,
} from '@heroui/navbar';
import { Link } from '@heroui/link';
import { Button } from '@heroui/button';

interface NavbarProps {
    isDarkMode: boolean;
    isMenuOpen: boolean;
    onThemeToggle: () => void;
    onMenuToggle: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
    isDarkMode,
    isMenuOpen,
    onThemeToggle,
    onMenuToggle
}) => {
    return (
        <HeroUINavbar
            maxWidth="full"
            position="sticky"
            className={`border-b transition-colors duration-200 ${isDarkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'}`}
        >
            <NavbarContent className="basis-1/5 sm:basis-full" justify="start">
                <NavbarBrand className="gap-3 max-w-fit">
                    <Link
                        className="flex justify-start items-center gap-1"
                        color="foreground"
                        href="/"
                    >
                        <h1 className="text-xl font-bold" style={{ color: isDarkMode ? '#60A5FA' : '#3B82F6' }}>ThreatHunter AI</h1>
                    </Link>
                </NavbarBrand>
                <div className="hidden lg:flex gap-4 justify-start ml-2">
                    <NavbarItem>
                        <Link
                            color="foreground"
                            href="/chat"
                            className={`transition-colors duration-200 ${isDarkMode ? 'text-white hover:text-gray-300' : 'text-gray-900 hover:text-gray-600'}`}
                        >
                            Chat
                        </Link>
                    </NavbarItem>
                    <NavbarItem>
                        <Link
                            color="foreground"
                            href="/docs"
                            className={`transition-colors duration-200 ${isDarkMode ? 'text-white hover:text-gray-300' : 'text-gray-900 hover:text-gray-600'}`}
                        >
                            Documentation
                        </Link>
                    </NavbarItem>
                </div>
            </NavbarContent>

            <NavbarContent className="hidden sm:flex basis-1/5 sm:basis-full" justify="end">
                <NavbarItem>
                    <Button
                        isIconOnly
                        variant="light"
                        onPress={onThemeToggle}
                        className={`p-2 transition-colors duration-200 ${isDarkMode ? 'text-white hover:bg-gray-700' : 'text-gray-900 hover:bg-gray-100'}`}
                    >
                        {isDarkMode ? '🌞' : '🌙'}
                    </Button>
                </NavbarItem>
            </NavbarContent>

            <NavbarContent className="sm:hidden basis-1 pl-4" justify="end">
                <NavbarItem>
                    <Button
                        isIconOnly
                        variant="light"
                        onPress={onThemeToggle}
                        className={`p-2 transition-colors duration-200 ${isDarkMode ? 'text-white hover:bg-gray-700' : 'text-gray-900 hover:bg-gray-100'}`}
                    >
                        {isDarkMode ? '🌞' : '🌙'}
                    </Button>
                </NavbarItem>
                <NavbarMenuToggle
                    className={`transition-colors duration-200 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}
                    onClick={onMenuToggle}
                />
            </NavbarContent>

            <NavbarMenu className={`transition-colors duration-200 ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}>
                <NavbarMenuItem>
                    <Link
                        color="foreground"
                        href="/chat"
                        className={`text-lg transition-colors duration-200 ${isDarkMode ? 'text-white hover:text-gray-300' : 'text-gray-900 hover:text-gray-600'}`}
                    >
                        Chat
                    </Link>
                </NavbarMenuItem>
                <NavbarMenuItem>
                    <Link
                        color="foreground"
                        href="/docs"
                        className={`text-lg transition-colors duration-200 ${isDarkMode ? 'text-white hover:text-gray-300' : 'text-gray-900 hover:text-gray-600'}`}
                    >
                        Documentation
                    </Link>
                </NavbarMenuItem>
            </NavbarMenu>
        </HeroUINavbar>
    );
}; 