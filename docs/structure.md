# Project Structure

Complete guide to the Unified Business Agent's file organization and architecture.

## Directory Tree

```
project-root/
├── docs/                                    # Documentation
│   ├── plan.md                              # 25-day development plan
│   ├── structure.md                         # This file - project structure
│   ├── agents.md                            # Agent architecture details
│   ├── todo.md                              # Implementation roadmap
│   ├── api-integration.md                   # External API setup guide
│   ├── deployment.md                        # Deployment instructions
│   └── testing.md                           # Testing strategy
│
├── src/                                     # Source code
│   ├── __init__.py                          # Package initialization
│   ├── __main__.py                          # FastAPI server & entry point
│   ├── agent.py                             # LangChain agent setup
│   ├── models.py                            # Pydantic models for A2A
│   ├── tools.py                             # LangChain tool definitions
│   │
│   ├── core/                                # Core architecture components
│   │   ├── __init__.py                      # Core package init
│   │   ├── base_module.py                   # Abstract base class for modules
│   │   ├── planner.py                       # Task decomposition with LLM
│   │   ├── router.py                        # Task-to-module routing
│   │   ├── executor.py                      # Sequential task execution
│   │   └── aggregator.py                    # Result synthesis with LLM
│   │
│   ├── modules/                             # Specialized domain modules
│   │   ├── __init__.py                      # Modules package init
│   │   ├── customer_service.py              # Support ticket management
│   │   ├── data_analytics.py                # Data processing & analysis
│   │   ├── finance.py                       # Expense & invoice tracking
│   │   ├── scheduling.py                    # Calendar & meeting management
│   │   └── document_processor.py            # OCR & document extraction
│   │
│   └── utils/                               # Utility functions & integrations
│       ├── __init__.py                      # Utils package init
│       ├── database.py                      # Database abstraction layer
│       ├── mongodb_database.py              # MongoDB implementation
│       ├── google_calendar.py               # Google Calendar API wrapper
│       ├── gmail.py                         # Gmail API wrapper
│       └── document_ai.py                   # Document AI/OCR integration
│
├── tests/                                   # Test suite
│   ├── __init__.py                          # Tests package init
│   ├── test_modules.py                      # Module unit tests
│   ├── test_tools.py                        # Tool unit tests
│   ├── test_integration.py                  # Integration tests
│   └── fixtures/                            # Test data and fixtures
│       ├── sample_invoice.pdf
│       ├── sample_dataset.csv
│       └── test_credentials.json
│
├── credentials/                             # API credentials (not in git)
│   ├── google_credentials.json              # Google OAuth credentials
│   └── .gitkeep                             # Keep directory in git
│
├── .env.example                             # Environment variables template
├── .gitignore                               # Git ignore rules
├── AgentCard.json                           # A2A protocol metadata
├── curlPOST.json                            # Sample API request
├── docker-compose.yml                       # Docker Compose config
├── Dockerfile                               # Docker container definition
├── pyproject.toml                           # Python dependencies
├── README.md                                # Project overview
└── LICENSE                                  # MIT License

```

## File Responsibilities

### Entry Point & Server

#### `src/__main__.py` (~200 lines)
**Purpose**: FastAPI server and JSON-RPC request handler

**Responsibilities**:
- Initialize FastAPI application
- Handle A2A JSON-RPC requests
- Manage session state
- Format responses in A2A protocol
- Health check endpoint
- CORS middleware configuration
- Lifecycle management (startup/shutdown)

**Key Components**:
```python
app = FastAPI()  # FastAPI application
agent = None     # Global agent instance

@app.post("/")   # Main JSON-RPC endpoint
@app.get("/health")  # Health check
```

**Dependencies**:
- FastAPI, Uvicorn
- Pydantic for request/response validation
- agent.py for agent initialization

---

### Agent Layer

#### `src/agent.py` (~250 lines)
**Purpose**: LangChain agent setup and configuration

**Responsibilities**:
- Initialize ChatGroq LLM instances
- Register all tools from tools.py
- Configure agent executor
- Set up conversation memory
- Define system prompt
- Handle message processing
- Error handling and logging

**Key Components**:
```python
class UnifiedBusinessAgent:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile")
        self.tools = get_all_tools()
        self.agent_executor = create_react_agent(...)
    
    def process_message(self, message: str) -> str:
        # Process user message and return response
```

**Dependencies**:
- LangChain, ChatGroq
- tools.py for tool registry
- Conversation memory

---

#### `src/models.py` (~100 lines)
**Purpose**: Pydantic models for A2A protocol compliance

