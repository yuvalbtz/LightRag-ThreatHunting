import React from 'react';
import { createContext, useContextSelector } from 'use-context-selector';
import { useTheme as useHeroUITheme } from '@heroui/use-theme';
interface ThemeContextType {
    isDarkMode: boolean;
    toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | null>(null);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { theme, setTheme } = useHeroUITheme();

    const toggleTheme = React.useCallback(() => {
        setTheme(theme === 'dark' ? 'light' : 'dark');
    }, [theme]);


    return (
        <ThemeContext.Provider value={{ isDarkMode: theme === 'dark', toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = () => {
    const context = useContextSelector(ThemeContext, (state) => state);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};

// Selector hook for dark mode state
export const useDarkMode = () => {
    const isDarkMode = useContextSelector(ThemeContext, (state) => state?.isDarkMode);
    if (isDarkMode === undefined) {
        throw new Error('useDarkMode must be used within a ThemeProvider');
    }
    return isDarkMode;
}; 