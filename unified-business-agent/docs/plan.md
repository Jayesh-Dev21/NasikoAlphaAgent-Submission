# Unified Business Agent - Comprehensive Project Plan

## Executive Summary

The **Unified Business Agent (UBA)** is a sophisticated, multi-domain AI agent designed for the Nasiko Hackathon. It combines customer service, data analytics, and finance/accounting capabilities into a single, intelligent system that can handle complex, multi-step business workflows.

### Key Highlights

- **Multi-Domain**: Seamlessly handles customer service, data analytics, and finance tasks
- **Modular Architecture**: Based on HR-system's proven dual-architecture approach (LangChain + Custom Pipeline)
- **Groq-Powered**: Uses Groq Cloud's fast, free LLMs for optimal performance
- **Production-Ready**: MongoDB backend, external API integrations, comprehensive error handling
- **A2A Compliant**: Fully compatible with Nasiko platform using A2A protocol

---

## Project Goals and Objectives

### Primary Goals

1. **Build a unified agent** that handles three distinct business domains without compromising performance
2. **Demonstrate modular architecture** that can be easily extended with new capabilities
3. **Achieve production quality** with proper error handling, logging, and database management
4. **Optimize for speed and cost** using Groq Cloud's free, high-performance LLMs
5. **Create hackathon-ready submission** with complete documentation and deployment guide

### Success Criteria

- ✅ Agent successfully processes requests in all three domains
- ✅ Complex multi-step workflows execute correctly (e.g., "analyze this invoice and schedule a meeting to discuss")
- ✅ External integrations work (Google Calendar, Gmail, Document AI)
- ✅ Database operations are reliable with proper fallback mechanisms
- ✅ Agent deploys successfully on Nasiko platform
- ✅ Response times are acceptable (<5 seconds for simple queries, <15 seconds for complex workflows)
- ✅ Comprehensive documentation enables easy understanding and extension

---

## Technical Requirements

### Core Technologies

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Runtime** | Python | 3.11+ | Base language |
| **Web Framework** | FastAPI | 0.109.0+ | JSON-RPC API server |
| **AI Framework** | LangChain | 0.2.x | Agent orchestration |
| **LLM Provider** | Groq Cloud | - | Fast, free inference |
| **Primary LLM** | llama-3.3-70b-versatile | - | Main agent reasoning |
| **Secondary LLM** | llama-3.1-70b-versatile | - | Planning & aggregation |
| **Database** | MongoDB | 4.6.0+ | Primary storage |
| **Containerization** | Docker | Latest | Deployment |

### External Service Integrations

1. **Groq Cloud API** - LLM inference (free tier)
2. **Google Calendar API** - Meeting and event scheduling
3. **Gmail API** - Email notifications and communication
4. **Document AI / OCR** - Invoice, receipt, and document processing
5. **Support Ticket System** - Customer service ticket management
6. **MongoDB Atlas** - Cloud database (optional, free tier)

### Development Environment

- **OS**: Linux/macOS/Windows (Docker ensures consistency)
- **Editor**: Any (VS Code recommended)
- **Git**: For version control and GitHub deployment
- **curl/Postman**: For API testing
- **Docker Desktop**: For local testing and deployment

---

## Architecture Overview

### Dual-Architecture Design

