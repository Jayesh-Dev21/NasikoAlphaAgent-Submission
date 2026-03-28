# Implementation Roadmap

Detailed task breakdown for building the Unified Business Agent over 25 days.

## Progress Tracker

- ✅ Completed
- 🚧 In Progress
- ⏳ Pending
- ⏭️ Deferred

---

## Phase 1: Foundation (Days 1-2)

### Goal
Set up project scaffolding, basic server, and Docker configuration.

### Tasks

- [x] **1.1** Create project directory structure
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 30 min

- [x] **1.2** Create all documentation files
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 3 hours

- [ ] **1.3** Configure .env.example with all variables
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 30 min

- [ ] **1.4** Create .gitignore
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 15 min

- [ ] **1.5** Create pyproject.toml with dependencies
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 30 min

- [ ] **1.6** Implement Pydantic models (models.py)
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 1 hour
  - Dependencies: None

- [ ] **1.7** Implement FastAPI server (__main__.py)
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - Dependencies: 1.6

- [ ] **1.8** Create Dockerfile
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 30 min

- [ ] **1.9** Create docker-compose.yml
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 30 min

- [ ] **1.10** Test: Build Docker image successfully
  - Priority: HIGH
  - Test Case: `docker build -t uba .`

- [ ] **1.11** Test: Run container and access health endpoint
  - Priority: HIGH
  - Test Case: `curl http://localhost:5000/health`

### Deliverables
- ✅ Working FastAPI server
- ✅ Health check endpoint returns 200
- ✅ Docker container builds and runs
- ✅ All configuration documented

---

## Phase 2: Core Architecture (Days 3-5)

### Goal
Implement the modular pipeline (Planner, Router, Executor, Aggregator) and base module interface.

### Tasks

- [ ] **2.1** Implement BaseModule abstract class
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 1 hour
  - File: `src/core/base_module.py`

- [ ] **2.2** Set up Groq Cloud API integration
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 1 hour
  - Test: Verify API key works

- [ ] **2.3** Implement Planner with llama-3.1-70b
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - File: `src/core/planner.py`
  - Dependencies: 2.2

- [ ] **2.4** Implement TaskRouter
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 1.5 hours
  - File: `src/core/router.py`
  - Dependencies: 2.1

- [ ] **2.5** Implement TaskExecutor
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 1.5 hours
  - File: `src/core/executor.py`
  - Dependencies: 2.4

- [ ] **2.6** Implement Aggregator with llama-3.1-70b
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - File: `src/core/aggregator.py`
  - Dependencies: 2.2

- [ ] **2.7** Implement basic agent.py with Groq
  - Priority: HIGH
  - Complexity: High
  - Estimate: 3 hours
  - File: `src/agent.py`
  - Dependencies: 2.2

- [ ] **2.8** Create initial tools.py structure
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - File: `src/tools.py`

- [ ] **2.9** Connect agent to modular pipeline
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 1 hour
  - Dependencies: 2.7, 2.8, 2.3, 2.5, 2.6

- [ ] **2.10** Test: Planner outputs valid JSON tasks
  - Test Case: Simple query → valid task list

- [ ] **2.11** Test: End-to-end pipeline execution
  - Test Case: Query → Plan → Execute → Aggregate

### Deliverables
- Complete modular pipeline operational
- Agent can process simple requests
- Pipeline properly integrated with LangChain

---

## Phase 3: Database Layer (Days 6-7)

### Goal
Implement MongoDB and file-based database with abstraction layer.

### Tasks

- [ ] **3.1** Implement database abstraction (database.py)
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 1.5 hours
  - File: `src/utils/database.py`

- [ ] **3.2** Implement file-based database
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - File: `src/utils/database.py`
  - Features: JSON file storage, CRUD operations

- [ ] **3.3** Implement MongoDB database
  - Priority: HIGH
  - Complexity: High
  - Estimate: 4 hours
  - File: `src/utils/mongodb_database.py`
  - Features: Full CRUD, indexes, aggregations

- [ ] **3.4** Define database schemas for all collections
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - Collections: tickets, datasets, expenses, events, documents

