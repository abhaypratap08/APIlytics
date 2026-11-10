# APIlytics Decisions Log

Creator / backend owner: **Abhay Pratap Singh**.

## 2026-11-10 — Creator attribution

- All API responses set `X-Creator: Abhay Pratap Singh` and
  `X-Project-Owner: Backend and Integration` via HTTP middleware.
- FastAPI OpenAPI metadata (`contact`, `description`) names Abhay as creator.
- `/` root response includes `creator` and `role` fields (non-contract-bound).
- The dev console at `/ui` shows the byline and a footer credit.
- Docker Compose labels: `com.apilytics.creator`, `com.apilytics.role`.
- Health response shape `{"status":"ok"}` is intentionally unchanged to keep
  contract tests stable — creator info is transported via header only.