The UBA follows the HR-system's proven dual-architecture pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Request (JSON-RPC)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Server (__main__.py)                    │
│  • JSON-RPC request validation                              │
│  • Session management                                        │
│  • Response formatting                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Agent Layer (agent.py)                          │
│  • LangChain AgentExecutor                                  │
│  • Tool selection and invocation                            │
│  • Conversation memory                                       │
│  • Response generation                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
           ┌───────────┴──────────┐
           │                      │
           ▼                      ▼
    ┌─────────────┐      ┌──────────────────┐
    │ Simple Tools│      │ Complex Tools    │
    │ (Direct)    │      │ (via Pipeline)   │
    └─────────────┘      └────────┬─────────┘
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │   Modular Pipeline            │
                  │                               │
                  │  1. Planner                   │
                  │     └─> Task Decomposition    │
                  │                               │
                  │  2. Executor                  │
                  │     └─> Sequential Execution  │
                  │                               │
                  │  3. Router                    │
                  │     └─> Module Selection      │
                  │                               │
                  │  4. Modules                   │
                  │     ├─> CustomerService       │
                  │     ├─> DataAnalytics         │
                  │     ├─> Finance               │
                  │     ├─> Scheduling            │
                  │     └─> DocumentProcessor     │
                  │                               │
                  │  5. Aggregator                │
                  │     └─> Result Synthesis      │
                  └────────────────┬──────────────┘
                                   │
                                   ▼
                  ┌────────────────────────────────┐
                  │    Utilities Layer             │
                  │  • MongoDB Database            │
                  │  • Google Calendar             │
                  │  • Gmail                       │
                  │  • Document AI                 │
                  │  • Ticket System               │
                  └────────────────────────────────┘
