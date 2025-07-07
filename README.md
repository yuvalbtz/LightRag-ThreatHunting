<center><h2>🚀 LightRAG: Simple and Fast Retrieval-Augmented Generation</h2></center>
<div align="center">
<table border="0" width="100%">
<tr>
<td width="100" align="center">
<img src="./assets/logo.png" width="80" height="80" alt="lightrag">
</td>
<td>
<div>
    <p>
        <a href='https://lightrag.github.io'><img src='https://img.shields.io/badge/Project-Page-Green'></a>
        <a href='https://youtu.be/oageL-1I0GE'><img src='https://badges.aleen42.com/src/youtube.svg'></a>
        <a href='https://arxiv.org/abs/2410.05779'><img src='https://img.shields.io/badge/arXiv-2410.05779-b31b1b'></a>
        <a href='https://learnopencv.com/lightrag'><img src='https://img.shields.io/badge/LearnOpenCV-blue'></a>
    </p>
    <p>
        <img src='https://img.shields.io/github/stars/hkuds/lightrag?color=green&style=social' />
        <img src="https://img.shields.io/badge/python-3.10-blue">
        <a href="https://pypi.org/project/lightrag-hku/"><img src="https://img.shields.io/pypi/v/lightrag-hku.svg"></a>
        <a href="https://pepy.tech/project/lightrag-hku"><img src="https://static.pepy.tech/badge/lightrag-hku/month"></a>
    </p>
    <p>
        <a href='https://discord.gg/yF2MmDJyGJ'><img src='https://discordapp.com/api/guilds/1296348098003734629/widget.png?style=shield'></a>
        <a href='https://github.com/HKUDS/LightRAG/issues/285'><img src='https://img.shields.io/badge/群聊-wechat-green'></a>
    </p>
</div>
</td>
</tr>
</table>

<img src="./README.assets/b2aaf634151b4706892693ffb43d9093.png" width="800" alt="LightRAG Diagram">

</div>

# 🕵️‍♂️ LightRag ThreatHunting

<div align="center">

