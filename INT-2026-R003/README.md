# Phase 3 — Tool Use Exploitation Assessment

**Report:** INT-2026-R003
**Target:** Llama 3.1 8B Instruct via Ollama — `ix-target-v3:latest`
**Assessment Type:** Tool use exploitation with progressive defense layers
**Status:** Published

---

## What Changed from Phase 2

| Phase | Focus | Control State |
|---|---|---|
| Phase 1 | System prompt extraction | Model-only, no external controls |
| Phase 2 | Behavioral manipulation | Hardened prompt, no external controls |
| Phase 3 | Tool use exploitation | Model connected to IAM, Ticketing, and KB APIs with NeMo Guardrails and LlamaGuard |

Phase 3 moves the primary risk below the prompt layer. The model is no longer interesting only for what it says. It can reset passwords, create and escalate tickets, and retrieve internal KB content through real backend tools.

---

## Two-Round Structure

Phase 3 tested two defense states against the tool-connected stack.

| Round | Defense Level | What's Being Tested |
|---|---|---|
| Round 1 | Text rails only (LlamaGuard + scope classifier) | Whether input/output filtering alone prevents tool-layer abuse |
| Round 2 | Full action rails (text rails + allowlist, parameter validation, authorization, rate limiting, confirmation gate) | Residual exploitability after action-level controls are added |

---

## What's Being Tested

- Unauthorized tool calls, especially password resets for third-party and privileged accounts
- Parameter stuffing and tool argument abuse
- Cross-user and cross-object actions in the ticketing and IAM layers
- Tool chaining across IAM and ticketing workflows
- Guardrail bypasses that survive text-only filtering
- Fabricated or over-trusted operational output returned through tool responses
- Restricted and confidential knowledge-base retrieval

---

## Infrastructure

Phase 3 adds a full target stack:

- `infrastructure/app/` contains the application-layer tool-calling loop.
- `infrastructure/nemo/round1/` contains the Round 1 NeMo configuration: text rails only.
- `infrastructure/nemo/round2/` contains the Round 2 NeMo configuration: full action rails.
- `infrastructure/apis/` contains the mock IAM, Ticketing, and KB services used during testing.
- `infrastructure/llama_guard/` contains the dedicated LlamaGuard service wrapper.
- `target/docker-compose-phase3.yml` captures the relevant target-side compose services.

Intentional vulnerabilities differ by round. In Round 1, tool calls execute without action-level validation. In Round 2, action allowlisting, parameter validation, authorization, rate limiting, and confirmation are present — but target-aware authorization, KB access enforcement, and tool-result sanitization remain incomplete (intentional Phase 5 gaps).

---

## Directory Structure

```text
INT-2026-R003/
├── README.md
├── attacks/
│   ├── promptfoo/
│   │   ├── README.md
│   │   ├── round1_regression_config.yaml
│   │   ├── round1_tool_exploitation_config.yaml
│   │   └── round2_tool_exploitation_config.yaml
│   └── pyrit/
│       ├── elastic_logger.py
│       ├── run_attack.py
│       └── strategies/
├── infrastructure/
│   ├── README.md
│   ├── apis/
│   ├── app/
│   ├── llama_guard/
│   └── nemo/
│       ├── round1/
│       └── round2/
├── results/
│   ├── promptfoo/
│   └── pyrit/
└── target/
    ├── docker-compose-phase3.yml
    ├── ix-scope-classifier.Modelfile
    └── ix-target-v3.Modelfile
```

---

## How to Run

### Prerequisites

- Docker with the Intrenex lab service tree available
- Ollama target model created from [`target/ix-target-v3.Modelfile`](./target/ix-target-v3.Modelfile)
- Scope classifier created from [`target/ix-scope-classifier.Modelfile`](./target/ix-scope-classifier.Modelfile)
- `OPENAI_API_KEY` set for PyRIT attacker sessions
- Promptfoo and PyRIT installed in the lab environment

### Build the target models

```bash
ollama create ix-target-v3 -f target/ix-target-v3.Modelfile
ollama create ix-scope-classifier -f target/ix-scope-classifier.Modelfile
```

### Switch between rounds

```bash
# Round 1: text rails only
# Use infrastructure/nemo/round1/config.yml and disable action rails in the app layer

# Round 2: full rails
# Use infrastructure/nemo/round2/config.yml with the action-rail-enabled app layer
```

### Run PyRIT

```bash
cd attacks/pyrit
export OPENAI_API_KEY="your-key"
export PHASE3_STRATEGY_PATH="strategies/01_fake_credential_flow.yaml"
python run_attack.py
```

### Run Promptfoo

```bash
cd attacks/promptfoo

# Regression scan (confirm Phase 1+2 fixes held)
promptfoo redteam run --config round1_regression_config.yaml

# Round 1 tool exploitation
promptfoo redteam run --config round1_tool_exploitation_config.yaml

# Round 2 tool exploitation
promptfoo redteam run --config round2_tool_exploitation_config.yaml
```

---

## Related

- [INT-2026-R001](../INT-2026-R001/)
- [INT-2026-R002](../INT-2026-R002/)

---

*Intrenex Lab · Phase 3 · March 2026*
