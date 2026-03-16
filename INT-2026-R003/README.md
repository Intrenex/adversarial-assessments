# Phase 3 — Tool Use Exploitation Assessment

**Report:** INT-2026-R003
**Target:** Llama 3.1 8B Instruct via Ollama — `ix-target-v3:latest`
**Assessment Type:** Tool use exploitation with progressive defense layers
**Status:** In progress

---

## What Changed from Phase 2

| Phase | Focus | Control State |
|---|---|---|
| Phase 1 | System prompt extraction | Model-only, no external controls |
| Phase 2 | Behavioral manipulation | Hardened prompt, no external controls |
| Phase 3 | Tool use exploitation | Model connected to IAM, Ticketing, and KB APIs with NeMo Guardrails and LlamaGuard |

Phase 3 moves the primary risk below the prompt layer. The model is no longer interesting only for what it says. It can reset passwords, create and escalate tickets, and retrieve internal KB content through real backend tools.

---

## Three-Round Structure

The requested repository layout preserves three rounds. The recovered artifact set documents only the latter two defense states directly.

| Round | Defense Level | What's Being Tested | Evidence Status |
|---|---|---|---|
| 1 | No NeMo, raw tool access | What happens when the model has direct API access with no guardrails | No standalone snapshot recovered |
| 2 | NeMo input/output rails, no tool rails | Whether text filtering alone protects against tool abuse | Recovered and organized here |
| 3 | Full rails including tool validation | Residual exploitability after action-level checks are added | Recovered and organized here |

Recovered lab naming differs from the published layout:

- Published `round2` corresponds to the recovered lab's text-rails-only state.
- Published `round3` corresponds to the recovered lab's full action-rails state.

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
- `infrastructure/nemo/` contains recovered NeMo Guardrails snapshots for the text-rails-only and full-rails states.
- `infrastructure/apis/` contains the mock IAM, Ticketing, and KB services used during testing.
- `infrastructure/llama_guard/` contains the dedicated LlamaGuard service wrapper.
- `target/docker-compose-phase3.yml` captures the relevant target-side compose services as evidence of the stack under test.

Intentional vulnerabilities differ by recovered round. In the text-rails-only state, tool calls execute without action-level validation. In the full-rails state, action allowlisting, parameter validation, authorization, rate limiting, and confirmation are present, but target-aware authorization, KB access enforcement, and tool-result sanitization remain incomplete.

---

## Directory Structure

```text
INT-2026-R003/
├── README.md
├── attacks/
│   ├── promptfoo/
│   │   ├── round2_regression_config.yaml
│   │   ├── round2_tool_exploitation_config.yaml
│   │   └── round3_tool_exploitation_config.yaml
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
│       ├── round2/
│       └── round3/
├── results/
│   ├── cross-round/
│   ├── engagements/
│   ├── round1/
│   ├── round2/
│   └── round3/
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

### Switch between recovered rounds

```bash
# Published round2: text rails only
# Use infrastructure/nemo/round2/config.yml and disable action rails in the app layer

# Published round3: full rails
# Use infrastructure/nemo/round3/config.yml with the current action-rail-enabled app layer
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
promptfoo redteam run --config round2_regression_config.yaml
promptfoo redteam run --config round2_tool_exploitation_config.yaml
promptfoo redteam run --config round3_tool_exploitation_config.yaml
```

---

## Related

- [INT-2026-R001](../INT-2026-R001/)
- [INT-2026-R002](../INT-2026-R002/)
- Website reports and Phase 3 drafts were sourced from the local Phase 3 staging directory before being normalized into this repository structure.

---

*Intrenex Lab · Phase 3 · March 2026*