**Responsibilities**:
- Define request/response schemas
- Validate JSON-RPC messages
- Type safety for API contracts
- Serialization/deserialization

**Key Models**:
```python
class MessagePart(BaseModel)
class Message(BaseModel)
class MessageParams(BaseModel)
class JSONRPCRequest(BaseModel)
class Artifact(BaseModel)
class TaskStatus(BaseModel)
class JSONRPCResponse(BaseModel)
```

---

#### `src/tools.py` (~600 lines)
**Purpose**: LangChain tool definitions for all capabilities

**Responsibilities**:
- Define all 15+ tools with @tool decorator
- Bridge LangChain agent to modular pipeline
- Handle simple operations directly
- Delegate complex operations to pipeline
- Input validation and error handling

**Tool Categories**:
1. **Database Tools** (5):
   - `add_to_database`: Generic data insertion
   - `get_from_database`: Retrieve by ID
   - `search_database`: Query with filters
   - `update_database`: Modify records
   - `delete_from_database`: Remove records

2. **Customer Service Tools** (3):
   - `create_support_ticket`: Create new ticket
   - `get_ticket_status`: Check ticket info
   - `update_ticket`: Modify ticket status
   
3. **Data Analytics Tools** (4):
   - `load_dataset`: Import data files
   - `analyze_dataset`: Perform analysis
   - `generate_report`: Create reports
   - `query_data`: Custom queries

4. **Finance Tools** (3):
   - `add_expense`: Track expenses
   - `process_invoice`: OCR + expense creation
   - `get_financial_summary`: Generate reports

5. **Scheduling Tools** (2):
   - `schedule_meeting`: Create calendar events
   - `find_available_slots`: Search free times

6. **Multi-Step Tool** (1):
   - `business_assistant`: Complex workflows via pipeline

**Global Components**:
```python
_planner = None
_executor = None
_aggregator = None

def set_modular_components(planner, executor, aggregator):
    # Inject pipeline components
```

---

### Core Architecture

#### `src/core/base_module.py` (~30 lines)
**Purpose**: Abstract base class for all modules

**Responsibilities**:
- Define standard module interface
- Enforce implementation of required methods
- Enable plug-and-play architecture

**Interface**:
```python
class BaseModule(ABC):
    @abstractmethod
    async def can_handle(self, task: dict) -> bool:
        """Check if module can handle task"""
    
    @abstractmethod
    async def execute(self, task: dict) -> str:
        """Execute the task and return result"""
    
    @abstractmethod
    def get_capabilities(self) -> dict:
        """Return module capabilities"""
```

---

#### `src/core/planner.py` (~80 lines)
**Purpose**: Break down complex queries into structured tasks

**Responsibilities**:
- Use Groq llama-3.1-70b for planning
- Convert natural language to task JSON
- Determine task sequence and dependencies
- Handle JSON parsing errors gracefully

**Key Method**:
```python
async def plan(self, query: str, context: dict = None) -> list:
    # Returns: [
    #   {
    #     "type": "create_ticket",
    #     "description": "Create support ticket",
    #     "priority": "high",
    #     "params": {...}
    #   },
    #   ...
    # ]
```

**Temperature**: 0.0 (deterministic planning)

---

#### `src/core/router.py` (~60 lines)
**Purpose**: Route tasks to appropriate modules

**Responsibilities**:
- Maintain task-type to module mapping
- Query modules if mapping fails
- Return None if no module can handle
- Log routing decisions

**Routing Map**:
```python
{
    "create_ticket": CustomerServiceModule,
    "analyze_data": DataAnalyticsModule,
    "process_invoice": FinanceModule,
    "schedule_meeting": SchedulingModule,
    "extract_document": DocumentProcessorModule,
    ...
}
```

**Key Method**:
```python
async def route(self, task: dict) -> BaseModule | None:
    # Returns appropriate module instance
```

---

#### `src/core/executor.py` (~70 lines)
**Purpose**: Execute tasks sequentially

**Responsibilities**:
- Run tasks in order
- Route each task via TaskRouter
- Collect results
- Handle errors gracefully
- Log execution progress

**Key Method**:
```python
async def execute(self, tasks: list) -> list:
    # Returns: ["result1", "result2", ...]
```

---

#### `src/core/aggregator.py` (~80 lines)
**Purpose**: Synthesize multiple results into coherent response

**Responsibilities**:
- Use Groq llama-3.1-70b for synthesis
- Create natural, conversational responses
- Highlight key information
- Suggest next steps
- Professional business tone

**Key Method**:
```python
async def aggregate(self, results: list, original_query: str) -> str:
    # Returns natural language summary
```

