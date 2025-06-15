import { ChatInterface } from './components/ChatInterface';
import { Providers } from './context/Providers';
import { useTheme } from './context/ThemeContext';

function App() {
  const { isDarkMode } = useTheme();

  return (
    <div className={`min-h-screen bg-gray-50 ${isDarkMode ? 'dark' : ''}`}>
      <Providers>
        <ChatInterface />
      </Providers>
    </div>
  );
}

export default App;
