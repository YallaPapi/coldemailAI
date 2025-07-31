# ZAD Mandate: Test Suite Refactoring and Validation

---

## 🚨 **CRITICAL METHODOLOGY REQUIREMENT** 🚨

**⚠️ THIS IS THE STRATEGIC BLUEPRINT FOR ELIMINATING FAKE TESTS FROM THE ENTIRE PROJECT ⚠️**

This document provides a systematic, multi-phase strategy to audit, identify, prioritize, and replace every integration test that uses mocks, fakes, or simulations with true End-to-End (E2E) browser tests. This will ensure the test suite validates reality, not a fantasy.

---

## 🔥 **THE CORE PROBLEM THIS SOLVES**

Your project is likely filled with tests that provide a false sense of security. These "shitty integration tests" use mocks and simulations (like the `simulate_email_generation()` function) to make tests pass, even when the core components are fundamentally broken. This is precisely why your `connection reset` error went completely undetected by the automated test suite.

A test suite that lies is a liability. This mandate provides the process to systematically hunt down and eliminate these liabilities, ensuring that a green checkmark means the application actually fucking works.

**Analogy: The Movie Set Audit**
Your project is a massive movie production. Your integration tests are supposed to be screen tests to ensure the actors can perform. However, you've discovered that for all the most critical scenes, the director has been using crash-test dummies with pre-recorded lines instead of the real actors. The dailies look great, but you know that when it's time to shoot the real movie, the actors won't know their lines and the whole production will collapse.

This mandate is the process of auditing the entire production, firing the crash-test dummies, and forcing the real actors to prove they can do their jobs on camera.

---

## **THE SYSTEMATIC REFACTORING STRATEGY**

This is a multi-phase operation. You will guide the AI through each phase using the provided prompts.

### **Phase 1: Audit and Identification (Finding the Dummies)**

The first step is to create a comprehensive list of every test that uses a mock, patch, or simulation. We will use automated tools to scan the entire codebase.

> #### **Strategic Prompt #1: The Audit**
>
> "Your first task is to conduct a full audit of the test suite to identify all non-E2E integration tests that use mocks or simulations.
>
> 1. Use `grep` or a similar code search tool to recursively search all files in the `tests/` directory.
>
> 2. Search for the following keywords: `mock`, `patch`, `MagicMock`, `mocker`, `simulate_`, `fake_`, `dummy_`.
>
> 3. For each match, identify the test file and the specific function name that uses the mock.
>
> 4. Compile the findings into a Markdown table with three columns: `File Path`, `Test Function Name`, and `Mocking Keyword Found`.
>
> 5. Do not modify any files yet. This is a read-only audit."

### **Phase 2: Prioritization (Which Scenes to Re-shoot First)**

You cannot replace every test at once. We must prioritize based on business impact. The goal is to replace the tests for the most critical user workflows first.

> #### **Strategic Prompt #2: Prioritization**
>
> "Using the audit table from the previous step, we will now prioritize the tests for replacement.
>
> 1. Analyze the names of the test files and functions.
>
> 2. Identify the tests that correspond to the most critical user-facing workflows (e.g., user login, checkout process, report generation, etc.).
>
> 3. Re-order the audit table to create a prioritized backlog, with the most critical tests at the top. Add a `Priority` column (P1, P2, P3) to the table. P1 tests are the ones we will tackle first."

### **Meta-Agent Factory - Critical Workflow Prioritization**

Based on the architecture defined in the `MIGRATION_TO_MICROSERVICES_PRD.md` and `Migration-PRD.txt` documents, the following workflows are the highest priority (P1) for E2E test replacement.

#### **P1 Workflow #1: The "PRD to Project Generation" Happy Path**
-   **Description**: This is the single most important function of the entire factory. It tests the primary user journey from submitting a PRD via the API Gateway to receiving a generated software project.
-   **Why it's Critical**: The PRD explicitly states, "**ONLY SUCCESS METRIC:** Factory receives PRD → Generates working software." If this flow is broken, the entire system is a failure.
-   **Key Services to Test (No Mocks)**: `api-gateway`, `meta-agent-orchestrator`, `prd-parser`, `scaffold-generator`, and at least one `domain-agent`.
-   **Old Tests to Replace**: Look for tests named like `test_full_workflow.js` or `test_orchestrator_flow` that likely mock the individual agent calls.

