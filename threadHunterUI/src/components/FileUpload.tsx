import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

interface FileUploadProps {
    onFileUpload: (file: File) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload }) => {
    const [file, setFile] = useState<File | null>(null);
    const [error, setError] = useState<string>('');

    const onDrop = useCallback((acceptedFiles: File[]) => {
        const uploadedFile = acceptedFiles[0];
        if (uploadedFile) {
            const fileExtension = uploadedFile.name.split('.').pop()?.toLowerCase();
            if (fileExtension === 'csv' || fileExtension === 'pcap') {
                setFile(uploadedFile);
                setError('');
                onFileUpload(uploadedFile);
            } else {
                setError('Please upload a CSV or PCAP file');
            }
        }
    }, [onFileUpload]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'text/csv': ['.csv'],
            'application/vnd.tcpdump.pcap': ['.pcap']
        },
        maxFiles: 1
    });

    return (
        <div className="w-full max-w-xl mx-auto">
            <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}`}
            >
                <input {...getInputProps()} />
                <div className="space-y-4">
                    <div className="text-4xl">📁</div>
                    {isDragActive ? (
                        <p className="text-blue-500">Drop the file here...</p>
                    ) : (
                        <div>
                            <p className="text-gray-600">Drag and drop your file here, or click to select</p>
                            <p className="text-sm text-gray-500 mt-2">Supported formats: CSV, PCAP</p>
                        </div>
                    )}
                </div>
            </div>

            {file && (
                <div className="mt-4 p-4 bg-green-50 rounded-lg">
                    <p className="text-green-700">File selected: {file.name}</p>
                </div>
            )}

            {error && (
                <div className="mt-4 p-4 bg-red-50 rounded-lg">
                    <p className="text-red-700">{error}</p>
                </div>
            )}
        </div>
    );
};

export default FileUpload; 