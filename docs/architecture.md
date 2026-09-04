# Architecture

The current implementation is a read-only, file-backed vertical slice. React/Vite consumes FastAPI endpoints; FastAPI parses the supplied CSVs through a repository layer and applies transparent operational rules. No LLM, generative model, autonomous legal decision, or new database is created.

```mermaid
flowchart LR
  CSV[Supplied FRA and land-use CSVs] --> R[Python repository]
  R --> API[FastAPI REST API]
  API --> UI[React/Vite dashboard]
  API --> S[Deterministic review signals]
  S --> H[Authorized human review]
```

Future claim-level services should add PostgreSQL/PostGIS only when the teammate supplies the authoritative schema and connection details. Analytical outputs should use a shared evidence object with source, acquisition date, method, provenance, limitations, and verification status.
