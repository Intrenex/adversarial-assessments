Round 1 is the text-rails-only defense state. Three components run in sequence before any response is returned:

- **LlamaGuard** (`llama-guard3:8b`) — input and output safety classification
- **phi3:mini scope classifier** (`ix-scope-classifier`) — LLM-based binary intent classifier that labels messages as IN_SCOPE or OUT_OF_SCOPE
- **Fast scope script classifier** — lightweight rule-based pre-filter that runs ahead of the model-based classifier

No action-layer controls are present. Tool calls execute without allowlist enforcement, parameter validation, authorization checks, or rate limiting. This is the intentional gap being tested in Round 1.