![ThreatHunting Logo](https://img.shields.io/badge/ThreatHunting-Advanced%20RAG%20System-blue?style=for-the-badge&logo=shield)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-18+-blue?style=for-the-badge&logo=react)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue?style=for-the-badge&logo=docker)

**Advanced Threat Hunting and Malware Analysis Platform powered by LightRAG**

_A comprehensive system for building knowledge graphs from network flows, analyzing threat patterns, and providing intelligent threat hunting capabilities through Retrieval-Augmented Generation (RAG)._

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🏗️ Architecture](#️-architecture)
- [🚀 Features](#-features)
- [📦 Installation](#-installation)
- [🔧 Configuration](#-configuration)
- [💻 Usage](#-usage)
- [🔍 API Reference](#-api-reference)
- [🎨 Frontend Components](#-frontend-components)
- [🔄 Development](#-development)
- [📊 Knowledge Graph Structure](#-knowledge-graph-structure)
- [🔐 Security](#-security)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🎯 Overview

**LightRag ThreatHunting** is an advanced cybersecurity platform that combines the power of **LightRAG** (Retrieval-Augmented Generation) with sophisticated threat hunting capabilities. The system transforms network flow data, malware analysis reports, and security playbooks into intelligent knowledge graphs that enable automated threat detection, analysis, and response.

### 🎯 Key Capabilities

- **📊 Network Flow Analysis**: Convert CSV/PCAP files into rich knowledge graphs
- **🧠 Intelligent Threat Detection**: AI-powered analysis of network patterns and behaviors
- **📚 Playbook Integration**: Automatic extraction and processing of security playbooks
- **🔍 Real-time Querying**: Natural language queries with streaming responses
- **🎨 Interactive Visualization**: Dynamic graph visualization with real-time updates
- **🔄 Hot Reload Development**: Full development environment with live code updates

---

## 🏗️ Architecture

The ThreatHunting platform follows a modern microservices architecture with the following components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   LightRAG      │
│   (React/Vite)  │◄──►│   (FastAPI)     │◄──►│   Engine        │
│                 │    │                 │    │                 │
│ • Graph Viz     │    │ • REST API      │    │ • Knowledge     │
│ • Chat Interface│    │ • Streaming     │    │   Graph         │
│ • File Upload   │    │ • File Processing│   │ • Vector DB     │
│ • Real-time UI  │    │ • Hot Reload    │    │ • LLM Integration│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   Docker Compose│    │   Storage       │
│                 │    │                 │    │                 │
│ • Static Files  │    │ • Container     │    │ • AppDbStore    │
│ • API Routing   │    │   Orchestration │    │ • Custom KG     │
│ • CORS Handling │    │ • Environment   │    │ • RAG Storage   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔧 Technology Stack

| Component            | Technology                   | Purpose                         |
| -------------------- | ---------------------------- | ------------------------------- |
| **Frontend**         | React 18 + TypeScript + Vite | Modern UI with hot reload       |
| **Backend**          | FastAPI + Python 3.10+       | High-performance API            |
| **RAG Engine**       | LightRAG                     | Knowledge graph and retrieval   |
| **LLM**              | Ollama/DeepSeek              | Natural language processing     |
| **Embeddings**       | BGE-M3                       | Vector embeddings               |
| **Storage**          | JSON + NetworkX              | Knowledge graph storage         |
| **Containerization** | Docker + Docker Compose      | Deployment and isolation        |
| **Proxy**            | Nginx                        | Static file serving and routing |

---

## 🚀 Features

### 🔍 **Advanced Threat Analysis**

- **Network Flow Processing**: Convert CSV/PCAP files into structured knowledge graphs
- **Entity Recognition**: Automatic identification of IPs, ports, protocols, and services
- **Behavioral Analysis**: Pattern detection for suspicious activities
- **Threat Intelligence**: Integration with security playbooks and malware reports

### 🧠 **Intelligent RAG System**

- **Multi-Modal Retrieval**: Combines vector search and knowledge graph traversal
- **Context-Aware Queries**: Understands threat hunting context and terminology
- **Streaming Responses**: Real-time AI responses with progressive disclosure
- **Conversation Memory**: Maintains context across multiple queries

### 🎨 **Interactive Visualization**

- **Dynamic Graph Rendering**: Real-time network topology visualization
- **Interactive Nodes**: Click to explore entity details and relationships
- **Search and Filter**: Find specific entities or patterns in the graph
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### 🔄 **Development Experience**

- **Hot Reload**: Instant updates for both frontend and backend changes
- **Docker Integration**: Consistent development environment
- **Environment Management**: Flexible configuration for different deployment scenarios
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

---

## 📦 Installation

### Prerequisites

- **Docker & Docker Compose**: For containerized deployment
- **Python 3.10+**: For local development
- **Node.js 18+**: For frontend development
- **Git**: For version control

### Quick Start

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd LightRag-ThreatHunting
   ```

2. **Development Environment**

   ```bash
   # Start with hot reload (recommended for development)
   ./dev-sudo.sh

   # Or use regular development mode
   ./dev.sh
   ```

3. **Production Environment**
   ```bash
   # Start production environment
   ./prod.sh
   ```

### Environment Configuration

The system supports multiple environment configurations through `.env` files:

#### Development Environment

```bash
# Copy development template
cp env.example .env

# Edit configuration
nano .env
```

#### Production Environment

```bash
# Copy and customize for production
cp env.example .env.prod

# Edit production configuration
nano .env.prod

# Use production environment
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

#### Environment Variables Reference

| Category              | Variable                | Description                       | Default                                   |
| --------------------- | ----------------------- | --------------------------------- | ----------------------------------------- |
| **API Configuration** | `OPENROUTER_API_KEY`    | OpenRouter API key for LLM access | Required                                  |
|                       | `OPENAI_API_KEY`        | OpenAI API key (alternative)      | Optional                                  |
|                       | `ANTHROPIC_API_KEY`     | Anthropic API key (alternative)   | Optional                                  |
| **Database**          | `DATABASE_URL`          | Database connection string        | `sqlite:///./AppDbStore/threathunting.db` |
|                       | `REDIS_URL`             | Redis connection string           | `redis://localhost:6379`                  |
| **Security**          | `SECRET_KEY`            | Application secret key            | Required                                  |
|                       | `JWT_SECRET_KEY`        | JWT signing key                   | Required                                  |
| **Application**       | `DEBUG`                 | Debug mode                        | `true`                                    |
|                       | `LOG_LEVEL`             | Logging level                     | `INFO`                                    |
|                       | `ENVIRONMENT`           | Environment name                  | `development`                             |
| **Frontend**          | `REACT_APP_API_URL`     | Backend API URL                   | `http://localhost:8000`                   |
|                       | `REACT_APP_ENVIRONMENT` | Frontend environment              | `development`                             |
| **Knowledge Graph**   | `KG_STORAGE_PATH`       | KG storage directory              | `./custom_kg`                             |
|                       | `KG_CACHE_ENABLED`      | Enable KG caching                 | `true`                                    |
| **File Upload**       | `MAX_FILE_SIZE`         | Max file size in bytes            | `104857600` (100MB)                       |
|                       | `ALLOWED_FILE_TYPES`    | Allowed file extensions           | `.csv,.json,.txt,.log,.pcap`              |
| **Rate Limiting**     | `RATE_LIMIT_REQUESTS`   | Requests per window               | `100`                                     |
|                       | `RATE_LIMIT_WINDOW`     | Rate limit window in seconds      | `3600`                                    |
| **Monitoring**        | `ENABLE_METRICS`        | Enable metrics collection         | `true`                                    |
|                       | `METRICS_PORT`          | Metrics server port               | `9090`                                    |

#### LLM Configuration

| Variable          | Description                    | Default          |
| ----------------- | ------------------------------ | ---------------- |
| `LLM_BINDING`     | LLM provider (ollama/deepseek) | `ollama`         |
| `LLM_MODEL`       | Model name                     | `mistral:latest` |
| `EMBEDDING_MODEL` | Embedding model                | `bge-m3:latest`  |
| `WORKING_DIR`     | Data storage directory         | `/app`           |

#### Security Best Practices

1. **Never commit `.env` files to version control**

   ```bash
   # .gitignore should include:
   .env
   .env.local
   .env.prod
   ```

2. **Use strong, unique secrets**

   ```bash
   # Generate secure secrets
   openssl rand -hex 32  # For SECRET_KEY
   openssl rand -hex 32  # For JWT_SECRET_KEY
   ```

3. **Environment-specific configurations**

   ```bash
   # Development
   cp env.example .env

   # Production
   cp env.example .env.prod
   # Edit with production values
   ```

4. **Docker Compose with environment files**

   ```bash
   # Development
   docker-compose -f docker-compose.dev.yml --env-file .env up

   # Production
   docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
   ```

---

## 🔧 Configuration

### Backend Configuration

The backend API (`api.py`) provides the following key endpoints:

#### Core Endpoints

- `GET /` - Health check and API information
- `POST /build-kg` - Build knowledge graph from uploaded files
- `GET /graph-data` - Retrieve graph data for visualization
- `POST /query/stream` - Streaming chat interface
- `GET /graph-folders-names` - List available knowledge graphs

#### Playbook Integration

- `POST /generate-playbooks` - Generate enriched security playbooks
- `POST /fetch-playbooks` - Fetch playbooks from external sources
- `POST /extract-playbook` - Extract playbook from URL

### Frontend Configuration

The React frontend (`threadHunterUI/`) includes:

#### Key Components

- **KnowledgeGraphContainer**: Main graph visualization
- **ChatContainer**: AI chat interface
- **FileUpload**: Drag-and-drop file upload
- **GraphControls**: Graph manipulation controls

#### Development Configuration

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    port: 3000,
    host: "0.0.0.0",
    proxy: {
      "/api": {
        target: "http://backend:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
```

---

## 💻 Usage

### 1. **Building Knowledge Graphs**

#### Upload Network Flow Data

1. Navigate to the web interface at `http://localhost:3000`
2. Drag and drop a CSV file containing network flow data
3. The system will automatically:
   - Parse the CSV structure
   - Identify entities (IPs, ports, protocols)
   - Build relationships between entities
   - Create a knowledge graph

#### Supported File Formats

- **CSV**: Network flow data with columns like Source IP, Destination IP, Protocol, etc.
- **PCAP**: Packet capture files (planned feature)

### 2. **Querying the Knowledge Graph**

#### Natural Language Queries

Use the chat interface to ask questions like:

- "What are the most active IP addresses in the network?"
- "Show me all connections to external IPs"
- "Identify potential data exfiltration patterns"
- "What services are running on port 443?"

#### Advanced Queries

- **Entity Analysis**: "Analyze the behavior of IP 192.168.1.100"
- **Pattern Detection**: "Find unusual connection patterns"
- **Threat Assessment**: "Assess the security posture of this network"

### 3. **Visualizing the Network**

#### Interactive Graph Features

- **Zoom and Pan**: Navigate through large networks
- **Node Selection**: Click nodes to see detailed information
- **Edge Inspection**: Hover over connections to see relationship details
- **Search**: Find specific entities by name or IP

#### Graph Controls

- **Layout Algorithms**: Choose between different graph layouts
- **Clustering**: Group related entities together
- **Filtering**: Show/hide specific entity types
- **Export**: Save graph visualizations

### 4. **Security Playbook Integration**

#### Automatic Playbook Processing

The system can:

- Fetch playbooks from security blogs and repositories
- Extract threat indicators and procedures
- Integrate playbook knowledge into the RAG system
- Provide context-aware threat hunting guidance

---

## 🔍 API Reference

### Core API Endpoints

#### Knowledge Graph Management

**POST** `/api/build-kg`
Build a knowledge graph from uploaded file data.

```json
{
  "file": "network_flows.csv",
  "source_column": "Source IP",
  "target_column": "Destination IP",
  "relationship_columns": ["Protocol", "Service"],
  "working_dir": "./custom_kg"
}
```

**GET** `/api/graph-data`
Retrieve graph data for visualization.

```json
{
  "nodes": [
    {
      "id": "192.168.1.100",
      "label": "192.168.1.100",
      "type": "IP Address",
      "properties": {...}
    }
  ],
  "edges": [
    {
      "from": "192.168.1.100",
      "to": "8.8.8.8",
      "label": "DNS Query",
      "properties": {...}
    }
  ]
}
```

#### Chat Interface

**POST** `/api/query/stream`
Streaming chat interface with RAG-powered responses.

```json
{
  "query": "What are the suspicious connections in this network?",
  "dir_path": "./custom_kg",
  "conversation_history": []
}
```

#### Playbook Management

**POST** `/api/generate-playbooks`
Generate enriched security playbooks.

```json
{
  "year": "2023",
  "max_samples": 5
}
```

### Response Formats

#### Streaming Response

```
data: {"token": "Based on the network analysis, "}
data: {"token": "I can identify several suspicious patterns..."}
data: [DONE]
```

#### Error Response

```json
{
  "detail": "Error message",
  "status_code": 500
}
```

---

## 🎨 Frontend Components

### Core Components

#### KnowledgeGraphContainer

Main container for graph visualization and interaction.

**Features:**

- File upload with drag-and-drop
- Graph rendering with vis.js
- Real-time updates
- Interactive controls

#### ChatContainer

AI-powered chat interface for querying the knowledge graph.

**Features:**

- Streaming responses
- Message history
- Context-aware suggestions
- Markdown rendering

#### GraphControls

Controls for manipulating graph visualization.

**Features:**

- Layout selection
- Zoom controls
- Filter options
- Export functionality

### State Management

The frontend uses React Context for state management:

#### ChatContext

Manages chat messages, loading states, and conversation history.

#### GraphContext

Handles graph data, loading states, and graph operations.

#### ThemeContext

Manages dark/light theme preferences.

### Worker Threads

#### GraphWorker

Web Worker for processing graph data and performing heavy computations.

**Capabilities:**

- Graph data processing
- Search operations
- Layout calculations
- Background tasks

---

## 🔄 Development

### Development Environment Setup

#### 1. **Hot Reload Configuration**

The development environment includes comprehensive hot reload:

**Backend Hot Reload:**

```bash
# Manual file watching with automatic server restart
./dev-start.sh
```

**Frontend Hot Reload:**

```bash
# Vite development server with proxy configuration
npm run dev
```

#### 2. **Docker Development**

**Development Compose:**

```yaml
# docker-compose.dev.yml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - ./api.py:/app/api.py
      - ./agent.py:/app/agent.py
      # ... other source files
    environment:
      - PYTHONUNBUFFERED=1
      - WATCHDOG_TIMEOUT=1
```

#### 3. **Environment Variables**

**Development Configuration:**

```bash
# env.dev
LLM_BINDING=ollama
LLM_MODEL=mistral:latest
EMBEDDING_MODEL=bge-m3:latest
LOG_LEVEL=DEBUG
VERBOSE=True
```

### Development Workflow

#### 1. **Making Changes**

```bash
# Start development environment
./dev-sudo.sh

# Make changes to files
# Backend: api.py, agent.py
# Frontend: src/components/*

# Changes are automatically detected and reloaded
```

#### 2. **Testing Changes**

```bash
# Test API endpoints
curl http://localhost:8000/test-hot-reload

# Test frontend
# Open http://localhost:3000 in browser
```

#### 3. **Debugging**

```bash
# View backend logs
docker-compose -f docker-compose.dev.yml logs backend

# View frontend logs
docker-compose -f docker-compose.dev.yml logs frontend
```

### Code Structure

```
LightRag-ThreatHunting/
├── api.py                 # FastAPI backend server
├── agent.py              # RAG agent and LLM integration
├── dev-start.sh          # Development startup script
├── docker-compose.dev.yml # Development Docker configuration
├── Dockerfile.dev        # Development Dockerfile
├── threadHunterUI/       # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── context/      # React context providers
│   │   ├── hooks/        # Custom React hooks
│   │   ├── services/     # API services
│   │   └── workers/      # Web workers
│   ├── vite.config.ts    # Vite configuration
│   └── package.json      # Frontend dependencies
├── AppDbStore/           # Knowledge graph storage
├── custom_kg/            # Custom knowledge graphs
└── examples/             # Example data and scripts
```

---

## 📊 Knowledge Graph Structure

### Entity Types

The system automatically identifies and categorizes entities:

#### Network Entities

- **IP Address**: IPv4/IPv6 addresses (e.g., `192.168.1.100`)
- **Port**: Network ports (e.g., `443`, `8080`)
- **Protocol**: Network protocols (e.g., `TCP`, `UDP`, `HTTP`)
- **Service**: Application services (e.g., `HTTPS`, `SSH`, `DNS`)

#### Behavioral Entities

- **Traffic Class**: Categorized traffic types
- **Network Entity**: Generic network objects
- **Threat Indicator**: Suspicious patterns and behaviors

### Relationship Types

#### Network Relationships

- **Connection**: Direct network connections between entities
- **Service Access**: Service-to-port relationships
- **Protocol Usage**: Entity-to-protocol associations

#### Behavioral Relationships

- **Data Flow**: Information transfer patterns
- **Dependency**: Service dependencies
- **Threat Association**: Links to threat indicators

### Graph Properties

#### Node Properties

```json
{
  "id": "192.168.1.100",
  "label": "192.168.1.100",
  "type": "IP Address",
  "properties": {
    "connection_count": 15,
    "external_connections": 3,
    "suspicious_score": 0.7,
    "last_seen": "2024-01-15T10:30:00Z"
  }
}
```

#### Edge Properties

```json
{
  "from": "192.168.1.100",
  "to": "8.8.8.8",
  "label": "DNS Query",
  "properties": {
    "protocol": "UDP",
    "port": 53,
    "frequency": "high",
    "data_volume": "low"
  }
}
```

---

## 🔐 Security

### Security Features

#### Input Validation

- **File Upload Validation**: Strict validation of uploaded files
- **API Input Sanitization**: All API inputs are validated and sanitized
- **CORS Configuration**: Proper CORS settings for cross-origin requests

#### Authentication & Authorization

- **API Key Support**: Optional API key authentication
- **Rate Limiting**: Built-in rate limiting for API endpoints
- **Request Validation**: Pydantic models for request validation

#### Data Security

- **Secure Storage**: Knowledge graphs stored in isolated containers
- **Temporary File Cleanup**: Automatic cleanup of temporary files
- **Log Sanitization**: Sensitive data removed from logs

### Best Practices

#### Development Security

```bash
# Use environment variables for sensitive data
export OPENROUTER_API_KEY="your-api-key"

# Regular security updates
docker-compose pull
docker-compose build --no-cache
```

#### Production Security

```bash
# Use production Docker configuration
./prod.sh

# Enable SSL/TLS
# Configure firewall rules
# Set up monitoring and alerting
```

---

## 🤝 Contributing

### Development Guidelines

#### Code Style

- **Python**: Follow PEP 8 guidelines
- **TypeScript**: Use strict TypeScript configuration
- **React**: Follow React best practices and hooks

#### Testing

```bash
# Run backend tests
python -m pytest tests/

# Run frontend tests
cd threadHunterUI
npm test
```

#### Documentation

- Update README for new features
- Add API documentation for new endpoints
- Include code comments for complex logic

### Contribution Process

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests and documentation**
5. **Submit a pull request**

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd LightRag-ThreatHunting

# Set up development environment
./dev-sudo.sh

# Make changes and test
# Submit pull request
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Acknowledgments

- **LightRAG Team**: For the powerful RAG framework
- **FastAPI**: For the excellent web framework
- **React Community**: For the frontend ecosystem
- **Docker**: For containerization technology

---

## 📞 Support

### Getting Help

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions for questions and ideas

### Community

- **GitHub**: [Repository](https://github.com/your-repo)
- **Discord**: [Community Server](https://discord.gg/your-server)
- **Email**: [Contact](mailto:your-email@domain.com)

---

<div align="center">

**Built with ❤️ for the cybersecurity community**

_Empowering threat hunters with AI-powered knowledge graphs_

</div>

**Thank you for your interest in our work!**