```

### Why Dual Architecture?

**LangChain Layer Benefits**:
- Natural language understanding
- Intelligent tool selection
- Conversation memory and context
- Built-in error handling
- Flexible, adaptable responses

**Custom Pipeline Benefits**:
- Complex multi-step workflows
- Deterministic task decomposition
- Module-specific optimizations
- Easier testing and debugging
- Clear separation of concerns

**Together**: The best of both worlds - flexibility AND structure

---

## Module Specifications

### 1. Customer Service Module

**Capabilities**:
- Create, update, retrieve, and close support tickets
- Automated ticket categorization and priority assignment
- Customer inquiry handling with context-aware responses
- FAQ lookup and knowledge base integration
- Customer sentiment analysis
- Email notifications for ticket updates
- Ticket escalation based on urgency

**Key Methods**:
```python
async def create_ticket(customer_email, subject, description, priority) -> str
async def get_ticket(ticket_id) -> dict
async def update_ticket(ticket_id, status, notes) -> str
async def close_ticket(ticket_id, resolution) -> str
async def analyze_sentiment(text) -> dict
async def find_similar_tickets(description) -> list
async def search_faq(query) -> str
```

**Database Schema** (MongoDB):
```json
{
  "ticket_id": "TKT-20260328-001",
  "customer_email": "customer@example.com",
  "customer_name": "John Doe",
  "subject": "Cannot access account",
  "description": "Detailed description...",
  "status": "open|in-progress|resolved|closed",
  "priority": "low|medium|high|urgent",
  "category": "technical|billing|general",
  "created_at": "2026-03-28T10:00:00Z",
  "updated_at": "2026-03-28T11:30:00Z",
  "assigned_to": "agent_name",
  "resolution": "Resolution details...",
  "sentiment": {"score": 0.2, "label": "negative"},
  "tags": ["login", "access"],
  "history": [
    {"timestamp": "...", "action": "created", "by": "system"}
  ]
}
```

---

### 2. Data Analytics Module

**Capabilities**:
- Process CSV, Excel, JSON, PDF documents
- Data cleaning and transformation
- Statistical analysis and pattern recognition
- Generate insights and recommendations
- Create visualizations and charts (as text descriptions or saved files)
- Custom query execution on datasets
- Trend analysis and forecasting
- Data export in multiple formats

**Key Methods**:
```python
async def load_dataset(file_path_or_url, format) -> dict
async def analyze_dataset(dataset_id, analysis_type) -> str
async def generate_report(dataset_id, report_type) -> str
async def query_data(dataset_id, query) -> str
async def detect_patterns(dataset_id) -> dict
async def create_visualization(dataset_id, chart_type) -> str
async def export_data(dataset_id, export_format) -> str
```

**Database Schema**:
```json
{
  "dataset_id": "DS-20260328-001",
  "name": "Q1 Sales Data",
  "source": "uploaded_file|url|api",
  "file_path": "/data/sales_q1.csv",
  "format": "csv|json|xlsx|pdf",
  "uploaded_at": "2026-03-28T10:00:00Z",
  "size_bytes": 1048576,
  "rows": 5000,
  "columns": 15,
  "schema": {
    "date": "datetime",
    "product": "string",
    "revenue": "float",
    ...
  },
  "analyses": [
    {
      "type": "trend_analysis",
      "performed_at": "2026-03-28T10:30:00Z",
      "results": {...}
    }
  ],
  "metadata": {
    "date_range": "2026-01-01 to 2026-03-31",
    "total_revenue": 1250000.50,
    ...
  }
}
```

---

### 3. Finance Module

**Capabilities**:
- Expense tracking and categorization
- Invoice processing with OCR
- Receipt management and digitization
- Financial report generation
- Budget tracking and alerts
- Transaction categorization
- Expense approval workflows
- Financial summaries and dashboards

**Key Methods**:
```python
async def process_invoice(file_path, vendor) -> dict
async def add_expense(amount, category, description, date) -> str
async def get_expenses(start_date, end_date, filters) -> list
async def categorize_expense(description, amount) -> str
async def generate_financial_report(period, report_type) -> str
async def check_budget(category, amount) -> dict
async def process_receipt(image_path) -> dict
```

**Database Schema**:
```json
{
  "expense_id": "EXP-20260328-001",
  "amount": 125.50,
  "currency": "USD",
  "category": "office_supplies|travel|meals|software|...",
  "description": "Office chairs for team",
  "vendor": "Office Depot",
  "date": "2026-03-28",
  "payment_method": "corporate_card|cash|check|...",
  "status": "pending|approved|rejected|paid",
  "receipt_url": "/receipts/exp-001.pdf",
  "invoice_number": "INV-12345",
  "approved_by": "manager@company.com",
  "approved_at": "2026-03-29T09:00:00Z",
  "budget_category": "operations",
  "tax_deductible": true,
  "notes": "Quarterly purchase",
  "extracted_data": {
    "vendor_name": "Office Depot",
    "vendor_address": "...",
    "line_items": [...]
  }
}
```

---

### 4. Scheduling Module

**Capabilities**:
- Schedule meetings and events via Google Calendar
- Find available time slots
- Send calendar invitations via email
- Manage recurring events
- Handle timezone conversions
- Cancel and reschedule events
- Integration with customer service and finance modules

**Key Methods**:
```python
async def schedule_meeting(title, attendees, date_time, duration) -> str
async def find_available_slots(attendees, duration, date_range) -> list
async def create_event(title, date_time, duration, description) -> str
async def cancel_event(event_id) -> str
async def reschedule_event(event_id, new_date_time) -> str
async def get_events(start_date, end_date) -> list
```

**Database Schema**:
```json
{
  "event_id": "EVT-20260328-001",
  "google_event_id": "abc123...",
  "title": "Customer Meeting - Invoice Discussion",
  "description": "Discuss Q1 invoices",
  "start_time": "2026-03-30T14:00:00Z",
  "end_time": "2026-03-30T15:00:00Z",
  "timezone": "America/New_York",
  "attendees": [
    {"email": "customer@example.com", "status": "accepted"}
  ],
  "location": "Google Meet",
  "meet_link": "https://meet.google.com/...",
  "status": "scheduled|completed|cancelled",
  "created_by": "agent",
  "created_at": "2026-03-28T10:00:00Z",
  "reminders": [15, 60],
  "related_to": {
    "type": "ticket|expense|dataset",
    "id": "TKT-20260328-001"
  }
}
```

---

### 5. Document Processor Module

**Capabilities**:
- OCR for images and PDFs
- Extract text from invoices, receipts, forms
- Parse structured documents
- Validate extracted data
- Support multiple document types
- Handle batch processing

**Key Methods**:
```python
async def extract_text(file_path) -> str
async def process_invoice(file_path) -> dict
async def process_receipt(file_path) -> dict
async def validate_document(file_path, doc_type) -> dict
async def batch_process(file_paths, doc_type) -> list
```

**Database Schema**:
```json
{
  "document_id": "DOC-20260328-001",
  "file_path": "/uploads/invoice_001.pdf",
  "file_name": "invoice_001.pdf",
  "file_type": "pdf|jpg|png",
  "document_type": "invoice|receipt|form|report",
  "processed_at": "2026-03-28T10:00:00Z",
  "status": "processed|failed|pending",
  "extracted_text": "Full text content...",
  "structured_data": {
    "vendor": "Acme Corp",
    "invoice_number": "INV-12345",
    "date": "2026-03-25",
    "amount": 1250.00,
    "line_items": [...]
  },
  "confidence_score": 0.95,
  "validation_errors": [],
  "linked_to": {
    "type": "expense",
    "id": "EXP-20260328-001"
  }
}
```

---

## Development Phases

### Phase 1: Foundation (Days 1-2)

**Tasks**:
1. Project scaffolding and directory structure
2. FastAPI server with JSON-RPC handler
3. Pydantic models for A2A protocol
4. Basic agent with Groq integration
5. Health check endpoint
6. Docker configuration
7. Environment variable management

**Deliverables**:
- Working FastAPI server
- Basic agent responding to simple queries
- Docker container builds and runs
- Environment configuration documented

**Testing**:
- Server starts without errors
- Health check returns 200
- Simple "hello" query gets response
- Docker container runs successfully

---

### Phase 2: Core Architecture (Days 3-5)

**Tasks**:
1. Implement BaseModule abstract class
2. Create Planner with Groq llama-3.1-70b
3. Implement TaskRouter
4. Create TaskExecutor
5. Build Aggregator with Groq llama-3.1-70b
6. Connect LangChain agent to modular pipeline
7. Create tools.py with initial tool set

**Deliverables**:
- Complete modular pipeline working
- Planner breaks down complex queries
- Router selects appropriate modules
- Aggregator synthesizes results
- Tools delegate to pipeline

**Testing**:
- Planner outputs valid JSON tasks
- Router correctly maps tasks to modules
- Executor runs tasks sequentially
- Aggregator creates coherent responses
- End-to-end pipeline test passes

---

### Phase 3: Database Layer (Days 6-7)

**Tasks**:
1. MongoDB database abstraction layer
2. File-based fallback database
3. Database schemas for all collections
4. CRUD operations for each domain
5. Indexes for performance
6. Mock data for testing

**Deliverables**:
- MongoDB integration working
- File-based fallback operational
- All schemas implemented
- Database utilities tested

**Testing**:
- Create, read, update, delete operations
- Query performance acceptable
- Fallback mechanism works
- Data validation catches errors

---

### Phase 4: Customer Service Module (Days 8-10)

**Tasks**:
1. Create CustomerServiceModule class
2. Implement ticket management methods
3. Sentiment analysis integration
4. FAQ knowledge base
5. Email notification system
6. Tools for customer service

**Deliverables**:
- Full customer service module
- Ticket CRUD operations working
- Sentiment analysis functional
- Email notifications sent

**Testing**:
- Create and retrieve tickets
- Sentiment analysis accuracy
- Email notifications received
- FAQ lookup works correctly

---

### Phase 5: Data Analytics Module (Days 11-13)

**Tasks**:
1. Create DataAnalyticsModule class
2. CSV/Excel/JSON parsing
3. Data analysis algorithms
4. Report generation
5. Pattern detection
6. Tools for data analytics

**Deliverables**:
- Data analytics module complete
- Multi-format file support
- Analysis and reporting working
- Pattern detection functional

**Testing**:
- Load various file formats
- Analyze sample datasets
- Generate reports
- Detect patterns in test data

---

### Phase 6: Finance Module (Days 14-16)

**Tasks**:
1. Create FinanceModule class
2. Expense tracking implementation
3. Document AI / OCR integration
4. Invoice processing pipeline
5. Financial reporting
6. Tools for finance operations

**Deliverables**:
- Finance module complete
- Expense CRUD operations
- Invoice OCR working
- Financial reports generated

**Testing**:
- Add and retrieve expenses
- Process invoice images
- Generate financial summaries
- Budget tracking works

---

### Phase 7: Scheduling & Document Modules (Days 17-19)

**Tasks**:
1. Create SchedulingModule class
2. Google Calendar API integration
3. Gmail API integration
4. Create DocumentProcessorModule
5. OCR service integration
6. Tools for scheduling and documents

**Deliverables**:
- Scheduling module complete
- Google Calendar integration working
- Gmail sending emails
- Document processor extracting text

**Testing**:
- Create calendar events
- Send email invitations
- Process various document types
- Extract structured data accurately

---

### Phase 8: Integration & Polish (Days 20-22)

**Tasks**:
1. Cross-module workflows
2. Error handling improvements
3. Logging enhancements
4. Performance optimization
5. Documentation completion
6. AgentCard.json configuration

**Deliverables**:
- All modules working together
- Comprehensive error handling
- Complete documentation
- Agent card properly configured

**Testing**:
- Complex multi-module workflows
- Error scenarios handled gracefully
- Performance benchmarks met
- Documentation reviewed

---

### Phase 9: Deployment & Testing (Days 23-25)

**Tasks**:
1. Final Docker configuration
2. Environment variable documentation
3. Deploy to Nasiko platform
4. End-to-end testing
5. Performance testing
6. Bug fixes

**Deliverables**:
- Agent deployed on Nasiko
- All features working in production
- Performance acceptable
- Bugs resolved

**Testing**:
- Full regression test suite
- Performance under load
- Edge cases handled
- Production deployment successful

---

## Testing Strategy

### Unit Testing

**Coverage**:
- Each module method tested independently
- Database operations validated
- External API mocks tested
- Utility functions verified

**Tools**:
- pytest for test framework
- pytest-asyncio for async tests
- unittest.mock for mocking

**Example**:
```python
@pytest.mark.asyncio
async def test_create_ticket():
    cs_module = CustomerServiceModule()
    result = await cs_module.create_ticket(
        customer_email="test@example.com",
        subject="Test Ticket",
        description="This is a test",
        priority="high"
    )
    assert "TKT-" in result
    assert "created successfully" in result
