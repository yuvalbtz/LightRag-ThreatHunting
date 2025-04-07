# custom_kg = {

# "chunks": [

# {

# "content": "Alice and Bob are collaborating on quantum computing research.",

# "source_id": "doc-1"

# }

# ],

# "entities": [

# {

# "entity_name": "Alice",

# "entity_type": "person",

# "description": "Alice is a researcher specializing in quantum physics.",

# "source_id": "doc-1"

# },

# {

# "entity_name": "Bob",

# "entity_type": "person",

# "description": "Bob is a mathematician.",

# "source_id": "doc-1"

# },

# {

# "entity_name": "Quantum Computing",

# "entity_type": "technology",

# "description": "Quantum computing utilizes quantum mechanical phenomena for computation.",

# "source_id": "doc-1"

# }

# ],

# "relationships": [

# {

# "src_id": "Alice",

# "tgt_id": "Bob",

# "description": "Alice and Bob are research partners.",

# "keywords": "collaboration research",

# "weight": 1.0,

# "source_id": "doc-1"

# },

# {

# "src_id": "Alice",

# "tgt_id": "Quantum Computing",

# "description": "Alice conducts research on quantum computing.",

# "keywords": "research expertise",

# "weight": 1.0,

# "source_id": "doc-1"

# },

# {

# "src_id": "Bob",

# "tgt_id": "Quantum Computing",

# "description": "Bob researches quantum computing.",

# "keywords": "research application",

# "weight": 1.0,

# "source_id": "doc-1"

# }

# ]

# }

# custom_kg = {

# "entities": [

# {

# "entity_name": "131.202.240.150",

# "entity_type": "IP",

# "description": "Source IP",

# "source_id": "flow-1"

# },

# {

# "entity_name": "23.45.42.52",

# "entity_type": "IP",

# "description": "Destination IP",

# "source_id": "flow-1"

# },

# {

# "entity_name": "50459",

# "entity_type": "Port",

# "description": "Source Port",

# "source_id": "flow-1"

# },

# {

# "entity_name": "80",

# "entity_type": "Port",

# "description": "Destination Port (HTTP)",

# "source_id": "flow-1"

# },

# {

# "entity_name": "Protocol 6",

# "entity_type": "Protocol",

# "description": "TCP",

# "source_id": "flow-1"

# },

# {

# "entity_name": "Flow 131.202.240.150-23.45.42.52",

# "entity_type": "Flow",

# "description": "Network flow from Source to Destination",

# "source_id": "flow-1"

# },

# {

# "entity_name": "131.202.240.150-184.73.220.127-48078-80-6",

# "entity_type": "FlowId",

# "description": "Flow ID",

# "source_id": "flow-1"

# }

# ],

# "relationships": [

# {

# "src_id": "131.202.240.150",

# "tgt_id": "23.45.42.52",

# "description": "Source IP communicating with Destination IP",

# "keywords": "network flow",

# "weight": 1.0,

# "source_id": "flow-1"

# },

# {

# "src_id": "131.202.240.150",

# "tgt_id": "50459",

# "description": "Uses Source Port",

# "keywords": "source port",

# "weight": 1.0,

# "source_id": "flow-1"

# },

# {

# "src_id": "23.45.42.52",

# "tgt_id": "80",

# "description": "Uses Destination Port (HTTP)",

# "keywords": "destination port",

# "weight": 1.0,

# "source_id": "flow-1"

# },

# {

# "src_id": "Flow 131.202.240.150-23.45.42.52",

# "tgt_id": "Protocol 6",

# "description": "Uses TCP protocol",

# "keywords": "protocol",

# "weight": 1.0,

# "source_id": "flow-1"

# },

# {

# "src_id": "131.202.240.150-184.73.220.127-48078-80-6",

# "tgt_id": "131.202.240.150",

# "description": "Flow ID source",

# "keywords": "flow source",

# "weight": 1.0,

# "source_id": "flow-1"

# }

# ],

# "flow_details": {

# "flowId": "131.202.240.150-184.73.220.127-48078-80-6",

# "srcIp": "131.202.240.150",

# "srcPort": "48078",

# "dstIp": "184.73.220.127",

# "dstPort": "80",

# "protocol": "6",

# "timestamp": "31/03/2015 11:07:01 AM",

# "flowDuration": "14582312",

# "totalFwdPkts": "1",

# "totalBwdPkts": "2",

# "totalLenFwdPkts": "0.0",

# "totalLenBwdPkts": "0.0",

# "fwdPktLenMax": "0.0",

# "fwdPktLenMin": "0.0",

# "fwdPktLenMean": "0.0",

# "fwdPktLenStd": "0.0",

# "bwdPktLenMax": "0.0",

# "bwdPktLenMin": "0.0",

# "bwdPktLenMean": "0.0",

# "bwdPktLenStd": "0.0",

# "flowBytsPerSec": "0.0",

# "flowPktsPerSec": "0.2057286937764053",

# "flowIatMean": "7291156.0",

# "flowIatStd": "1.0230770220956875E7",

# "flowIatMax": "1.4525403E7",

# "flowIatMin": "56909.0",

# "fwdIatTot": "0",

# "fwdIatMean": "0",

# "fwdIatStd": "0",

# "fwdIatMax": "0",

# "fwdIatMin": "0",

# "bwdIatTot": "1.4525403E7",

# "bwdIatMean": "1.4525403E7",

# "bwdIatStd": "0.0",

# "bwdIatMax": "1.4525403E7",

# "bwdIatMin": "1.4525403E7",

# "fwdPshFlags": "0",

# "bwdPshFlags": "0",

# "fwdUrgFlags": "0",

# "bwdUrgFlags": "0",

# "fwdHeaderLen": "32",

