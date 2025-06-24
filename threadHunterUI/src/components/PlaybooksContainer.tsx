import React, { useState, useMemo } from 'react';
import { Button, Input, Select, SelectItem } from '@heroui/react';
import PlayBooksListRenderer from './PlayBooksListRenderer';
import { useTheme } from '../context/ThemeContext';
import { MTAPlayBook, Playbook } from '@/types';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import MTAPlayBookCard from './MTAPlayBookCard';
import { api } from '@/services/api';


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


const DummyMTAPlaybooks: (MTAPlayBook)[] = [
    {
        sample_url: "https://www.google.com",
        malware_name: "Malware 1",
        hunt_goal: "Hunt goal 1",
        generated_prompt: "Generated prompt 1"
    },
    {
        sample_url: "https://www.google.com",
        malware_name: "Malware 2",
        hunt_goal: "Hunt goal 2",
        generated_prompt: "Generated prompt 2"
    },
    {
        sample_url: "https://www.google.com",
        malware_name: "Malware 3",
        hunt_goal: "Hunt goal 3",
        generated_prompt: "Generated prompt 3"
    }
];


export const PlaybooksContainer = () => {

    const [searchQuery, setSearchQuery] = useState('');
    const [selectedType, setSelectedType] = useState<PlaybookType>('All Types');
    const [selectedSeverity, setSelectedSeverity] = useState<PlaybookSeverity>('All Severities');
    const { isDarkMode } = useTheme();
    const [MTAStats, setMTAStats] = useState<{ year: number, max_samples: number }>({ year: 2013, max_samples: 2 });
    const [playbooks, setPlaybooks] = useState<MTAPlayBook[]>([
        {
            "sample_url": "https://www.malware-traffic-analysis.net/2013/12/27/index.html",
            "malware_name": "Simda",
            "hunt_goal": "Detect download and command-and-control (C2) communication patterns associated with Simda malware delivered via the Styx exploit kit.",
            "generated_prompt": "1. Are there flows with high Down/Up Ratio values, indicating significant download activity consistent with malware payload retrieval?\n2. Do any flows to destination port 80 exhibit elevated Flow Bytes/s and Flow Packets/s, suggesting malicious file transfers?\n3. Are there multiple short-duration flows (low Flow Duration) from the same source IP to new destination IPs, indicative of C2 beaconing?\n4. Do flows show SYN and ACK flag counts consistent with successful TCP handshakes followed by abrupt RST flag terminations, signaling exploit-driven connections?\n5. Are there deviations in Fwd Packet Length Mean and Bwd Packet Length Mean between initial exploit traffic and subsequent C2 communication?\n6. Do flows from internal IPs to external IPs on port 80 with high Total Backward Packets suggest repeated server responses during payload staging?\n7. Are there clusters of flows with similar Active Mean and Idle Mean values, indicating periodic communication patterns to C2 infrastructure?"
        },
        {
            "sample_url": "https://www.malware-traffic-analysis.net/2013/12/26/index.html",
            "malware_name": "Goon Exploit Kit, Urausy",
            "hunt_goal": "Detect Goon EK exploit delivery and Urausy ransomware callback activity using flow metadata.",
            "generated_prompt": "1. Are there flows with high SYN Flag Count and low Flow Duration, indicating rapid connection attempts to potential exploit servers?\n2. Identify flows where Down/Up Ratio exceeds 10:1, suggesting large malicious payload downloads (e.g., Z.jar) from external IPs.\n3. Find bidirectional flows with Protocol 6 (TCP) where Fwd Packet Length Mean differs significantly from Bwd Packet Length Mean, indicating asymmetric C2 communication patterns.\n4. Detect flows to multiple destination IPs from the same source port within 60 seconds, matching exploit kit multi-stage delivery patterns.\n5. Identify flows with elevated RST Flag Count and ACK Flag Count combinations, potentially showing failed C2 connection attempts post-exploitation.\n6. Are there clusters of flows with similar Flow Bytes/s and Flow Packets/s values to 85.17.95.243, indicating Urausy callback traffic patterns?\n7. Find short-lived flows (Active Mean < 1s) with Total Fwd Packets > 50, matching Java exploit delivery characteristics observed in Goon EK."
        }
    ]);
    const [loading, setLoading] = useState(false);
    // const filteredPlaybooks = useMemo(() => {
    //     return playbooks.filter(playbook => {
    //         const searchTerms = searchQuery.toLowerCase().split(' ');
    //         const matchesSearch = searchTerms.every(term =>
    //             playbook.name.toLowerCase().includes(term) ||
    //             playbook.description.toLowerCase().includes(term) ||
    //             playbook.indicators.some(indicator => indicator.toLowerCase().includes(term))
    //         );

    //         const matchesType = selectedType === 'All Types' ||
    //             (selectedType === 'Malware' && playbook.type === 'malware') ||
    //             (selectedType === 'Exploits' && playbook.type === 'exploit');

    //         const matchesSeverity = selectedSeverity === 'All Severities' ||
    //             playbook.severity === selectedSeverity.toLowerCase();

    //         return matchesSearch && matchesType && matchesSeverity;
    //     });
    // }, [searchQuery, selectedType, selectedSeverity]);

    const handlePlaybookSelect = () => {
        // sendMessage(`Selected playbook: ${playbook.name}`, null);
    };

    const handleGraphSearch = () => {
        // sendMessage(`Searching graph for: ${query}`, null);
    };




    const Years = [
        { key: "2013", label: "2013" },
        { key: "2014", label: "2014" },
        { key: "2015", label: "2015" },
        { key: "2016", label: "2016" },
        { key: "2017", label: "2017" },
        { key: "2018", label: "2018" },
        { key: "2019", label: "2019" },
        { key: "2020", label: "2020" },
        { key: "2021", label: "2021" },
        { key: "2022", label: "2022" },
        { key: "2023", label: "2023" },
        { key: "2024", label: "2024" },
        { key: "2025", label: "2025" }
    ];

    const maxSamples = [
        { key: "1", label: "1" },
        { key: "2", label: "2" },
        { key: "3", label: "3" },
        { key: "4", label: "4" },
        { key: "5", label: "5" },
    ]

    const handleGetAllPlaybooks = async () => {
        setLoading(true);
        try {
            const playbooks = await api.playbooks.getAll(MTAStats.year.toString(), MTAStats.max_samples);
            console.log("playbooks", playbooks);
            setPlaybooks(playbooks);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }



    return (
        <div className={`w-1/3 border-r transition-colors duration-200 ${isDarkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'}`}>
            <div className="h-full overflow-y-auto">
                <div className={`p-4 h-full flex flex-col`}>
                    <div className='flex gap-2 mb-4'>
                        <Select
                            id='mta-year'
                            size='sm'
                            variant='underlined'
                            label="MTA Year"
                            placeholder="Select MTA Year..."
                            items={Years}
                            selectedKeys={[MTAStats.year.toString()]}
                            onSelectionChange={(keys) => {
                                const selected = Array.from(keys)[0];
                                setMTAStats({ ...MTAStats, year: parseInt(selected.toString()) })
                            }}
                        >
                            {Years.map((year) => (
                                <SelectItem key={year.key}>{year.label}</SelectItem>
                            ))}
                        </Select>
                        <Select
                            variant='underlined'
                            id='mta-max-samples'
                            size='sm'
                            label="MTA number of blogs"
                            placeholder="Select MTA number of blogs..."
                            items={maxSamples}
                            selectedKeys={[MTAStats.max_samples.toString()]}
                            onSelectionChange={(keys) => {
                                const selected = Array.from(keys)[0];
                                setMTAStats({ ...MTAStats, max_samples: parseInt(selected.toString()) })
                            }}
                        >
                            {(maxSample) => <SelectItem key={maxSample.key}>{maxSample.label}</SelectItem>}
                        </Select>
                        <Button
                            size='lg'
                            variant='flat'
                            onPress={handleGetAllPlaybooks}
                            isLoading={loading}
                        >
                            <MagnifyingGlassIcon className='w-5 h-5' />
                        </Button>
                    </div>



                    {/* Search and Filters - Fixed at top
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

                        Type Filters
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

                        Severity Filters
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
                    </div> */}

                    {/* Scrollable Cards Section */}
                    <PlayBooksListRenderer
                        renderItems={playbooks}
                        ComponentType={({ item }) => <MTAPlayBookCard playbook={item} onSelectPlaybook={handlePlaybookSelect} handleSearchGraph={handleGraphSearch} />}
                    />
                    {/* image of playbooks */}
                    {playbooks.length === 0 && (
                        <div className="flex justify-center items-center h-full">
                            <svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
                                <circle cx="100" cy="100" r="90" fill="none" stroke="currentColor" strokeWidth="10" />
                                <path d="M100 10 L100 90" stroke="currentColor" strokeWidth="10" />
                                <path d="M100 10 L100 90" stroke="currentColor" strokeWidth="10" />
                                <path d="M100 10 L100 90" stroke="currentColor" strokeWidth="10" />
                            </svg>
                        </div>
                    )}

                    {playbooks.length === 0 && (
                        <div className="flex justify-center items-center h-full">
                            <p className="text-gray-500">No playbooks found for the selected year and number of blogs</p>
                        </div>
                    )}
                </div >
            </div>
        </div>
    );
}; 