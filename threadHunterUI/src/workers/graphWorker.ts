import { GraphData, GraphNode, GraphEdge } from '../types';




// Process graph data for visualization
self.onmessage = async (e: MessageEvent) => {
    const { type, data } = e.data;
    const API_BASE_URL = '/api'
    switch (type) {
        case 'PROCESS_GRAPH_DATA':
            const processedData = processGraphData(data);
            self.postMessage({ type: 'GRAPH_DATA_PROCESSED', data: processedData });
            break;

        case 'BUILD_GRAPH':
            try {
                const formData = new FormData();
                formData.append('file', data.file);
                formData.append('max_rows', data.kg_settings.max_rows.toString());
                formData.append('source_column', 'Source IP');
                formData.append('target_column', 'Destination IP');
                formData.append('working_dir', './AppDbStore/' + data.file.name?.split('.')[0]);

                const response = await fetch(`${API_BASE_URL}/build-kg`, {
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) {
                    throw new Error('Failed to build graph');
                }

                const result = await response.json();
                self.postMessage({ type: 'GRAPH_BUILT', data: result });
            } catch (error) {
                self.postMessage({ type: 'GRAPH_BUILD_ERROR', error: error instanceof Error ? error.message : 'Unknown error' });
            }
            break;

        case 'GET_GRAPH_DATA':
            try {
                const dir_path = data?.dir_path || './custom_kg';
                const response = await fetch(`${API_BASE_URL}/graph-data?dir_path=${dir_path}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch graph data');
                }

                const graphData = await response.json();
                self.postMessage({ type: 'GRAPH_DATA_FETCHED', data: graphData });
            } catch (error) {
                self.postMessage({ type: 'GRAPH_DATA_ERROR', error: error instanceof Error ? error.message : 'Unknown error' });
            }
            break;

        case 'SEARCH_NODES':
            const searchResults = searchNodes(data.nodes, data.query);
            self.postMessage({ type: 'SEARCH_RESULTS', data: searchResults });
            break;
    }
};

function processGraphData(data: GraphData): GraphData {
    // Process nodes
    const processedNodes = data.nodes.map(node => ({
        ...node,
        // Add any node processing logic here
        title: node.label, // Add tooltip
        color: node.color || '#4B5563', // Default color if none specified
    }));

    // Process edges
    const processedEdges = data.edges.map(edge => {
        const fromNode = data.nodes.find(n => n.id === edge.from);
        const toNode = data.nodes.find(n => n.id === edge.to);
        const edgeTitle = edge.label || `${fromNode?.label || edge.from} → ${toNode?.label || edge.to}`;
        return {
            ...edge,
            title: edgeTitle,
            label: edgeTitle,
            arrows: {
                to: { enabled: true, scaleFactor: 1 }
            },
            smooth: {
                enabled: true,
                type: 'continuous',
                roundness: 0.5
            }
        };
    });

    return {
        nodes: processedNodes,
        edges: processedEdges
    };
}

function searchNodes(nodes: GraphNode[], query: string): GraphNode[] {
    const searchTerm = query.toLowerCase();
    return nodes.filter(node =>
        node.label.toLowerCase().includes(searchTerm) ||
        node.id.toString().toLowerCase().includes(searchTerm)
    );
}

// Export types for TypeScript
export type { GraphNode, GraphEdge, GraphData }; 