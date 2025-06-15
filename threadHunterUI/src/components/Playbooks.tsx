import React, { useState, useMemo } from 'react';
import { Card, CardBody } from '@heroui/card';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';

// Simple search icon component
const SearchIcon = ({ className }: { className?: string }) => (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1.5}
        stroke="currentColor"
        className={className}
    >
        <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
        />
    </svg>
);

interface Playbook {
    id: string;
    name: string;
    type: 'malware' | 'exploit';
    description: string;
    indicators: string[];
    severity: 'low' | 'medium' | 'high' | 'critical';
}

interface PlaybooksProps {
    onSelectPlaybook: (playbook: Playbook) => void;
    isDarkMode: boolean;
    onSearchGraph: (query: string) => void;
}

const severityColors = {
    critical: {
        light: 'bg-red-500 text-white',
        dark: 'bg-red-600 text-white'
    },
    high: {
        light: 'bg-orange-500 text-white',
        dark: 'bg-orange-600 text-white'
    },
    medium: {
        light: 'bg-yellow-500 text-white',
        dark: 'bg-yellow-600 text-white'
    },
    low: {
        light: 'bg-green-500 text-white',
        dark: 'bg-green-600 text-white'
    }
};

const playbooks: Playbook[] = [
    {
        id: '1',
        name: 'Ransomware Detection',
        type: 'malware',
        description: 'Detect and analyze ransomware activities in the network',
        indicators: ['encrypted_files', 'ransom_note', 'bitcoin_wallet'],
        severity: 'critical'
    },
    {
        id: '2',
        name: 'SQL Injection Prevention',
        type: 'exploit',
        description: 'Prevent and detect SQL injection attacks',
        indicators: ['sql_queries', 'database_errors', 'suspicious_input'],
        severity: 'high'
    },
    {
        id: '3',
        name: 'Phishing Campaign Analysis',
        type: 'malware',
        description: 'Analyze and track phishing campaign activities',
        indicators: ['suspicious_emails', 'malicious_links', 'credential_theft'],
        severity: 'high'
    },
    {
        id: '4',
        name: 'XSS Attack Detection',
        type: 'exploit',
        description: 'Detect cross-site scripting attacks',
        indicators: ['script_tags', 'event_handlers', 'encoded_payloads'],
        severity: 'high'
    },
    {
        id: '5',
        name: 'Data Exfiltration Monitor',
        type: 'malware',
        description: 'Monitor and detect data exfiltration attempts',
        indicators: ['large_data_transfers', 'unusual_ports', 'compressed_files'],
        severity: 'critical'
    },
    {
        id: '6',
        name: 'Privilege Escalation Detection',
        type: 'exploit',
        description: 'Detect attempts to escalate user privileges',
        indicators: ['sudo_commands', 'kernel_exploits', 'service_abuse'],
        severity: 'high'
    },
    {
        id: '7',
        name: 'Malware Command & Control',
        type: 'malware',
        description: 'Detect malware command and control communications',
        indicators: ['dns_tunneling', 'beaconing', 'encrypted_traffic'],
        severity: 'critical'
    },
    {
        id: '8',
        name: 'Web Shell Detection',
        type: 'exploit',
        description: 'Detect web shell installations and usage',
        indicators: ['php_shells', 'jsp_shells', 'suspicious_uploads'],
        severity: 'high'
    },
    {
        id: '9',
        name: 'Credential Dumping',
        type: 'malware',
        description: 'Detect attempts to dump system credentials',
        indicators: ['lsass_dumps', 'registry_access', 'memory_scans'],
        severity: 'critical'
    },
    {
        id: '10',
        name: 'Lateral Movement',
        type: 'exploit',
        description: 'Detect lateral movement attempts in the network',
        indicators: ['remote_execution', 'network_scans', 'service_enumeration'],
        severity: 'high'
    },
    {
        id: '11',
        name: 'Supply Chain Attack',
        type: 'malware',
        description: 'Detect supply chain compromise attempts',
        indicators: ['package_tampering', 'unsigned_updates', 'vendor_compromise'],
        severity: 'critical'
    },
    {
        id: '12',
        name: 'Zero-Day Exploit Detection',
        type: 'exploit',
        description: 'Detect potential zero-day exploit attempts',
        indicators: ['crash_reports', 'memory_corruption', 'unusual_behavior'],
        severity: 'critical'
    },
    {
        id: '13',
        name: 'Cryptocurrency Mining',
        type: 'malware',
        description: 'Detect unauthorized cryptocurrency mining',
        indicators: ['high_cpu_usage', 'mining_pools', 'gpu_abuse'],
        severity: 'medium'
    },
    {
        id: '14',
        name: 'API Abuse Detection',
        type: 'exploit',
        description: 'Detect API abuse and unauthorized access',
        indicators: ['rate_limiting', 'token_theft', 'endpoint_abuse'],
        severity: 'high'
    },
    {
        id: '15',
        name: 'Insider Threat Detection',
        type: 'malware',
        description: 'Detect potential insider threat activities',
        indicators: ['data_access', 'unusual_times', 'privilege_abuse'],
        severity: 'high'
    },
    {
        id: '16',
        name: 'Cloud Service Abuse',
        type: 'exploit',
        description: 'Detect abuse of cloud services and resources',
        indicators: ['resource_exhaustion', 'unauthorized_apis', 'cost_anomalies'],
        severity: 'medium'
    },
    {
        id: '17',
        name: 'Mobile Malware Detection',
        type: 'malware',
        description: 'Detect mobile malware and suspicious apps',
        indicators: ['suspicious_permissions', 'fake_apps', 'data_leakage'],
        severity: 'high'
    },
    {
        id: '18',
        name: 'Container Escape Detection',
        type: 'exploit',
        description: 'Detect container escape attempts',
        indicators: ['privilege_escalation', 'host_access', 'namespace_breakout'],
        severity: 'critical'
    },
    {
        id: '19',
        name: 'Social Engineering',
        type: 'malware',
        description: 'Detect social engineering attempts',
        indicators: ['phishing_emails', 'impersonation', 'urgent_requests'],
        severity: 'medium'
    },
    {
        id: '20',
        name: 'IoT Device Compromise',
        type: 'exploit',
        description: 'Detect IoT device compromise attempts',
        indicators: ['default_credentials', 'firmware_tampering', 'unusual_traffic'],
        severity: 'high'
    }
];

