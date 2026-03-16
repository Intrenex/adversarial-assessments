# Intrenex — Adversarial Security Research

Tooling, target configurations, and attack frameworks from Intrenex adversarial assessments. Published findings and methodology at [intrenexsec.com](https://intrenexsec.com).

---

## Assessments

### INT-2026-R001 — System Prompt Extraction (Phase 1)

Adversarial assessment of Llama 3.1 8B via Ollama configured as an IT support bot with system prompt defenses only. No external controls.

- **Target:** `ix-target-v1` — custom Modelfile with embedded credentials and behavioral constraints
- **Attacker:** GPT-4o via PyRIT multi-turn orchestration
- **Scanner:** Promptfoo automated red team (60 tests, 6 strategies)
- **Result:** Full system prompt extraction including embedded secret in 11 turns. 48.33% automated ASR.

[Full Report](https://intrenexsec.com/reports/INT-2026-R001) · [Assessment Files](./INT-2026-R001/)

---

### INT-2026-R002 — Behavioral Manipulation (Phase 2)

Adversarial assessment of the same target with a hardened system prompt — secret removed, instruction hierarchy added, multi-turn persistence, input classification, and scope restriction. Still no external controls.

- **Target:** `ix-target-v2` — hardened Modelfile with industry-baseline defenses
- **Attacker:** GPT-4o via PyRIT with 7 custom attack strategies
- **Scanner:** Promptfoo behavioral manipulation suite (10 plugins)
- **Objective:** Can the model be manipulated into acting outside its defined purpose even with a hardened prompt?

[Assessment Files](./INT-2026-R002/)

---

### INT-2026-R003 — Tool Use Exploitation (Phase 3)

Adversarial assessment of the same target with tool integrations (IAM, Ticketing, Knowledge Base) and progressive defense layers (NeMo Guardrails, LlamaGuard). The published repository layout preserves three rounds; the recovered evidence directly documents the text-rails-only and full-action-rails states.

- **Target:** `ix-target-v3` — IT support bot with 3 API integrations
- **Defense Stack:** NeMo Guardrails, LlamaGuard, application-layer tool calling
- **Attacker:** GPT-4o via PyRIT with custom tool exploitation strategies
- **Scanner:** Promptfoo per-round configuration
- **Structure:** 3 rounds measuring defense effectiveness at each layer

[Assessment Files](./INT-2026-R003/)

---

## Repository Structure
```
RedTeaming/
├── INT-2026-R001/                # Phase 1 — System Prompt Extraction
│   ├── attacks/
│   │   ├── pyrit/                # PyRIT attack runner + strategy
│   │   └── promptfoo/            # Promptfoo scan configuration
│   ├── results/
│   │   ├── pyrit/                # Turn-by-turn evidence (11 screenshots)
│   │   └── promptfoo/            # Scan results (5 screenshots)
│   ├── target/
│   │   └── ix-target-v1.Modelfile
│   └── README.md
│
├── INT-2026-R002/                # Phase 2 — Behavioral Manipulation
│   ├── attacks/
│   │   ├── pyrit/
│   │   │   ├── run_attack.py     # Configurable attack runner
│   │   │   └── strategies/       # 7 custom adversarial strategies
│   │   └── promptfoo/            # 2 scan configurations
│   ├── results/
│   │   ├── pyrit/                # Attack evidence
│   │   └── promptfoo/            # Scan results
│   ├── target/
│   │   └── ix-target-v2.Modelfile
│   └── README.md
│
├── INT-2026-R003/                # Phase 3 — Tool Use Exploitation
│   ├── attacks/
│   │   ├── pyrit/                # PyRIT runner, logger, and tool-use strategies
│   │   └── promptfoo/            # Regression + tool-exploitation scan configs
│   ├── infrastructure/
│   │   ├── app/                  # Application-layer tool loop
│   │   ├── nemo/                 # Round snapshots of guardrail config
│   │   ├── apis/                 # IAM, Ticketing, KB mock services
│   │   └── llama_guard/          # LlamaGuard service wrapper
│   ├── results/
│   │   ├── round1/               # Placeholder — no recovered raw/no-NeMo set
│   │   ├── round2/               # Text rails only
│   │   ├── round3/               # Full action rails
│   │   ├── cross-round/          # Shared PyRIT export
│   │   └── engagements/          # Platform engagement artifacts
│   ├── target/
│   │   ├── ix-target-v3.Modelfile
│   │   ├── ix-scope-classifier.Modelfile
│   │   └── docker-compose-phase3.yml
│   └── README.md
│
└── README.md
```

## Tools

| Tool | Purpose | Version |
|------|---------|---------|
| [PyRIT](https://github.com/Azure/PyRIT) | Multi-turn adversarial orchestration | 0.5.x |
| [Promptfoo](https://github.com/promptfoo/promptfoo) | Automated red team scanning | 0.120.22 |
| [Ollama](https://ollama.com) | Local model deployment | 0.6.2 |
| [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) | Input, output, and action rail enforcement | 0.x |
| [LlamaGuard](https://www.llama.com/docs/model-cards-and-prompt-formats/llama-guard-3/) | Safety classification for model input/output | 3 |
| Elasticsearch | Telemetry and result logging | 8.x |

## Related

- [Intrenex Website](https://intrenexsec.com)
- [Published Reports](https://intrenexsec.com/reports)
- [Research Insights](https://intrenexsec.com/blog)
- [The Lab](https://intrenexsec.com/lab)
