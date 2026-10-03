# ServicePulse — Engineering Decisions

**Version:** 1.0
**Last Updated:** 2025-07-08**

This document contains Architectural Decision Records (ADRs) for key technical choices.

---

## ADR-001: Why FastAPI

**Date:** 2025-07-08  
**Status:** Accepted

### Context

We need an API framework that:
- Supports async operations for future scalability
- Provides automatic OpenAPI documentation
- Encourages type safety through type hints
- Has minimal overhead
- Integrates well with testing frameworks

### Options Considered

1. **FastAPI** — Modern, async-first, auto-docs, Pydantic integration
2. **Flask** — Mature, simple, but synchronous by default
3. **Django REST Framework** — Full-stack, heavier, overkill for this scope
4. **Starlette** — Lighter, but less features out of the box

### Decision

Choose FastAPI.

### Rationale

- Automatic OpenAPI/Swagger docs reduce documentation effort
- Type hints + Pydantic validation catch errors early
- Async support enables future non-blocking I/O
- Excellent test client for unit/integration tests
- Active community and good ecosystem

### Consequences

- Requires Python 3.10+ (we use 3.12+)
- Learning curve for team unfamiliar with async
- Slightly steeper learning curve than Flask

---

## ADR-002: Why SQLite Initially

**Date:** 2025-07-08  
**Status:** Accepted

### Context

We need a database for development that:
- Requires no configuration
- Works out of the box
- Is file-based for easy cleanup
- Will allow migration to PostgreSQL later

### Options Considered

1. **SQLite** — Zero-config, file-based, embedded
2. **PostgreSQL** — Production-grade, but requires setup
3. **MySQL** — Similar to PostgreSQL, more complex
4. **In-memory** — Fast, but data lost on restart

### Decision

Use SQLite for development, design for PostgreSQL migration.

### Rationale

- Zero configuration for developers
- File-based database is easy to version-control setup
- Migration path is straightforward (SQLAlchemy supports both)
- Reduces initial setup complexity from 30 minutes to 0

### Consequences

- Not suitable for multi-process deployment
- Must update `DATABASE_URL` for production
- Some PostgreSQL-specific features not tested initially

---

## ADR-003: Why Layered Architecture

**Date:** 2025-07-08  
**Status:** Accepted

### Context

We need to:
- Separate concerns properly
- Enable unit testing without database
- Allow database swapping without changing business logic
- Support multiple API versions in future

### Options Considered

1. **Layered (onion) architecture** — Clear separation of concerns
2. **Flat architecture** — All logic in route handlers
3. **MVC pattern** — Framework-enforced, less flexible

### Decision

Implement layered architecture:
```
API Layer → Service Layer → Domain Layer → Repository Layer → Database
```

### Rationale

- Route handlers are thin: only HTTP concerns
- Business logic in service layer, testable without HTTP
- Domain layer has pure logic (state machines, validation)
- Repository pattern isolates database access
- Easy to mock dependencies for testing

### Consequences

- More files/folders initially
- Slightly more boilerplate
- But easier to maintain and test long-term

---

## ADR-004: Why API Versioning

**Date:** 2025-07-08  
**Status:** Accepted

### Context

The API will evolve as:
- Project 2 adds CI/CD
- Project 3 transforms the system
- Project 5 builds the command center

We need to support backward compatibility.

### Options Considered

1. **URL versioning** (`/api/v1/`) — Explicit, cache-friendly
2. **Header versioning** — Less visible, harder to debug
3. **No versioning** — RISKY for this portfolio

### Decision

Use URL path versioning: `/api/v1/`

### Rationale

- Explicit and visible in logs/monitoring
- Easy to route to different implementations
- Cache-friendly (different URLs)
- Clear upgrade path for consumers

### Consequences

- Must maintain `/api/v1/` for backward compatibility
- Breaking changes require `/api/v2/` path
- All new endpoints must include `/api/v1/`

---

## ADR-005: Why Structured Logging

**Date:** 2025-07-08  
**Status:** Accepted

### Context

We need to:
- Analyze failures efficiently
- Correlate events across components
- Support future log aggregation

### Options Considered

1. **Structured JSON logs** — Machine-readable, queryable
2. **Plain text logs** — Human-readable, hard to parse
3. **Hybrid** — Mixed format, inconsistent

### Decision

JSON-formatted structured logs.

### Rationale

- Easier log aggregation and analysis
- Correlation ID searchable in every entry
- Can be parsed programmatically
- Standard format for observability tools

### Consequences

- Less human-readable in raw form (but tools exist)
- Slightly larger log volume
- Must ensure no sensitive data is logged

---

## ADR-006: Why Metrics Decoupled from Dashboard

**Date:** 2025-07-08  
**Status:** Accepted

### Context

Project 5 will build a dashboard, but Project 1 needs metrics now.

### Options Considered

1. **Separate metrics service** — Overkill for this scope
2. **Embedded metrics** — Simple, sufficient for now
3. **Built into dashboard** — Creates circular dependency

### Decision

Implement metrics in the backend, expose via `/api/v1/metrics`.

### Rationale

- Backend owns the data generation
- Dashboard can query metrics without backend changes
- Metrics format (Prometheus) is standard
- Project 5 can build dashboard independently

### Consequences

- Backend owns metrics schema
- Dashboard must handle metrics API changes
- But clear separation of concerns

---

## ADR-007: Why Modular Monolith

**Date:** 2025-07-08  
**Status:** Accepted

### Context

This is a time-constrained portfolio project with 5 interdependent projects.

### Options Considered

1. **Modular monolith** — One codebase, multiple services
2. **Microservices** — Distributed, complex
3. **Serverless** — Costly, vendor lock-in

### Decision

Build as a modular monolith.

### Rationale

- Single deployment unit (simpler)
- No network latency between components
- Easier to share code (services, domains)
- Can extract services later if needed
- Suitable for portfolio scope

### Consequences

- Not horizontally scalable without extraction
- All components share database
- But easier to develop and deploy initially

---

## Summary

| Decision | Rationale |
|---|---|
| FastAPI | Modern, async, auto-docs, good ecosystem |
| SQLite initially | Zero-config, easy migration path |
| Layered architecture | Testability, maintainability, separation |
| URL versioning | Explicit, cache-friendly, clear upgrade path |
| Structured logging | Queryable, correlation-friendly, standard |
| Decoupled metrics | Clear ownership, reusable by dashboard |
| Modular monolith | Simpler development, deployable, extractable later |
