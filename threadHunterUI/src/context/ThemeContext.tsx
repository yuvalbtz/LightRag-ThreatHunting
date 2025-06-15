import React from 'react';
import { createContext, useContextSelector } from 'use-context-selector';

interface ThemeContextType {
    isDarkMode: boolean;
    toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | null>(null);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [isDarkMode, setIsDarkMode] = React.useState(() => {
        const saved = localStorage.getItem('darkMode');
        return saved ? JSON.parse(saved) : false;
    });

    const toggleTheme = React.useCallback(() => {
        setIsDarkMode((prev: boolean) => {
            const newValue = !prev;
            localStorage.setItem('darkMode', JSON.stringify(newValue));
            return newValue;
        });
    }, []);

    const value = React.useMemo(() => ({
        isDarkMode,
        toggleTheme
    }), [isDarkMode, toggleTheme]);

    return (
        <ThemeContext.Provider value={value}>
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