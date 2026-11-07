# Contributing to APIlytics

Welcome to APIlytics!

This document defines the contribution workflow, development responsibilities, repository structure, and implementation expectations for everyone working on the project.

APIlytics is an AI-powered API analytics and intelligence platform focused on observing, detecting, optimizing, and protecting APIs.

Our goal is to maintain a modular and maintainable codebase where each team member owns their respective components while following shared architectural and integration standards.

## 1. Team Responsibilities

Each contributor is responsible for developing and maintaining their assigned component.

| Contributor | Responsibility | Directory |
|---|---|---|
| Abhay Pratap Singh (@abhaypratap08) | Backend, infrastructure, API development and integration | `backend/` |
| Jay Singh (@jaysingh-143) | Frontend development, dashboard and UI/UX | `frontend/` |
| Hariom Mani Tripathi (@Hariom0901) | Machine Learning, anomaly detection and cost intelligence | `ML/` |

## 2. Individual Development Responsibilities

### @jaysingh-143 — Frontend Development

**Primary responsibility:** Own the frontend development of APIlytics.

Create and maintain a dedicated `frontend/` directory in the repository root.

Expected responsibilities:

- Design and implement the APIlytics dashboard.
- Develop reusable UI components.
- Implement API traffic visualization and analytics dashboards.
- Build endpoint-level monitoring and statistics views.
- Develop anomaly alerts and security intelligence interfaces.
- Implement cost analytics and forecasting visualizations.
- Integrate frontend components with backend APIs.
- Handle loading, error, and empty states.
- Maintain responsive layouts and consistent UI design.

**Expected directory:**

```text
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── layouts/
│   ├── services/
│   ├── hooks/
│   ├── assets/
│   └── styles/
├── public/
├── package.json
└── README.md
```

You may modify the internal structure as needed, provided the frontend remains modular and maintainable.

**Deliverables:**

- A functional frontend application.
- Reusable dashboard components.
- API integration layer.
- Documented setup and execution instructions.
- Screenshots or demonstrations of implemented features.

### @Hariom0901 — Machine Learning & Cost Intelligence

**Primary responsibility:** Own the machine learning, anomaly detection, and cost intelligence components.

Create and maintain a dedicated `ML/` directory in the repository root.

Expected responsibilities:

- Develop API traffic anomaly detection.
- Explore and implement Isolation Forest or other suitable detection algorithms.
- Identify unusual traffic patterns and abnormal request behavior.
- Develop API abuse detection logic.
- Implement endpoint-level cost attribution.
- Explore cost forecasting and optimization techniques.
- Develop feature extraction and preprocessing pipelines.
- Evaluate model performance using appropriate metrics.
- Expose model inference functionality through clearly defined interfaces.
- Document model assumptions, inputs, outputs, and limitations.

**Expected directory:**

```text
ML/
├── models/
├── preprocessing/
├── detection/
├── cost_intelligence/
├── evaluation/
├── datasets/
├── tests/
└── README.md
```

You may extend this structure based on implementation requirements.

**Deliverables:**

- Working anomaly detection pipeline.
- Model training and inference modules, where applicable.
- Cost attribution and forecasting components.
- Evaluation results and relevant metrics.
- Documented input/output schemas.
- Instructions for running and testing ML components.

### @abhaypratap08 — Backend & Integration

**Primary responsibility:** Own backend development, infrastructure, and integration across project components.

Responsibilities include:

- FastAPI backend development.
- API routes, schemas, validation, and business logic.
- PostgreSQL and ClickHouse integration.
- Database session and connection management.
- Kafka-based telemetry ingestion and processing integration.
- Redis integration where required.
- Authentication and authorization.
- Integration of frontend and ML components.
- API contracts and service communication.
- Docker-based development infrastructure.

The backend should provide clearly defined interfaces for the frontend and ML components.

## 3. Repository Structure

The repository should gradually evolve toward the following structure:

```text
APIlytics/
│
├── backend/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── database/
│   └── tests/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
│
├── ML/
│   ├── models/
│   ├── preprocessing/
│   ├── detection/
│   ├── cost_intelligence/
│   ├── evaluation/
│   └── tests/
│
├── docs/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── CONTRIBUTING.md
└── SECURITY.md
```

This is the intended organizational direction, not a requirement to create every directory or placeholder immediately.

Each contributor should create and maintain their assigned directory as development progresses.

## 4. Development and Integration Guidelines

Although each contributor owns a separate component, all components must work together as one application.

### Shared Integration Rules

- Do not modify another contributor's component without discussing it first.
- Keep module boundaries clear.
- Define API contracts before implementing dependent integrations.
- Communicate changes that affect shared schemas or interfaces.
- Avoid duplicating functionality across directories.
- Keep configuration and secrets outside committed source code.
- Document external dependencies and setup requirements.

### Frontend ↔ Backend

Jay and Abhay should coordinate on:

- API endpoint definitions.
- Request and response schemas.
- Authentication requirements.
- Error handling.
- Data visualization formats.

### ML ↔ Backend

Hariom and Abhay should coordinate on:

- Telemetry input formats.
- Feature and preprocessing requirements.
- Model inference interfaces.
- Detection result schemas.
- Cost estimation outputs.
- Processing and inference expectations.

Do not independently assume interface formats. Agree on the contract before integration.

## 5. Contribution Workflow

Every contributor should follow this workflow:

1. Pull the latest changes from the main repository.
2. Work within the assigned component.
3. Create a dedicated feature or fix branch.
4. Implement the required functionality.
5. Test the implementation independently.
6. Update the relevant README or technical documentation.
7. Commit changes using the agreed conventions.
8. Push the branch and open a pull request.
9. Coordinate integration with the relevant team members.

### Branch Naming

Use descriptive branch names:

```text
feature/frontend-dashboard
feature/ml-anomaly-detection
feature/cost-forecasting
feature/backend-telemetry
fix/frontend-api-integration
fix/ml-preprocessing
```

Avoid committing unfinished work directly to the main branch.

## 6. Code Quality Standards

All contributors are expected to:

- Write readable and maintainable code.
- Use meaningful names for files, functions, and variables.
- Keep functions and modules focused.
- Avoid unnecessary dependencies.
- Handle errors explicitly.
- Remove debugging statements and unused code.
- Add tests for new functionality.
- Document non-obvious implementation decisions.

### Python

- Follow PEP 8 conventions.
- Use type hints where practical.
- Use appropriate exception handling.
- Keep dependencies documented.

### JavaScript / TypeScript

- Follow consistent formatting conventions.
- Prefer reusable components.
- Avoid duplicated logic.
- Handle asynchronous operations properly.
- Use TypeScript where appropriate.

## 7. Commit Guidelines

Use the following commit format:

```text
<type>: <short description>
```

| Type | Purpose |
|---|---|
| `feat` | New functionality |
| `fix` | Bug fixes |
| `refactor` | Code restructuring |
| `docs` | Documentation |
| `test` | Tests |
| `perf` | Performance improvements |
| `chore` | Maintenance |

Examples:

```text
feat: implement API analytics dashboard
feat: add isolation forest anomaly detection
feat: implement endpoint cost attribution
fix: resolve telemetry ingestion issue
refactor: modularize ML preprocessing
docs: update frontend setup instructions
```

Keep commits focused and descriptive.

## 8. Pull Request Guidelines

Before opening a pull request:

- Ensure changes belong to the assigned component.
- Verify that the implementation works independently.
- Run relevant tests.
- Update documentation.
- Check for unintended changes to other components.
- Ensure no credentials or environment files are included.

actual implementation progresses.

# Final Note

## Each contributor owns their respective component, but the final responsibility is shared.
