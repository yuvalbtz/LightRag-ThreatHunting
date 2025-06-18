import { useDarkMode } from "@/context/ThemeContext";
import { useGraphWorker } from "@/hooks/useGraphWorker";
import { api } from "@/services/api";
import { FolderIcon } from "@heroicons/react/24/outline";
import { Select, SelectItem } from "@heroui/react";
import { useState, useMemo } from "react";


const GraphFoldersNamesSelection = () => {
    const [folders, setFolders] = useState<{ key: string, label: string }[]>([]);
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



    return (<Select
        startContent={<FolderIcon className="w-5 h-5" />}
        aria-label="Graph Folder"
        selectedKeys={updateCurrentFolderAndGetFolders}
        isLoading={isLoading}
        onSelectionChange={async (keys) => {
            const selected = Array.from(keys)[0];
            await getGraphData(selected.toString());
        }}
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