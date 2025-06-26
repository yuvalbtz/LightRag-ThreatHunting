import { useChat } from "@/context/ChatContext";
import { useDarkMode } from "@/context/ThemeContext";
import { useGraphWorker } from "@/hooks/useGraphWorker";
import { api } from "@/services/api";
import { FolderIcon } from "@heroicons/react/24/outline";
import { Select, SelectItem, SharedSelection } from "@heroui/react";
import { useState, useMemo } from "react";


const GraphFoldersNamesSelection = () => {
    const [folders, setFolders] = useState<{ key: string, label: string }[]>([]);
    const { fetchGraphLLMConversations } = useChat();
    const isDarkMode = useDarkMode();
    const { getGraphData, dir_path } = useGraphWorker();
    const [isLoading, setIsLoading] = useState(false);

    const updateCurrentFolderAndGetFolders = useMemo(() => {
        if (folders.find((folder) => folder.key === dir_path)) return dir_path ? [dir_path] : [];
        setIsLoading(true);
        api.graph.getGraphFoldersNames().then((res) => {
            setFolders(res.folders.map((folder) => ({ key: folder, label: folder })));
        });
        setIsLoading(false);
        return dir_path ? [dir_path] : [];
    }, [dir_path]);


    const handleSelectionChange = async (keys: SharedSelection) => {
        try {
            const selectedFolder = Array.from(keys)[0];
            await fetchGraphLLMConversations(selectedFolder.toString());
            await getGraphData(selectedFolder.toString());
        } catch (error) {
            console.error('Error fetching graph LLM conversations:', error);
        }
    }







    return (<Select
        startContent={<FolderIcon className="w-5 h-5" />}
        aria-label="Graph Folder"
        selectedKeys={updateCurrentFolderAndGetFolders}
        isLoading={isLoading}
        onSelectionChange={handleSelectionChange}
        listboxProps={{ emptyContent: 'No graph folders found' }}
        classNames={{ popoverContent: isDarkMode ? 'bg-gray-800/80 text-white' : '' }}
        className={`w-[300px] ${isDarkMode ? 'text-white' : 'text-gray-900'}`}
        variant="underlined"
        size="sm"
        placeholder="Select a Graph folder"
    >
        {folders.map((folder) => (
            <SelectItem key={folder.key}>{folder.label}</SelectItem>
        ))}
    </Select>
    )
}

export default GraphFoldersNamesSelection;