**Temperature**: 0.3 (natural but consistent)

---

### Specialized Modules

#### `src/modules/customer_service.py` (~300 lines)
**Purpose**: Customer service and support ticket management

**Capabilities**:
- Create, read, update, close tickets
- Sentiment analysis
- FAQ lookup
- Ticket categorization
- Email notifications

**Key Methods**:
```python
async def create_ticket(customer_email, subject, description, priority)
async def get_ticket(ticket_id)
async def update_ticket(ticket_id, status, notes)
async def close_ticket(ticket_id, resolution)
async def analyze_sentiment(text)
async def search_faq(query)
```

**Database Collections**: `tickets`

---

#### `src/modules/data_analytics.py` (~350 lines)
**Purpose**: Data processing, analysis, and reporting

**Capabilities**:
- Load CSV, Excel, JSON files
- Data cleaning and transformation
- Statistical analysis
- Pattern detection
- Report generation
- Visualization (text-based)

**Key Methods**:
```python
async def load_dataset(file_path, format)
async def analyze_dataset(dataset_id, analysis_type)
async def generate_report(dataset_id, report_type)
async def query_data(dataset_id, query)
async def detect_patterns(dataset_id)
```

**Database Collections**: `datasets`

---

#### `src/modules/finance.py` (~320 lines)
**Purpose**: Financial tracking and invoice processing

**Capabilities**:
- Expense tracking
- Invoice OCR and processing
- Receipt management
- Budget tracking
- Financial reporting
- Categorization

**Key Methods**:
```python
async def add_expense(amount, category, description, date)
async def process_invoice(file_path, vendor)
async def get_expenses(start_date, end_date, filters)
async def generate_financial_report(period, report_type)
async def check_budget(category, amount)
```

**Database Collections**: `expenses`

---

#### `src/modules/scheduling.py` (~200 lines)
**Purpose**: Calendar and meeting management

**Capabilities**:
- Schedule meetings via Google Calendar
- Find available time slots
- Send email invitations
- Cancel/reschedule events
- Timezone handling

**Key Methods**:
```python
async def schedule_meeting(title, attendees, date_time, duration)
async def find_available_slots(attendees, duration, date_range)
async def create_event(title, date_time, duration, description)
async def cancel_event(event_id)
```

**Database Collections**: `events`
**External APIs**: Google Calendar, Gmail

---

#### `src/modules/document_processor.py` (~250 lines)
**Purpose**: Document OCR and text extraction

**Capabilities**:
- Extract text from PDFs and images
- Process invoices with structure
- Process receipts
- Validate extracted data
- Batch processing

**Key Methods**:
```python
async def extract_text(file_path)
async def process_invoice(file_path)
async def process_receipt(file_path)
async def validate_document(file_path, doc_type)
```

**Database Collections**: `documents`
**External APIs**: Document AI / Tesseract OCR

---

### Utilities Layer

#### `src/utils/database.py` (~150 lines)
**Purpose**: Database abstraction layer with fallback

**Responsibilities**:
- Determine database backend (MongoDB or file-based)
- Provide unified interface
- Handle database unavailability
- Singleton pattern for connection

**Key Methods**:
```python
def get_database() -> Database:
    # Returns MongoDB or FileDatabase instance

class Database(ABC):
    @abstractmethod
    async def insert(collection, document)
    @abstractmethod
    async def find_one(collection, query)
    @abstractmethod
    async def find(collection, query)
    @abstractmethod
    async def update(collection, query, update)
    @abstractmethod
    async def delete(collection, query)
```

---

#### `src/utils/mongodb_database.py` (~400 lines)
**Purpose**: MongoDB implementation with full feature set

**Responsibilities**:
- MongoDB connection management
- All CRUD operations
- Indexes for performance
- Aggregation pipelines
- Error handling and retry logic

**Collections**:
- `tickets`: Support tickets
- `datasets`: Uploaded datasets
- `expenses`: Financial records
- `events`: Calendar events
- `documents`: Processed documents
- `system`: Configuration and metadata

**Key Features**:
```python
# Indexes for performance
tickets.create_index([("ticket_id", 1)])
tickets.create_index([("customer_email", 1)])
tickets.create_index([("status", 1)])

# Aggregation pipelines for analytics
db.tickets.aggregate([
    {"$match": {"status": "open"}},
    {"$group": {"_id": "$priority", "count": {"$sum": 1}}}
])
```

---

#### `src/utils/google_calendar.py` (~250 lines)
**Purpose**: Google Calendar API integration