```

---

### Integration Testing

**Coverage**:
- Tool → Module → Database flows
- Cross-module workflows
- External API integrations
- Pipeline execution

**Example Scenarios**:
1. "Analyze this invoice and create an expense record"
   - DocumentProcessor → Finance → Database
2. "Create a support ticket and schedule a follow-up meeting"
   - CustomerService → Scheduling → Google Calendar → Gmail
3. "Process this sales data and email me a report"
   - DataAnalytics → Scheduling → Gmail

---

### End-to-End Testing

**Coverage**:
- JSON-RPC request → Response
- Multi-turn conversations
- Session management
- Error recovery

**Test Cases**:
```json
{
  "jsonrpc": "2.0",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [{
        "kind": "text",
        "text": "I have an invoice from Acme Corp for $1,250. Can you process it, create an expense record, and schedule a meeting next week to discuss?"
      }]
    }
  }
}
```

**Expected Flow**:
1. Agent receives request
2. Selects multi-step workflow tool
3. Planner creates 3 tasks:
   - Process invoice (DocumentProcessor)
   - Create expense (Finance)
   - Schedule meeting (Scheduling)
4. Executor runs tasks sequentially
5. Aggregator synthesizes results
6. Response returned with confirmation

---

## Deployment Plan

### Local Development

```bash
# 1. Clone repository
git clone <repo-url>
cd unified-business-agent

