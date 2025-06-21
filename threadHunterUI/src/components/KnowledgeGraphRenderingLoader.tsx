import { useGraphWorker } from "@/hooks/useGraphWorker";
import { Progress } from "@heroui/react";


const KnowledgeGraphRenderingLoader = () => {

    const { stabilizationProgress } = useGraphWorker()

    return <div className="absolute inset-0 flex items-center justify-center z-10">
        <Progress className='w-[50%]' aria-label="Loading..." size="sm" value={stabilizationProgress} />
    </div>
};

export default KnowledgeGraphRenderingLoader;