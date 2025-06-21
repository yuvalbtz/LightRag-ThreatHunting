import { useGraphWorker } from "../hooks/useGraphWorker";

const KnowledgeGraphNetwork = () => {
    const { networkRef } = useGraphWorker();

    return (
        <div ref={networkRef} className="w-full h-[100%]" />
    );
};

export default KnowledgeGraphNetwork;