import React, { useState, useMemo } from 'react';
import { Button, Input } from '@heroui/react';
import PlayBookCard from './PlayBookCard';
import PlayBooksListRenderer from './PlayBooksListRenderer';
import { useTheme } from '../context/ThemeContext';
import { MTAPlayBook, Playbook } from '@/types';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import MTAPlayBookCard from './MTAPlayBookCard';


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

export const PlaybooksContainer = () => {

    const [searchQuery, setSearchQuery] = useState('');
    const [selectedType, setSelectedType] = useState<PlaybookType>('All Types');
    const [selectedSeverity, setSelectedSeverity] = useState<PlaybookSeverity>('All Severities');
    const { isDarkMode } = useTheme();

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

    const handlePlaybookSelect = () => {
        // sendMessage(`Selected playbook: ${playbook.name}`, null);
    };

    const handleGraphSearch = () => {
        // sendMessage(`Searching graph for: ${query}`, null);
    };


    const DummyMTAPlaybooks: (MTAPlayBook & { id: string })[] = [
        {
            id: "1",
            sample_url: "https://www.google.com",
            malware_name: "Malware 1",
            hunt_goal: "Hunt goal 1",
            generated_prompt: "Generated prompt 1"
        },
        {
            id: "2",
            sample_url: "https://www.google.com",
            malware_name: "Malware 2",
            hunt_goal: "Hunt goal 2",
            generated_prompt: "Generated prompt 2"
        },
        {
            id: "3",
            sample_url: "https://www.google.com",
            malware_name: "Malware 3",
            hunt_goal: "Hunt goal 3",
            generated_prompt: "Generated prompt 3"
        }
    ];


    return (
        <div className={`w-1/3 border-r transition-colors duration-200 ${isDarkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'}`}>
            <div className="h-full overflow-y-auto">
                <div className={`p-4 h-full flex flex-col`}>
                    {/* Search and Filters - Fixed at top */}
                    <div className="mb-4">
                        <div className="relative mb-4">
                            <Input
                                type="text"
                                placeholder="Search playbooks..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                startContent={<MagnifyingGlassIcon className={`relative left-0 top-0  w-5 h-5`} />}
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
                                    variant={selectedType === type ? 'solid' : 'flat'}
                                    color={selectedType === type ? 'primary' : 'default'}
                                    onPress={() => setSelectedType(type)}
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
                                    variant={selectedSeverity === severity ? 'solid' : 'flat'}
                                    color={selectedSeverity === severity ? 'primary' : 'default'}
                                    onPress={() => setSelectedSeverity(severity)}
                                >
                                    {severity}
                                </Button>
                            ))}
                        </div>
                    </div>

                    {/* Scrollable Cards Section */}
                    <PlayBooksListRenderer
                        renderItems={DummyMTAPlaybooks}
                        ComponentType={({ item }) => <MTAPlayBookCard playbook={item} onSelectPlaybook={handlePlaybookSelect} handleSearchGraph={handleGraphSearch} />}
                    />

                </div >
            </div>
        </div>
    );
}; 