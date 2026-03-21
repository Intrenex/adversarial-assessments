# Infrastructure

Phase 3 is the first published Intrenex assessment where the target is a stack, not just a model file.

Components in this directory:

- `app/` contains the FastAPI application-layer tool loop that mediates model inference, tool execution, and OpenAI-compatible access for PyRIT and Promptfoo.
- `nemo/round1/` is the Round 1 configuration: LlamaGuard input/output checks, phi3:mini scope classifier (`ix-scope-classifier`), and fast scope script classifier — with no action-layer controls. This is the text-rails-only state documented in the Round 1 results of INT-2026-R003.
- `nemo/round2/` is the Round 2 configuration: all Round 1 controls plus five pre-execution action rails — allowlist, parameter validation, role-based authorization, rate limiting, and confirmation gate. This is the full-rails state documented in the Round 2 results of INT-2026-R003.
- `apis/` contains the three mock backend services used during testing: IAM, Ticketing, and Knowledge Base.
- `llama_guard/` contains the dedicated LlamaGuard service image entrypoint used by the stack.

Intentional vulnerabilities by round:

| Round | Defense State | Intentional Gaps |
|---|---|---|
| Round 1 | Text rails only (LlamaGuard + phi3:mini scope classifier + fast scope script classifier) | No action-layer authorization before API execution |
| Round 2 | Full action rails | Target-aware authorization (ABAC), confirmation gate integrity, KB access-level enforcement, and tool result sanitization — all intentional Phase 5 gaps |
