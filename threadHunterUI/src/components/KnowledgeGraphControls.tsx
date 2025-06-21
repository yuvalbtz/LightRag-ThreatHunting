import {
    ArrowPathIcon,
    ArrowsPointingOutIcon,
    MagnifyingGlassMinusIcon,
    MagnifyingGlassPlusIcon
} from '@heroicons/react/24/outline';
import { Button } from '@heroui/button';
import { createSystemMessage, useChat } from '../context/ChatContext';
import { useDarkMode } from '../context/ThemeContext';
import { useGraphWorker } from '../hooks/useGraphWorker';


const KnowledgeGraphControls = () => {
    const isDarkMode = useDarkMode();
    const {
        graphData,
        networkInstance,
        resetGraph,
        dir_path,
    } = useGraphWorker();

    const { sendMessage } = useChat();


    const handleReset = async () => {
        resetGraph();
        await sendMessage(createSystemMessage('Graph has been reset. You can now drag and drop a new file.', false, dir_path), dir_path);
    };

    return (
        <>
            {graphData && (
                <div className={`absolute m-auto p-1 left-0 right-0 rounded-full bottom-0 w-fit px-4 mb-1 flex gap-4 justify-center items-center z-20 ${isDarkMode ? 'bg-gray-900/80' : 'bg-white/90'} backdrop-blur-md`}>
                    <Button size="lg" isIconOnly variant="light" title="Zoom In" className={isDarkMode ? 'text-blue-200 hover:bg-gray-800' : 'text-blue-700 hover:bg-blue-100'} onPress={() => {
                        if (networkInstance) {
                            networkInstance.moveTo({
                                scale: networkInstance.getScale() * 1.2
                            });
                        }
                    }}>
                        <MagnifyingGlassPlusIcon className="w-7 h-7" />
                    </Button>
                    <Button size="lg" isIconOnly variant="light" title="Zoom Out" className={isDarkMode ? 'text-blue-200 hover:bg-gray-800' : 'text-blue-700 hover:bg-blue-100'} onPress={() => {
                        if (networkInstance) {
                            networkInstance.moveTo({
                                scale: networkInstance.getScale() * 0.8
                            });
                        }
                    }}>
                        <MagnifyingGlassMinusIcon className="w-7 h-7" />
                    </Button>
                    <Button size="lg" isIconOnly variant="light" title="Fit to View" className={isDarkMode ? 'text-blue-200 hover:bg-gray-800' : 'text-blue-700 hover:bg-blue-100'} onPress={() => {
                        if (networkInstance) {
                            networkInstance.fit({
                                animation: {
                                    duration: 1000,
                                    easingFunction: 'easeInOutQuad'
                                }
                            });
                        }
                    }}>
                        <ArrowsPointingOutIcon className="w-7 h-7" />
                    </Button>
                    <Button size="lg" isIconOnly variant="light" title="Reset Graph" className={isDarkMode ? 'text-blue-200 hover:bg-gray-800' : 'text-blue-700 hover:bg-blue-100'} onPress={handleReset}>
                        <ArrowPathIcon className="w-7 h-7" />
                    </Button>
                </div>
            )}
        </>
    );
};

export default KnowledgeGraphControls;