type PlaybookType = 'All Types' | 'Malware' | 'Exploits';
type PlaybookSeverity = 'All Severities' | 'Critical' | 'High' | 'Medium' | 'Low';

export const Playbooks: React.FC<PlaybooksProps> = ({ onSelectPlaybook, isDarkMode, onSearchGraph }) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedType, setSelectedType] = useState<PlaybookType>('All Types');
    const [selectedSeverity, setSelectedSeverity] = useState<PlaybookSeverity>('All Severities');

    const filteredPlaybooks = useMemo(() => {
        return playbooks.filter(playbook => {
            const searchTerms = searchQuery.toLowerCase().split(' ');
            const matchesSearch = searchTerms.every(term =>
                playbook.name.toLowerCase().includes(term) ||
                playbook.description.toLowerCase().includes(term) ||
                playbook.indicators.some(indicator => indicator.toLowerCase().includes(term))
            );

            const matchesType = selectedType === 'All Types' ||
                (selectedType === 'Malware' && playbook.type === 'malware') ||
                (selectedType === 'Exploits' && playbook.type === 'exploit');

            const matchesSeverity = selectedSeverity === 'All Severities' ||
                playbook.severity === selectedSeverity.toLowerCase();

            return matchesSearch && matchesType && matchesSeverity;
        });
    }, [searchQuery, selectedType, selectedSeverity]);

    const handleSearchGraph = (playbook: Playbook) => {
        const searchQuery = `${playbook.name} ${playbook.indicators.join(' ')}`;
        onSearchGraph(searchQuery);
    };

    return (
        <div className={`p-4 h-full flex flex-col ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}>
            {/* Search and Filters - Fixed at top */}
            <div className="mb-4">
                <div className="relative mb-4">
                    <Input
                        type="text"
                        placeholder="Search playbooks..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        startContent={<SearchIcon className={`relative left-0 top-0  w-5 h-5 ${isDarkMode ? 'text-white' : 'text-gray-500'}`} />}
                        variant='underlined'
                        className={`w-full pl-0`}
                    />
                </div>

                {/* Type Filters */}
                <div className="flex gap-2 mb-4">
                    {(['All Types', 'Malware', 'Exploits'] as const).map((type) => (
                        <Button
                            key={type}
                            size="sm"
                            variant={selectedType === type ? 'solid' : 'light'}
                            className={`${isDarkMode
                                ? selectedType === type
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                : selectedType === type
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                            onClick={() => setSelectedType(type)}
                        >
                            {type}
                        </Button>
                    ))}
                </div>

                {/* Severity Filters */}
                <div className="flex gap-2 mb-4">
                    {(['All Severities', 'Critical', 'High', 'Medium', 'Low'] as const).map((severity) => (
                        <Button
                            key={severity}
                            size="sm"
                            variant={selectedSeverity === severity ? 'solid' : 'light'}
                            className={`${isDarkMode
                                ? selectedSeverity === severity
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                : selectedSeverity === severity
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                            onClick={() => setSelectedSeverity(severity)}
                        >
                            {severity}
                        </Button>
                    ))}
                </div>
            </div>

            {/* Scrollable Cards Section */}
            <div className="flex-1 overflow-y-auto p-2">
                <div className="grid grid-cols-1 gap-4">
                    {filteredPlaybooks.map((playbook) => (
                        <Card
                            key={playbook.id}
                            className={`cursor-pointer transition-all duration-200  ${isDarkMode
                                ? 'bg-gray-700 hover:bg-gray-600'
                                : 'bg-white hover:bg-gray-50'
                                }`}
                            onClick={() => onSelectPlaybook(playbook)}
                        >
                            <CardBody>
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className={`text-lg font-semibold mb-2 ${isDarkMode ? 'text-white' : 'text-gray-900'
                                            }`}>
                                            {playbook.name}
                                        </h3>
                                        <p className={`text-sm mb-4 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'
                                            }`}>
                                            {playbook.description}
                                        </p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${isDarkMode
                                            ? 'bg-gray-600 text-gray-200'
                                            : 'bg-gray-100 text-gray-700'
                                            }`}>
                                            {playbook.type}
                                        </span>
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${isDarkMode
                                            ? severityColors[playbook.severity].dark
                                            : severityColors[playbook.severity].light
                                            }`}>
                                            {playbook.severity}
                                        </span>
                                        <Button
                                            isIconOnly
                                            size="sm"
                                            variant="light"
                                            className={`${isDarkMode
                                                ? 'text-gray-400 hover:text-white hover:bg-gray-600'
                                                : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'
                                                }`}
                                            onPress={(e: any) => {
                                                e.stopPropagation();
                                                handleSearchGraph(playbook);
                                            }}
                                        >
                                            <SearchIcon className="w-4 h-4" />
                                        </Button>
                                    </div>
                                </div>
                                <div className="flex flex-wrap items-center gap-2 justify-between mt-2">
                                    <div className="flex flex-wrap gap-2">
                                        {playbook.indicators.map((indicator, index) => (
                                            <span
                                                key={index}
                                                className={`px-2 py-1 rounded-full text-xs font-medium ${isDarkMode
                                                    ? 'bg-gray-600 text-gray-200'
                                                    : 'bg-gray-100 text-gray-700'
                                                    }`}
                                            >
                                                {indicator}
                                            </span>
                                        ))}
                                    </div>
                                    <Button
                                        size="sm"
                                        variant="light"
                                        className={`${isDarkMode
                                            ? 'bg-blue-900/10 text-blue-300 hover:bg-blue-900/20'
                                            : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                                            } px-3 py-1 rounded-full text-xs font-medium shadow-none border-none ml-2`}
                                        onPress={(e: any) => {
                                            e.stopPropagation();
                                            alert(`View details for: ${playbook.name}`);
                                        }}
                                    >
                                        View Details
                                    </Button>
                                </div>
                            </CardBody>
                        </Card>
                    ))}
                </div>
            </div>
        </div >
    );
}; 