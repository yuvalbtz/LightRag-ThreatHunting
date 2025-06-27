import { useGraphWorker } from "@/hooks/useGraphWorker";
import { Progress } from "@heroui/react";


const KnowledgeGraphRenderingLoader = () => {

    const { stabilizationProgress } = useGraphWorker()

    return (
        <div className="absolute inset-0  backdrop-blur-sm z-10">
            <div className="h-full w-full flex items-center justify-center">
                <div className="bg-blue-900/30 backdrop-blur-lg rounded-full p-2 shadow-2xl">
                    <Progress
                        className='w-[300px]'
                        aria-label="Loading..."
                        size="sm"
                        value={stabilizationProgress}
                    />
                </div>
            </div>
        </div>
    );
};

export default KnowledgeGraphRenderingLoader;