- [ ] **3.5** Create database indexes for performance
  - Priority: MEDIUM
  - Complexity: Simple
  - Estimate: 1 hour

- [ ] **3.6** Implement fallback mechanism
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 1 hour
  - Feature: Auto-switch to file DB if MongoDB unavailable

- [ ] **3.7** Create mock/seed data for testing
  - Priority: MEDIUM
  - Complexity: Simple
  - Estimate: 1 hour

- [ ] **3.8** Test: MongoDB CRUD operations
  - Test Case: Insert, find, update, delete

- [ ] **3.9** Test: File-based fallback works
  - Test Case: Run without MongoDB, verify file storage

- [ ] **3.10** Test: Database abstraction layer
  - Test Case: Switch between MongoDB and file-based seamlessly

### Deliverables
- MongoDB integration complete
- File-based fallback operational
- All schemas defined and indexed
- Database utilities fully tested

---

## Phase 4: Customer Service Module (Days 8-10)

### Goal
Implement full customer service capabilities with ticket management.

### Tasks

- [ ] **4.1** Create CustomerServiceModule class
  - Priority: HIGH
  - Complexity: High
  - Estimate: 3 hours
  - File: `src/modules/customer_service.py`

- [ ] **4.2** Implement ticket creation
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 1.5 hours
  - Method: `create_ticket()`

- [ ] **4.3** Implement ticket retrieval
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 1 hour
  - Method: `get_ticket()`

- [ ] **4.4** Implement ticket update
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 1 hour
  - Method: `update_ticket()`

- [ ] **4.5** Implement ticket closure
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 1 hour
  - Method: `close_ticket()`

- [ ] **4.6** Implement sentiment analysis
  - Priority: MEDIUM
  - Complexity: Medium
  - Estimate: 2 hours
  - Method: `analyze_sentiment()`
  - Use: Groq LLM or simple heuristics

- [ ] **4.7** Implement FAQ knowledge base
  - Priority: MEDIUM
  - Complexity: Medium
  - Estimate: 2 hours
  - Method: `search_faq()`

- [ ] **4.8** Add email notification support
  - Priority: MEDIUM
  - Complexity: Medium
  - Estimate: 1.5 hours
  - Integration: Gmail utility

- [ ] **4.9** Create tools for customer service
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - File: `src/tools.py` (add 3 tools)

- [ ] **4.10** Test: Create and retrieve tickets
  - Test Case: End-to-end ticket lifecycle

- [ ] **4.11** Test: Sentiment analysis accuracy
  - Test Case: Positive/negative/neutral messages

- [ ] **4.12** Test: Email notifications sent
  - Test Case: Ticket creation triggers email

### Deliverables
- Full customer service module
- Ticket CRUD operations working
- Sentiment analysis functional
- Email notifications operational

---

## Phase 5: Data Analytics Module (Days 11-13)

### Goal
Implement data processing, analysis, and reporting capabilities.

### Tasks

- [ ] **5.1** Create DataAnalyticsModule class
  - Priority: HIGH
  - Complexity: High
  - Estimate: 3 hours
  - File: `src/modules/data_analytics.py`

- [ ] **5.2** Implement CSV file loading
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - Library: pandas

- [ ] **5.3** Implement Excel file loading
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 1 hour
  - Library: openpyxl

- [ ] **5.4** Implement JSON file loading
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 1 hour

- [ ] **5.5** Implement data analysis algorithms
  - Priority: HIGH
  - Complexity: High
  - Estimate: 4 hours
  - Features: Statistics, trends, patterns

- [ ] **5.6** Implement report generation
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - Method: `generate_report()`

- [ ] **5.7** Implement pattern detection
  - Priority: MEDIUM
  - Complexity: High
  - Estimate: 3 hours
  - Method: `detect_patterns()`

- [ ] **5.8** Implement custom data queries
  - Priority: MEDIUM
  - Complexity: Medium
  - Estimate: 2 hours
  - Method: `query_data()`

- [ ] **5.9** Create tools for data analytics
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - File: `src/tools.py` (add 4 tools)

