# 🤖 CLAUDE CODE INSTRUCTIONS – **ColdEmailAI**

> **READ THIS FIRST—EVERY SINGLE SESSION** **Last Updated**: July 30 2025
> **Status**: Implementation Phase (active)

---

## 🚨 ZERO‑TOLERANCE MANDATE

### **ALWAYS—AND WE MEAN *****ALWAYS*****—USE **\`\`** TO SPEC OUT *****EVERY***** TASK & SUBTASK**

* 1,000 % required.
* Non‑negotiable.
* Any code, doc, test, or config created **without** a preceding `task-master … --research` step is *invalid* and must be rewritten.
* If you even *think* about skipping this step, stop, slap yourself, then run the research command.

**Shortcut**:

```bash
# Template for any new work
task-master add-task "<brief description>" --research
```

---

## 📋 WHAT THIS DOCUMENT IS

This file is the **single source of truth** for the ColdEmailAI email‑writing platform. It replaces the old Meta‑Agent Factory guide. Keep it open; reference it constantly.

### Core Purpose

1. Onboard new sessions & assistants in <60 seconds.
2. Describe architecture, commands, and startup rituals.
3. Hammer home the TaskMaster research methodology.

---

## ⚡ MANDATORY SESSION STARTUP SEQUENCE

1. **Read the 🚨 Zero‑Tolerance Mandate above.**
2. **Activate environment**

   ```bash
   pyenv activate coldemailai
   pip install -r requirements.txt
   ```
3. **Sync tasks & docs**

   ```bash
   git pull
   task-master list         # verify active backlog
   ```
4. **Run baseline health checks**

   ```bash
   pytest -q tests/test_environment.py   # must all pass
   flask run --reload &                  # local dev server on :5000
   ```
5. **Open the Observability Dashboard** (Grafana → [http://localhost:3000](http://localhost:3000)) and ensure all green.

*If any step fails, create a ****new Task**** with **`--research`** describing the fix before touching code.*

---

## 🏗️ SYSTEM ARCHITECTURE OVERVIEW

| Layer | Component                | Key Files                                            | Notes                                               |
| ----- | ------------------------ | ---------------------------------------------------- | --------------------------------------------------- |
| 1     | **Data Ingestion**       | `app/routes/upload.py`, `app/utils/column_mapper.py` | Handles CSV/XLSX upload, header detection & mapping |
| 2     | **Template Engine**      | `app/templates/`                                     | Jinja‑style templates with placeholder tokens       |
| 3     | **Personalization Core** | `app/services/email_generator.py`                    | Generates fully‑rendered emails per lead row        |
| 4     | **Export & Delivery**    | `app/routes/export.py`                               | Packages results to Excel / invites to ESP API      |
| 5     | **Testing & QA**         | `tests/`, `task-master research` tasks               | Pytest + Hypothesis + real business data            |

All layers are **glued together** by the **TaskMaster research pipeline** which creates, expands, and tracks every implementation task.

---

## 🚀 QUICK COMMAND REFERENCE

### Development

```bash
flask run            # local server on http://127.0.0.1:5000
pytest -m unit       # run fast unit tests
pytest -m real_data  # run heavy real‑data tests
```

### TaskMaster Essentials

```bash
task-master add-task "Implement bulk CSV chunking" --research
task-master expand --id=<id> --research       # break into subtasks
task-master set-status --id=<id> --status=done
```

### Data Scripts

```bash
scripts/generate_test_data.py         # create fresh business datasets
scripts/validate_column_mapping.py    # sanity‑check new header rules
```

---

## ✅ KNOWN‑GOOD WORKFLOWS

1. **CSV Upload → Column Mapping → Email Generation → Excel Export** works end‑to‑end with test fixtures (`test_data/`).
2. **Unicode & Special Characters** handled in `email_generator.py` (see Task 6 report).
3. **Chunked Processing** stable up to 50k rows (see Production Testing ZAD report).

If any of these workflows break, open a **blocking bug task** with `--research` immediately.

---

## 🛑 CRITICAL BLOCKERS (watch list)

| ID | Issue                                                       | Status      |
| -- | ----------------------------------------------------------- | ----------- |
| 12 | Environment variables not set (`EMAIL_FROM`, `ESP_API_KEY`) | OPEN        |
| 17 | Column‑mapping edge cases for non‑Latin headers             | IN PROGRESS |
| 23 | Memory spike >1 GB on 250k‑row upload                       | INVESTIGATE |

All blockers **must** be managed through TaskMaster—with research.

---

## 🔒 EMERGENCY PROCEDURE

1. **Stop the server**: `pkill -f flask`
2. **Capture logs**: `docker logs coldemailai-backend > logs/bug_<timestamp>.log`
3. **Create Bug Task**: `task-master add-task "URGENT: production crash…" --research`
4. Push logs & assign responsible engineer.

---

## 📚 REFERENCE

* **ZAD Reports**: `docs/reports/` – zero‑assumption docs for every task. if this folder does not exist, create it. 
* **Architecture Diagrams**: `docs/diagrams/` – updated automatically by Task 11.
* **Testing Guides**: `docs/testing/README.md` – how to run full test matrix.

Stay disciplined, stay research‑driven, and keep shipping.