**Responsibilities**:
- OAuth authentication
- Event creation with Google Meet links
- Find available time slots
- Event retrieval and cancellation
- Mock implementation for development

**Key Methods**:
```python
async def create_event(title, start_time, end_time, attendees)
async def find_available_slots(duration, date_range)
async def get_events(start_date, end_date)
async def cancel_event(event_id)
```

**Mock Mode**: Returns simulated events when credentials not available

---

#### `src/utils/gmail.py` (~200 lines)
**Purpose**: Gmail API integration for email notifications

**Responsibilities**:
- OAuth authentication
- Send emails (invitations, notifications)
- Format professional emails
- Mock implementation for development

**Key Methods**:
```python
async def send_email(to, subject, body, html=False)
async def send_calendar_invitation(event_details, attendees)
async def send_ticket_notification(ticket_info, recipient)
```

**Mock Mode**: Prints email to console when credentials not available

---

#### `src/utils/document_ai.py` (~220 lines)
**Purpose**: Document OCR and text extraction

**Responsibilities**:
- PDF text extraction
- Image OCR (Tesseract or cloud API)
- Invoice parsing with structure
- Receipt parsing
- Confidence scoring

**Key Methods**:
```python
async def extract_text_from_pdf(file_path)
async def extract_text_from_image(file_path)
async def parse_invoice(text)
async def parse_receipt(text)
```

**Supported Services**:
- Google Document AI
- Tesseract OCR (local)
- OCR.space API
- Fallback: regex-based extraction

---

### Configuration Files

#### `.env.example`
Template for environment variables with documentation

#### `.gitignore`
Excludes: `__pycache__/`, `*.pyc`, `.env`, `credentials/`, `data/`, logs

#### `AgentCard.json`
A2A protocol metadata with skills, capabilities, and examples

#### `curlPOST.json`
Sample JSON-RPC requests for testing

#### `Dockerfile`
Python 3.11 slim image with all dependencies

#### `docker-compose.yml`
Service orchestration with volume mounts and environment

#### `pyproject.toml`
Python dependencies and project metadata

---

## Code Organization Principles

### 1. Separation of Concerns
- **API Layer** (`__main__.py`): HTTP handling only
- **Agent Layer** (`agent.py`): LLM interaction only
- **Tools Layer** (`tools.py`): Interface between agent and logic
- **Core Layer** (`core/`): Task orchestration
- **Module Layer** (`modules/`): Domain-specific logic
- **Utils Layer** (`utils/`): Shared services

### 2. Dependency Injection
- Modules receive database instance in constructor
- Tools receive modular components via setter
- Utilities are singletons or factory functions

### 3. Abstract Interfaces
- `BaseModule` defines module contract
- `Database` defines storage contract
- Enables easy testing with mocks

### 4. Configuration Management
- All configuration via environment variables
- No hardcoded credentials
- Graceful degradation when services unavailable

### 5. Error Handling
- Try-catch at every external interaction
- Logging at all key operations
- User-friendly error messages
- Graceful fallbacks (mock services, file database)

### 6. Type Safety
- Type hints throughout
- Pydantic models for validation
- IDE autocomplete support

---

## Import Structure

### Typical Import Pattern

```python
# Standard library
import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

# Third-party packages
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.agents import create_react_agent

# Local imports
from src.core.base_module import BaseModule
from src.utils.database import get_database
from src.utils.mongodb_database import MongoDBDatabase
```

### Import Order
1. Standard library
2. Third-party packages
3. Local application imports

### Circular Import Avoidance
- `tools.py` uses global references for modular components
- Modules only import utilities, not each other
- Core components don't import modules directly

---

## Testing Structure

### Unit Tests
- One test file per module: `test_<module_name>.py`
- Test each method independently
- Use mocks for external dependencies

### Integration Tests
- Test cross-module workflows
- Test database operations
- Test API integrations with mocks

### Fixtures
- Sample datasets, invoices, receipts
- Mock credentials
- Test database snapshots

---

## Naming Conventions

### Files
- Lowercase with underscores: `customer_service.py`
- Tests prefix with `test_`: `test_customer_service.py`

### Classes
- PascalCase: `CustomerServiceModule`, `BaseModule`
- Modules end with `Module`: `FinanceModule`

### Functions/Methods
- snake_case: `create_ticket`, `process_invoice`
- Async functions prefix with `async def`

### Constants
- UPPERCASE: `MAX_FILE_SIZE`, `DEFAULT_PRIORITY`

### Private Members
- Prefix with underscore: `_internal_method`
- Global state: `_planner`, `_executor`

---

This structure provides a clear, maintainable, and scalable foundation for the Unified Business Agent.