- [ ] **5.10** Test: Load various file formats
  - Test Case: CSV, Excel, JSON files

- [ ] **5.11** Test: Analyze sample datasets
  - Test Case: Sales data, customer data

- [ ] **5.12** Test: Generate reports
  - Test Case: Quarterly revenue report

### Deliverables
- Data analytics module complete
- Multi-format file support (CSV, Excel, JSON)
- Analysis and reporting functional
- Pattern detection working

---

## Phase 6: Finance Module (Days 14-16)

### Goal
Implement expense tracking and invoice processing with OCR.

### Tasks

- [ ] **6.1** Create FinanceModule class
  - Priority: HIGH
  - Complexity: High
  - Estimate: 3 hours
  - File: `src/modules/finance.py`

- [ ] **6.2** Implement expense tracking
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - Method: `add_expense()`

- [ ] **6.3** Implement expense retrieval with filters
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 1.5 hours
  - Method: `get_expenses()`

- [ ] **6.4** Implement expense categorization
  - Priority: MEDIUM
  - Complexity: Medium
  - Estimate: 2 hours
  - Feature: Auto-categorize based on description

- [ ] **6.5** Integrate Document AI utility
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 1 hour
  - Dependency: Phase 7 (can parallelize)

- [ ] **6.6** Implement invoice processing pipeline
  - Priority: HIGH
  - Complexity: High
  - Estimate: 3 hours
  - Method: `process_invoice()`
  - Flow: OCR → Parse → Create Expense

- [ ] **6.7** Implement budget tracking
  - Priority: MEDIUM
  - Complexity: Medium
  - Estimate: 2 hours
  - Method: `check_budget()`

- [ ] **6.8** Implement financial reporting
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - Method: `generate_financial_report()`

- [ ] **6.9** Create tools for finance
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - File: `src/tools.py` (add 3 tools)

- [ ] **6.10** Test: Add and retrieve expenses
  - Test Case: CRUD operations

- [ ] **6.11** Test: Process invoice images
  - Test Case: Upload PDF/image, extract data

- [ ] **6.12** Test: Financial summaries
  - Test Case: Monthly expense report

### Deliverables
- Finance module complete
- Expense CRUD operations working
- Invoice OCR functional
- Financial reports generated

---

## Phase 7: Scheduling & Document Modules (Days 17-19)

### Goal
Implement calendar integration and document processing with OCR.

### Tasks

#### Scheduling Module

- [ ] **7.1** Create SchedulingModule class
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - File: `src/modules/scheduling.py`

- [ ] **7.2** Implement Google Calendar utility
  - Priority: HIGH
  - Complexity: High
  - Estimate: 4 hours
  - File: `src/utils/google_calendar.py`
  - Features: OAuth, event creation, Meet links

- [ ] **7.3** Implement Gmail utility
  - Priority: HIGH
  - Complexity: High
  - Estimate: 3 hours
  - File: `src/utils/gmail.py`
  - Features: OAuth, send emails

- [ ] **7.4** Implement meeting scheduling
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - Method: `schedule_meeting()`

- [ ] **7.5** Implement slot finding
  - Priority: MEDIUM
  - Complexity: Medium
  - Estimate: 2 hours
  - Method: `find_available_slots()`

- [ ] **7.6** Implement event management
  - Priority: MEDIUM
  - Complexity: Simple
  - Estimate: 1 hour
  - Methods: `cancel_event()`, `reschedule_event()`

#### Document Processor Module

- [ ] **7.7** Create DocumentProcessorModule class
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - File: `src/modules/document_processor.py`

- [ ] **7.8** Implement Document AI utility
  - Priority: HIGH
  - Complexity: High
  - Estimate: 4 hours
  - File: `src/utils/document_ai.py`
  - Features: PDF extraction, OCR, parsing

- [ ] **7.9** Implement text extraction
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - Method: `extract_text()`

- [ ] **7.10** Implement invoice parsing
  - Priority: HIGH
  - Complexity: High
  - Estimate: 3 hours
  - Method: `process_invoice()`

