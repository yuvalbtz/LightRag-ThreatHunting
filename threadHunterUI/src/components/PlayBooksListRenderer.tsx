import React from 'react';

interface ItemRendererProps<T> {
    renderItems: T[];
    ComponentType: React.ComponentType<{ item: T }>;
}

function PlayBooksListRenderer<T>({ renderItems, ComponentType }: ItemRendererProps<T>) {
    return (
        <div className="flex-1 overflow-y-auto p-2">
            <div className="grid grid-cols-1 gap-4">
                {renderItems.map((item, idx) => (
                    <ComponentType key={(item as any).id || idx} item={item} />
                ))}
            </div>
        </div>
    );
}

export default PlayBooksListRenderer;