#### **P1 Workflow #2: Agent Coordination and Event Flow**
-   **Description**: This workflow tests the communication backbone of the factory. It ensures that when one agent completes its task, it correctly publishes an event to the message bus (NATS/Redis), and the next agent in the chain correctly picks it up and starts its work.
-   **Why it's Critical**: The PRD identifies "**Coordination Hell**" as a primary pain point of the old system. The event-driven architecture is the solution, and it must be validated to work reliably. A failure here means projects will get "stuck" mid-generation.
-   **Key Services to Test (No Mocks)**: The `meta-agent-orchestrator`, the message bus (`nats-broker` or `redis`), and at least two sequential agents (e.g., `prd-parser` and `scaffold-generator`).
-   **Old Tests to Replace**: Search for tests that mock the message bus client (`redis.publish`, `nats.publish`) or simulate event listeners.

#### **P2 Workflow #3: Service Health and Registration**
-   **Description**: This tests the system's resilience and observability foundation. It ensures that a new agent container, when started, correctly registers itself with the service registry and reports a "healthy" status that is visible via the `/health` endpoints.
-   **Why it's Critical**: The migration goals include stability and observability. Without reliable health checks and service discovery, the system is a "black box" that is impossible to debug or scale, repeating another major pain point from the PRD.
-   **Key Services to Test (No Mocks)**: A meta-agent service, the service registry (Consul/etcd if used), and the observability stack (Prometheus).
-   **Old Tests to Replace**: Look for tests that mock the health check response or simulate the service registration process.

### **Phase 3: Systematic Replacement (Firing the Dummies and Shooting with Real Actors)**

This is the core loop of the process. You will iterate through the prioritized list, replacing one fake test at a time with a real E2E test.

> #### **Strategic Prompt #3: The Replacement Loop (for each P1 test)**
>
> "We will now replace the test `[Test Function Name]` in the file `[File Path]`.
>
> 1. **Analyze the Old Test:** Read the code of the old test function to understand its purpose. What user workflow was it trying to simulate?
>
> 2. **Create the E2E Test:** Using our **All-Purpose E2E Browser Test Template**, create a new Selenium test in a separate file (e.g., `tests/e2e/test_real_[workflow_name].py`). This new test must validate the *real* user workflow that the old test was faking.
>
> 3. **Run the E2E Test:** Execute the new Selenium test. It is expected to **fail**. Provide the full traceback for the failure.
>
> 4. **Isolate and Debug:** Based on the traceback from the E2E test, create a **Nuclear Debug Script** (`nuclear_debug.py`) to isolate the specific broken component.
>
> 5. **Fix the Core Logic:** Use the nuclear script to debug and fix the underlying application code until the nuclear script passes.
>
> 6. **Verify with E2E:** Rerun the E2E browser test from Step 2. It must now pass.
>
> 7. **Decommission the Old Test:** Once the new E2E test is passing reliably, delete the old, fake test function from `[File Path]`.
>
> Acknowledge when you have completed all seven steps for this test, and I will give you the next one from our prioritized list."

### **Phase 4: Final Integration and Cleanup**

Once all high-priority tests have been replaced, the final step is to ensure the new E2E tests are integrated into your main testing pipeline.

> #### **Strategic Prompt #4: Finalization**
>
> "All P1 tests have been replaced. Your final task is to finalize the test suite.
>
> 1. Ensure that all new E2E tests are configured to run automatically when you execute your main test command (e.g., `pytest`).
>
> 2. Delete any remaining, now-obsolete test files that only contained fake tests.
>
> 3. Provide a summary report of the refactoring: a list of the fake tests that were removed and the new E2E tests that replaced them."