- [ ] **7.11** Implement receipt parsing
  - Priority: MEDIUM
  - Complexity: Medium
  - Estimate: 2 hours
  - Method: `process_receipt()`

- [ ] **7.12** Create tools for scheduling and documents
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - File: `src/tools.py` (add 4 tools)

- [ ] **7.13** Test: Create calendar events
  - Test Case: Schedule meeting, verify in Google Calendar

- [ ] **7.14** Test: Send email invitations
  - Test Case: Meeting invitation received

- [ ] **7.15** Test: Process documents
  - Test Case: PDF, image → extracted text

### Deliverables
- Scheduling module complete
- Google Calendar integration working
- Gmail sending emails
- Document processor extracting text
- OCR functional

---

## Phase 8: Integration & Polish (Days 20-22)

### Goal
Cross-module workflows, error handling, logging, and documentation.

### Tasks

- [ ] **8.1** Implement cross-module workflows
  - Priority: HIGH
  - Complexity: High
  - Estimate: 4 hours
  - Test: "Process invoice and schedule meeting"

- [ ] **8.2** Enhance error handling across all modules
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 3 hours
  - Feature: Graceful degradation, user-friendly errors

- [ ] **8.3** Add comprehensive logging
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - Feature: Structured logging, log levels

- [ ] **8.4** Implement mock services for all external APIs
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 3 hours
  - Mocks: Calendar, Gmail, OCR

- [ ] **8.5** Performance optimization
  - Priority: MEDIUM
  - Complexity: Medium
  - Estimate: 2 hours
  - Features: Caching, connection pooling

- [ ] **8.6** Create AgentCard.json
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 1 hour

- [ ] **8.7** Create curlPOST.json examples
  - Priority: MEDIUM
  - Complexity: Simple
  - Estimate: 1 hour

- [ ] **8.8** Complete all documentation
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 3 hours
  - Files: api-integration.md, deployment.md

- [ ] **8.9** Code cleanup and refactoring
  - Priority: MEDIUM
  - Complexity: Medium
  - Estimate: 2 hours

- [ ] **8.10** Test: Complex multi-module workflow
  - Test Case: Invoice → Expense → Meeting → Email

- [ ] **8.11** Test: Error scenarios
  - Test Case: Invalid inputs, API failures

- [ ] **8.12** Test: Mock services work
  - Test Case: Run without any external credentials

### Deliverables
- All modules working together
- Comprehensive error handling
- Complete documentation
- AgentCard properly configured
- Mock services operational

---

## Phase 9: Deployment & Testing (Days 23-25)

### Goal
Final testing, deployment to Nasiko platform, and bug fixes.

### Tasks

- [ ] **9.1** Final Docker configuration review
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 1 hour

- [ ] **9.2** Create deployment documentation
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours
  - File: `docs/deployment.md`

- [ ] **9.3** Environment variable documentation
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 1 hour
  - Update: `.env.example`, README

- [ ] **9.4** Write unit tests
  - Priority: HIGH
  - Complexity: High
  - Estimate: 6 hours
  - Coverage: All modules

- [ ] **9.5** Write integration tests
  - Priority: HIGH
  - Complexity: High
  - Estimate: 4 hours
  - Coverage: Cross-module workflows

- [ ] **9.6** Run full test suite
  - Priority: HIGH
  - Complexity: Simple
  - Estimate: 1 hour
  - Target: >80% coverage

- [ ] **9.7** Fix bugs from testing
  - Priority: HIGH
  - Complexity: Variable
  - Estimate: 4 hours

- [ ] **9.8** Performance testing
  - Priority: MEDIUM
  - Complexity: Medium
  - Estimate: 2 hours
  - Metrics: Response times, throughput

- [ ] **9.9** Deploy to Nasiko platform (GitHub)
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours

- [ ] **9.10** End-to-end testing on Nasiko
  - Priority: HIGH
  - Complexity: Medium
  - Estimate: 2 hours

- [ ] **9.11** Fix deployment issues
  - Priority: HIGH
  - Complexity: Variable
  - Estimate: 2 hours