# "bwdHeaderLen": "64",

# "fwdPktsPerSec": "0.06857623125880176",

# "bwdPktsPerSec": "0.13715246251760352",

# "pktLenMin": "0.0",

# "pktLenMax": "0.0",

# "pktLenMean": "0.0",

# "pktLenStd": "0.0",

# "pktLenVar": "0.0",

# "finFlagCnt": "1",

# "synFlagCnt": "0",

# "rstFlagCnt": "0",

# "pshFlagCnt": "0",

# "ackFlagCnt": "3",

# "urgFlagCnt": "0",

# "cweFlagCount": "0",

# "eceFlagCnt": "0",

# "downUpRatio": "2.0",

# "pktSizeAvg": "0.0",

# "fwdSegSizeAvg": "0.0",

# "bwdSegSizeAvg": "0.0",

# "fwdBytsPerBAvg": "0",

# "fwdPktsPerBAvg": "0",

# "fwdBlkRateAvg": "0",

# "bwdBytsPerBAvg": "0",

# "bwdPktsPerBAvg": "0",

# "bwdBlkRateAvg": "0",

# "subflowFwdPkts": "0",

# "subflowFwdByts": "0",

# "subflowBwdPkts": "0",

# "subflowBwdByts": "0",

# "initFwdWinByts": "438",

# "initBwdWinByts": "136",

# "fwdActDataPkts": "0",

# "fwdSegSizeMin": "32",

# "activeMean": "0",

# "activeStd": "0",

# "activeMax": "0",

# "activeMin": "0",

# "idleMean": "1.4468494E7",

# "idleStd": "0.0",

# "idleMax": "1.4468494E7",

# "idleMin": "1.4468494E7",

# "label": "unknown",

# "flowStart": "1427825221530",

# "firstNPktSize": "198",

# "category": "7",

# "appProtocol": "7",

# "webService": "Unknown"

# }

# }

# custom_kg = {

# "entities": [

# {

# "entity_name": "CompanyA",

# "entity_type": "Organization",

# "description": "A major technology company",

# "source_id": "Source1",

# },

# {

# "entity_name": "ProductX",

# "entity_type": "Product",

# "description": "A popular product developed by CompanyA",

# "source_id": "Source1",

# },

# {

# "entity_name": "PersonA",

# "entity_type": "Person",

# "description": "A renowned researcher in AI",

# "source_id": "Source2",

# },

# {

# "entity_name": "UniversityB",

# "entity_type": "Organization",

# "description": "A leading university specializing in technology and sciences",

# "source_id": "Source2",

# },

# {

# "entity_name": "CityC",

# "entity_type": "Location",

# "description": "A large metropolitan city known for its culture and economy",

# "source_id": "Source3",

# },

# {

# "entity_name": "EventY",

# "entity_type": "Event",

# "description": "An annual technology conference held in CityC",

# "source_id": "Source3",

# },

# ],

# "relationships": [

# {

# "src_id": "CompanyA",

# "tgt_id": "ProductX",

# "description": "CompanyA develops ProductX",

# "keywords": "develop, produce",

# "weight": 1.0,

# "source_id": "Source1",

# },

# {

# "src_id": "PersonA",

# "tgt_id": "UniversityB",

# "description": "PersonA works at UniversityB",

# "keywords": "employment, affiliation",

# "weight": 0.9,

# "source_id": "Source2",

# },

# {

# "src_id": "CityC",

# "tgt_id": "EventY",

# "description": "EventY is hosted in CityC",

# "keywords": "host, location",

# "weight": 0.8,

# "source_id": "Source3",

# },

# ],

# "chunks": [

# {

# "content": "ProductX, developed by CompanyA, has revolutionized the market with its cutting-edge features.",

# "source_id": "Source1",

# "source_chunk_index": 0,

# },

# {

# "content": "One outstanding feature of ProductX is its advanced AI capabilities.",

# "source_id": "Source1",

# "chunk_order_index": 1,

# },

# {

# "content": "PersonA is a prominent researcher at UniversityB, focusing on artificial intelligence and machine learning.",

# "source_id": "Source2",

# "source_chunk_index": 0,

# },

# {

# "content": "EventY, held in CityC, attracts technology enthusiasts and companies from around the globe.",

# "source_id": "Source3",

# "source_chunk_index": 0,

# },

# {

# "content": "None",

# "source_id": "UNKNOWN",

# "source_chunk_index": 0,

# },

# ],

# }

# async def convert_to_custom_kg(flows: List[Dict[str, Any]]) -> Dict[str, Any]:

# custom_kg = {

# "chunks": [],

# "entities": [],

# "relationships": []

# }

# # Process each flow

# for flow in flows:

# flow_id = flow["Flow ID"]

# source_id = flow_id

# # Create a content chunk from the flow data

# content = f"Flow ID: {flow['Flow ID']} from {flow['Src IP']} to {flow['Dst IP']} at {flow['Timestamp']}"

# custom_kg["chunks"].append({

# "content": content,

# "source_id": source_id

# })

# # Create entities for Src and Dst IPs

# for ip, role in [(flow["Src IP"], "Src IP"), (flow["Dst IP"], "Dst IP")]:

# custom_kg["entities"].append({

# "entity_name": ip,

# "entity_type": "IP Address",

# "description": f"{ip} is the {role}.",

# "source_id": source_id

# })

# # Create relationships between Src and Dst

# custom_kg["relationships"].append({

# "src_id": flow["Src IP"],

# "tgt_id": flow["Dst IP"],

# "description": f"Data flow from {flow['Src IP']} to {flow['Dst IP']}.",

# "keywords": "data flow communication",

# "weight": 1.0,

# "source_id": source_id

# })

# return custom_kg