# 2. Create .env file
cp .env.example .env
# Edit .env with your API keys

# 3. Build Docker image
docker build -t unified-business-agent .

# 4. Run locally
docker run -p 5000:5000 --env-file .env unified-business-agent

# 5. Test
curl -X POST http://localhost:5000/ \
  -H "Content-Type: application/json" \
  -d @test-request.json
```

---

### Nasiko Platform Deployment

**Option 1: GitHub (Recommended)**

```bash
# 1. Create GitHub repo
# 2. Push code
git add .
git commit -m "Initial implementation"
git push origin main

# 3. Deploy via Nasiko dashboard
# - Navigate to "Add Agent"
# - Select "Connect GitHub"
# - Authenticate and select repository
# - Monitor deployment status
```

**Option 2: ZIP Upload**

```bash
# 1. Create ZIP file
zip -r unified-business-agent.zip . \
  -x "*.pyc" "*/__pycache__/*" "*/.git/*" "*/.env"

# 2. Upload via Nasiko dashboard
# - Navigate to "Add Agent"
# - Select "Upload ZIP"
# - Upload file and monitor deployment
```

---

### Environment Configuration

**Required Variables**:
```env
# Groq Cloud API
GROQ_API_KEY=your_groq_api_key

# Optional: Google APIs (calendar + Gmail). If omitted, app uses mock modes.
GOOGLE_CREDENTIALS_PATH=/app/credentials/google_credentials.json
GOOGLE_CALENDAR_ID=primary

# MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=BusinessAgentDB
USE_MONGODB=true

# Optional: SMTP fallback (not required)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Optional: Document AI
DOCUMENT_AI_ENDPOINT=https://api.documentai.com
DOCUMENT_AI_API_KEY=your_key

# Optional: External Support Ticket System
# Keep TICKET_SYSTEM_TYPE=internal for built-in DB ticketing (default)
# Example Zendesk endpoint: https://your-subdomain.zendesk.com/api/v2
# Example Freshdesk endpoint: https://your-domain.freshdesk.com/api/v2
TICKET_SYSTEM_ENDPOINT=
TICKET_SYSTEM_API_KEY=your_key
```

---

## Success Metrics

### Functional Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Tool success rate | >95% | Successful tool executions / total |
| Module coverage | 100% | All 5 modules implemented and tested |
| Integration tests passing | 100% | All integration tests green |
| End-to-end test passing | >95% | E2E scenarios successful |

### Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Simple query response time | <3s | Time from request to response |
| Complex workflow response time | <15s | Multi-step task completion |
| Database query time | <500ms | Average query execution |
| External API call time | <2s | Calendar, email, OCR calls |

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Code coverage | >80% | pytest coverage report |
| Documentation completeness | 100% | All modules documented |
| Error handling coverage | >90% | Try-catch blocks for failures |
| Logging coverage | 100% | All key operations logged |

---

## Risk Mitigation

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Groq API rate limits | High | Implement retry logic, use multiple models |
| External API failures | Medium | Mock implementations, graceful degradation |
| MongoDB unavailable | Medium | File-based fallback database |
| Document AI inaccuracy | Low | Manual review workflow, confidence scores |

### Schedule Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Module complexity underestimated | High | Prioritize core features, cut nice-to-haves |
| Integration issues | Medium | Early integration testing, modular design |
| Testing takes longer | Medium | Automated tests, parallel testing |

---

## Conclusion

The Unified Business Agent project combines three powerful business domains into a single, intelligent system. By leveraging the proven architecture from HR-system and adapting it for Groq Cloud and multi-domain operations, we can create a hackathon-winning agent that demonstrates:

- **Technical Excellence**: Modular architecture, proper error handling, production-ready code
- **Innovation**: Multi-domain unification, intelligent workflow orchestration
- **Practicality**: Real business value across customer service, analytics, and finance
- **Scalability**: Easy to extend with new modules and capabilities

The 25-day development plan provides a clear roadmap from foundation to deployment, with built-in testing and validation at each phase. This ensures a high-quality submission that showcases the full potential of AI agents in business automation.

---

**Next Steps**:
1. Review and approve this plan
2. Set up development environment
3. Begin Phase 1: Foundation
4. Iterate and refine based on progress