- [ ] **9.12** Final documentation review
  - Priority: MEDIUM
  - Complexity: Simple
  - Estimate: 1 hour

- [ ] **9.13** Create demo video/screenshots
  - Priority: LOW
  - Complexity: Simple
  - Estimate: 1 hour

### Deliverables
- Agent deployed on Nasiko platform
- All features working in production
- Test coverage >80%
- Complete documentation
- Bugs resolved

---

## Testing Checkpoints

### Checkpoint 1: Foundation (End of Phase 1)
- [ ] Server starts without errors
- [ ] Health check returns 200 OK
- [ ] Docker container runs successfully
- [ ] Can make basic JSON-RPC request

### Checkpoint 2: Core Architecture (End of Phase 2)
- [ ] Planner outputs valid task JSON
- [ ] Router selects correct modules
- [ ] Executor runs tasks sequentially
- [ ] Aggregator creates coherent responses
- [ ] Agent processes simple queries

### Checkpoint 3: Database (End of Phase 3)
- [ ] MongoDB CRUD operations work
- [ ] File-based fallback operational
- [ ] Database abstraction seamless
- [ ] Indexes improve query performance

### Checkpoint 4: First Module (End of Phase 4)
- [ ] Can create support tickets
- [ ] Can retrieve ticket information
- [ ] Sentiment analysis works
- [ ] Email notifications sent

### Checkpoint 5: All Modules (End of Phase 7)
- [ ] All 5 modules implemented
- [ ] All 15+ tools working
- [ ] External APIs integrated
- [ ] Mock services available

### Checkpoint 6: Integration (End of Phase 8)
- [ ] Cross-module workflows execute
- [ ] Error handling comprehensive
- [ ] Logging complete
- [ ] Documentation finished

### Checkpoint 7: Production (End of Phase 9)
- [ ] Deployed on Nasiko platform
- [ ] All tests passing
- [ ] Performance acceptable
- [ ] No critical bugs

---

## Risk Mitigation Strategies

### Technical Risks

**Groq API Rate Limits**
- Mitigation: Implement retry logic with exponential backoff
- Fallback: Use different model tiers
- Monitoring: Track API usage

**External API Failures**
- Mitigation: Mock implementations for all services
- Fallback: Graceful degradation with clear user messages
- Testing: Test with APIs disabled

**MongoDB Unavailable**
- Mitigation: File-based database fallback
- Testing: Run without MongoDB connection
- Monitoring: Health check includes database status

**OCR Accuracy Issues**
- Mitigation: Confidence scores and validation
- Fallback: Manual review workflow
- Testing: Various document qualities

### Schedule Risks

**Module Complexity Underestimated**
- Mitigation: Prioritize core features, defer nice-to-haves
- Buffer: Built-in time buffers in each phase
- Flexibility: Can skip optional features

**Integration Issues**
- Mitigation: Early integration testing
- Strategy: Modular design allows parallel development
- Testing: Integration tests from Phase 4 onwards

**Testing Takes Longer**
- Mitigation: Automated tests from day 1
- Strategy: Parallel testing while building
- Priority: Focus on critical paths

---

## Current Status

**Phase 1**: 🚧 In Progress
- [x] Directory structure created
- [x] Documentation files created
- [ ] Configuration files pending
- [ ] Implementation files pending

**Next Steps**:
1. Complete Phase 1 configuration files
2. Implement Pydantic models
3. Build FastAPI server
4. Test Docker build

---

## Daily Schedule (Example)

### Day 1
- Morning: Project setup, directory structure
- Afternoon: Documentation (README, structure.md)
- Evening: Configuration files

### Day 2
- Morning: Pydantic models, FastAPI server
- Afternoon: Docker configuration
- Evening: Test Phase 1 deliverables

### Day 3
- Morning: BaseModule, Groq setup
- Afternoon: Planner implementation
- Evening: Router implementation

*[Continue for all 25 days...]*

---

This roadmap provides a clear path from foundation to deployment with built-in testing, risk mitigation, and flexibility for schedule adjustments.
