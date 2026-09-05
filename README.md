# FRA AI Decision Support

### GIS-Based Evidence & Decision-Support Platform for Forest Rights Act (FRA) Claims

> Turning fragmented evidence into transparent, explainable, and auditable workflows while keeping final decisions with authorized human authorities.

## Live Demo

**https://fra-ai-decision-support-rohq.vercel.app**

The live demo uses synthetic/demo data to demonstrate the evidence and decision-support workflow.

---

## Problem Statement

Forest Rights Act (FRA) claim processing involves multiple forms of evidence, including land records, spatial information, field verification, satellite observations, and community evidence.

However, this information can be fragmented across different sources, making it difficult to efficiently analyze, verify, track, and audit claims.

This creates a need for a technology-driven platform that can bring evidence together, provide meaningful spatial and workflow insights, and support transparent decision-making.

The challenge is not simply collecting more data. The challenge is turning scattered evidence into an understandable, traceable, and actionable workflow.

---

## Our Solution

FRA AI Decision Support is a GIS-based decision-support platform that combines:

* Satellite change detection signals
* GIS and spatial analysis
* Explainable AI/ML signals
* Workflow anomaly analysis
* Field verification
* Community evidence
* Evidence tracking
* Review and analytics

The platform brings these components together into a unified workflow so that authorized users can review evidence, identify signals requiring attention, and make better-informed decisions.

### Human-in-the-Loop

The system is designed to support, not replace, authorized decision-makers.

It does not automatically approve or reject FRA claims and does not make legal conclusions.

---

## Key Features

### 1. Interactive GIS Evidence Map

Visualize claim-related information spatially through an interactive map.

The map can help users understand:

* Claim locations
* Spatial boundaries
* Evidence points
* Change-detection signals
* Field observations
* Other geographic information

This provides spatial context for evidence review.

### 2. Satellite Change Detection

The platform incorporates satellite/change records to identify possible land-cover changes.

These outputs are treated as signals for further verification rather than definitive proof.

> DEMO DATA — Possible change requiring human verification

### 3. Explainable AI Signals

Instead of relying on an unexplained black-box prediction, the platform presents interpretable signals that can help reviewers understand why a case may require additional attention.

Signals can include:

* Spatial relationships
* Evidence availability
* Change indicators
* Missing verification
* Workflow inconsistencies

### 4. Workflow Anomaly Analysis

The platform analyzes claim-processing workflows to identify unusual patterns.

It can surface:

* Processing delays
* Missing workflow stages
* Repeated activities
* Unusual workflow patterns
* Cases requiring review

### Delay Genome

Delay Genome is an operational workflow-analysis feature. It is not a legal-deadline determination system.

### 5. Evidence Ledger

The Evidence Ledger provides a structured record of information associated with a case.

It can track:

* Evidence sources
* Evidence status
* Verification information
* Spatial observations
* Review activity
* Workflow events

This helps create a more traceable and auditable workflow.

### 6. Community and Field Evidence

The platform brings different forms of evidence into the same workflow, including:

* Field verification
* Community evidence
* Supporting information
* Review notes

This allows human-collected evidence to be considered alongside spatial and analytical signals.

### 7. End-to-End Claim Workflow

The platform follows a structured workflow:

```text
Claim
  |
  v
Evidence Collection
  |
  v
Spatial and Data Analysis
  |
  v
AI / Change Signals
  |
  v
Field and Community Verification
  |
  v
Review
  |
  v
Human Decision
```

The key principle is:

> Evidence → Signals → Verification → Human Decision

### 8. Simulate New Claim

The demo provides a Simulate New Claim workflow to demonstrate the system without requiring real claimant information.

A synthetic case can be generated and processed through the platform to demonstrate:

1. Claim creation
2. Evidence association
3. Spatial analysis
4. Signal generation
5. Workflow analysis
6. Review requirements
7. Human decision-support

---

## System Architecture

```text
                    +---------------------+
                    |   React + Vite UI   |
                    |    Web Dashboard    |
                    +----------+----------+
                               |
                          REST APIs
                               |
                    +----------v----------+
                    |       FastAPI       |
                    |   Backend Services  |
                    +----------+----------+
                               |
          +--------------------+--------------------+
          |                    |                    |
          v                    v                    v
   Evidence Engine      Spatial Analysis     Workflow Analysis
          |                    |                    |
          +--------------------+--------------------+
                               |
                    +----------v----------+
                    |      SQLite DB      |
                    |   Demo Data Layer   |
                    +---------------------+
```

