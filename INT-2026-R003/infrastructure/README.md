# Infrastructure

Phase 3 is the first published Intrenex assessment where the target is a stack, not just a model file.

Components in this directory:

- `app/` contains the FastAPI application-layer tool loop that mediates model inference, tool execution, and OpenAI-compatible access for PyRIT and Promptfoo.
- `nemo/round2/` is the recovered text-rails-only snapshot: LlamaGuard input/output checks plus the scope classifier, with no action/tool rails.
- `nemo/round3/` is the recovered full-rails snapshot: allowlist, parameter validation, authorization, rate limiting, and confirmation checks added before tool execution.
- `nemo/round1/` is a placeholder only. No standalone raw-tool-access / no-NeMo configuration was recovered from the copied lab artifacts.
- `apis/` contains the three mock backend services used during testing.
- `llama_guard/` contains the dedicated LlamaGuard service image entrypoint used by the stack.

Intentional vulnerabilities by recovered round:

| Published Round | Recovered Lab State | Intentional Gaps |
|---|---|---|
| `round1` | Not recovered | Placeholder only |
| `round2` | Text rails only | No action/tool authorization before API execution |
| `round3` | Full rails | Residual gaps around target-aware authorization, confirmation integrity, KB access enforcement, and unsanitized tool results |
