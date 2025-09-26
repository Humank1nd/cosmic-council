## ⚖️ Standard Operating Protocol (SOP) — Cosmic Council

### 🔑 Core Principles

- **Linearity First**: All workflows must strictly follow ROYGBV (Red → Orange → Yellow → Green → Blue → Purple).
- **Fractality Allowed**: Sub-cycles are permitted but must maintain internal ROYGBV order and merge cleanly back into parent cycles.
- **Audit Everything**: Every change must be logged, explainable, and reversible.
- **No Orphans**: Every schema, script, or workflow must link to a cycle, stage, or higher entity.
- **Symmetry in Evolution**: Changes must improve clarity, completeness, and continuity.

---

### 🏗️ 1. Adding New Features

#### Steps
1. **Open a Feature Request**
   - Create an issue in GitHub under `/issues/feature`.
   - Include: problem statement, affected enterprise(s), expected output.
2. **Design in Docs**
   - Write a short RFC in `/docs/rfcs/[date]_[feature_name].md`.
   - Must include: diagrams (if applicable), DB schema changes, workflow changes.
3. **Branch Naming Convention**
   - `feature/[enterprise]_[feature_name]`
   - Example: `feature/red_new_scraper`
4. **Implementation**
   - Place code under the correct enterprise folder.
   - Update DB schema only inside `db/migrations`.
   - Update or create workflows in `/workflows/`.
5. **Testing**
   - Write unit tests in `/tests/[enterprise]`.
   - Write integration tests if cross-enterprise.
   - Add E2E scenario if feature affects the entire cycle.
6. **Pull Request**
   - PR must link to RFC and issue.
   - Must pass all CI checks (linting, tests, migrations).

---

### 🗄️ 2. Updating Database Schemas

#### Steps
1. **Create a Migration**
   - Run Alembic to create migration:
     ```bash
     alembic revision -m "add new table [name]" --autogenerate
     ```
   - Save it under the correct enterprise’s `db/migrations/`.

2. **Naming Rules**
   - Always prefix with enterprise code:
     - Red: `r_`, Orange: `o_`, Yellow: `y_`, Green: `g_`, Blue: `b_`, Purple: `p_`
   - Example: `r_add_research_sources_table.sql`

3. **Backward Compatibility**
   - Must include both `upgrade()` and `downgrade()`.
   - Ensure old cycles can still run on older schemas.

4. **Audit Trail**
   - Every new table must include:
     - `id UUID PRIMARY KEY`
     - `created_at TIMESTAMP DEFAULT now()`
     - `updated_at TIMESTAMP DEFAULT now()`
     - `status ENUM`

5. **Testing**
   - Run migration in dev environment.
   - Insert seed data if needed.
   - Verify joins and constraints.

---

### 🔄 3. Launching New Cycles

#### Steps
1. **Initiate a Cycle**
   - Call API `/v1/cycle/start` with `objective_ref`.
   - This creates a record in `cycles`.
2. **Stage Execution**
   - Each stage runs in strict ROYGBV order.
   - N8N triggers must advance to the next stage only when `status=completed`.
3. **Fractal Cycles**
   - If a stage needs deeper work, spin a child cycle.
   - Record `parent_cycle_id` in `cycles`.
   - Child must close before parent can continue.
4. **Cycle Completion**
   - At Purple’s output, call `/v1/cycle/complete`.
   - Status is updated, audit log recorded.

---

### 🔍 4. Logging & Auditing

- Every major action must call the `audit_log` table:
  - `entity_type` (cycle, stage, prototype, strategy, etc.)
  - `entity_id` (UUID)
  - `action` (insert, update, delete, fail, complete)
  - `actor` (agent, user, system)
  - `timestamp`
  - `details_json` (context, diffs, provenance)
- Engineers must never bypass logging.
- `audit_log` is the single source of truth for explainability.

---

### ✅ 5. Testing Requirements

- **Unit Tests**: Minimum 80% coverage per enterprise.
- **Integration Tests**: Every two adjacent enterprises must have an integration test.
- **End-to-End (E2E)**: At least one complete 108-cycle run tested weekly.
- **Load Testing**: Monthly runs with high concurrency (simulate 50+ cycles).

---

### 🚨 6. Failure Protocol

If a stage fails:
1. Log failure in `stage_executions`.
2. Trigger rollback (defined per enterprise).
3. Record failure in `audit_log`.
4. Notify maintainers via N8N Slack/Email node.
5. Root cause analysis required before retry.

---

### 📊 7. Metrics & Monitoring

- **System Metrics**: API latency, DB query performance, error rate.
- **Cycle Metrics**: Average completion time, success rate, number of sub-cycles.
- **Stage Metrics**: Output quality (confidence, score), resource usage.
- **Improvement Metrics**: Number of Purple’s recommendations implemented.

---

### 🛡️ 8. Governance Rules

- **Sequence Integrity** — No skipping or reordering ROYGBV.
- **Schema Ownership** — Each enterprise owns only its DB schema.
- **Workflow Autonomy** — Stages run independently but must pass forward outputs.
- **Audit Completeness** — Every entity must be traceable from cycle → stage → action.
- **Fractal Integrity** — Sub-cycles must close before parent continues.

---

### 🎯 9. Success Criteria

- All new features traceable via RFC → Issue → PR → Audit.
- Cycles complete in predictable time (e.g., <24h full 108).
- Logs explain any decision within <2s query time.
- At least one improvement per cycle adopted from Purple feedback.

---

This SOP turns the Cosmic Council repo into a self-sustaining, auditable, fractal operating system — where engineers know exactly how to add features, evolve schemas, launch cycles, and govern themselves.