---

## Technologies Used

### Frontend

* React.js
* Vite
* Leaflet
* GIS / Interactive Mapping

### Backend

* Python
* FastAPI
* REST APIs

### AI and Data Analysis

* Machine Learning
* Computer Vision
* Remote Sensing
* Satellite Imagery
* Spatial / GIS Analysis

### Database

* SQLite

---

## Project Structure

```text
FRA-AI-Decision-Support/
|
├── app/
│   ├── main.py
│   └── ...
|
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
|
├── data/
│   └── ...
|
├── requirements.txt
└── README.md
```

---

## Run Locally

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <PROJECT_FOLDER>
```

### 2. Create a virtual environment

For Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Start the backend

```powershell
$env:DATABASE_MODE='demo'
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will start using the Vite development server.

---

## Deployment

The current public application is deployed on Vercel.

### Live Application

**https://fra-ai-decision-support-rohq.vercel.app**

The deployed frontend uses the configured API services to communicate with the backend.

---

## Demo Mode

The project includes a deterministic demo mode so the workflow can be demonstrated without requiring real claimant credentials or government-system access.

Demo mode contains:

* 20 synthetic cases
* Deterministic evidence
* Synthetic spatial records
* Demo satellite/change observations
* Workflow events
* Review information
* Community evidence
* Analytics

The supplied CSV data is treated as immutable state aggregates.

---

## Data and Scientific Disclaimer

This prototype uses synthetic/demo data.

The demo data does not represent:

* Real FRA claims
* Real individuals
* Official government records
* Verified land observations
* Verified claimant information
* Scientifically validated satellite conclusions

Satellite/change outputs indicate only possible land-cover change requiring human verification.

---

## Responsible AI

FRA AI Decision Support follows a human-in-the-loop approach.

### The system provides:

```text
Evidence → Analysis → Signals → Verification → Review
```

### The system does not provide:

```text
Evidence → Automatic Legal Decision
```

The final decision remains with authorized human authorities.

The platform does not claim:

* Autonomous adjudication
* Legal decision-making
* Legal conclusions
* Scientific certainty
* Replacement of government authorities

---

## Why This Matters

| Existing Challenge               | Our Approach                   |
| -------------------------------- | ------------------------------ |
| Fragmented evidence              | Unified evidence workflow      |
| Difficult spatial interpretation | Interactive GIS map            |
| Large amounts of information     | Structured evidence view       |
| Possible land-cover changes      | Satellite/change signals       |
| Workflow bottlenecks             | Workflow anomaly analysis      |
| Difficult auditing               | Evidence Ledger                |
| Need for ground verification     | Field verification support     |
| Community evidence               | Community evidence module      |
| Risk of automated decisions      | Human-in-the-loop architecture |

---

## Expected Impact

### Faster Review

Surface relevant evidence and workflow signals more efficiently.

### Greater Transparency

Make evidence and processing stages easier to understand.

### Better Auditability

Maintain a structured evidence and workflow trail.

### Better Spatial Understanding

Connect claims with geographic and satellite-derived information.

### Stronger Evidence Integration

Bring field and community evidence into the same workflow.

### Responsible Decision Support

Use technology to assist authorized decision-makers rather than replace them.

---

## Future Scope

Future versions can include:

* PostGIS spatial database integration
* Higher-resolution satellite imagery
* Advanced geospatial analytics
* Mobile application for field officers
* Offline-first field data collection
* Digital evidence verification
* Role-based access control
* Government-approved data integrations
* Scalable cloud infrastructure
* Advanced change-detection pipelines

---

## Security and Privacy

The prototype is designed for demonstration purposes and does not process real claimant credentials.

Future production deployment would require:

* Role-based authentication
* Authorization controls
* Secure data storage
* Encryption
* Audit logging
* Data-retention policies
* Government-approved integrations
* Privacy and access controls

---

## Project Vision

> To build transparent evidence infrastructure for FRA workflows where technology strengthens verification, accountability, and accessibility without taking the decision away from people.

### FRA AI Decision Support

**Evidence you can trace.
Signals you can explain.
Decisions humans can trust.**

