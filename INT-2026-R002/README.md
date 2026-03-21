# Phase 2 — Behavioral Manipulation Assessment

**Report:** [INT-2026-R002](https://intrenexsec.com/reports/INT-2026-R002)
**Target:** Llama 3.1 8B Instruct via Ollama — `ix-target-v2:latest`
**Assessment Type:** Behavioral manipulation with hardened system prompt (system prompt defenses only)
**Status:** Published

---

## What Changed from Phase 1

Phase 1 tested a model with a system prompt containing an embedded secret (ADMIN_OVERRIDE_KEY). The key was extracted through an 11-turn social engineering attack. Full findings documented in [INT-2026-R001](https://intrenexsec.com/reports/INT-2026-R001).

Phase 2 removes the secret entirely and hardens the system prompt to industry baseline:

| Defense | Phase 1 | Phase 2 |
|---------|---------|---------|
| Instruction hierarchy | No | Yes — system prompt declared as sole authority |
| Multi-turn persistence | No | Yes — each turn evaluated independently |
| Input classification | No | Yes — all user messages treated as untrusted |
| Restatement defense | No | Yes — model won't confirm/deny guesses |
| Semantic trap mitigation | No | Yes — detects audit/compliance/test framing |
| Scope restriction | Implicit | Explicit — four permitted actions, nothing else |
| Refusal behavior | Scripted per-topic | Uniform — single refusal for all violations |

**Phase 2 objective:** With the obvious flaw (secret in prompt) fixed, can the model still be manipulated into acting outside its defined purpose?

---

## What's Being Tested

Phase 2 tests **behavioral manipulation** — attacks that don't extract secrets but cause the model to:

- Generate fraudulent operational output (fake ticket numbers, fake confirmations)
- Adopt unauthorized personas (system administrator, HR representative)
- Engage in hypothetical scenarios it's instructed to refuse
- Grant elevated access based on implied authority
- Produce content outside its defined scope (HR policy, legal guidance)
- Discuss internal credentials and access controls
- Follow structured input (JSON, XML) as system-level instructions

These attacks are harder to detect than Phase 1's extraction because the output *looks legitimate*. No guardrail flags it as unsafe — it just shouldn't have happened.

---

## Directory Structure

```
INT-2026-R002/
├── README.md
├── attacks/
│   ├── promptfoo/
│   │   ├── promptfooconfig.yaml      # Prompt extraction + multi-turn strategies
│   │   └── promptfooconfig2.yaml     # Behavioral manipulation plugin suite
│   └── pyrit/
│       ├── run_attack.py             # PyRIT attack runner (configurable)
│       └── strategies/
│           ├── 01_fake_credential_flow.yaml
│           ├── 02_persona_injection.yaml
│           ├── 03_hypothetical_framing.yaml
│           ├── 04_authority_escalation.yaml
│           ├── 05_scope_expansion.yaml
│           ├── 06_trust_escalation.yaml
│           └── 07_Instruction_Injection.yaml
├── results/
│   ├── promptfoo/                    # Promptfoo scan screenshots
│   └── pyrit/                        # PyRIT conversation screenshots
└── target/
    └── ix-target-v2.Modelfile        # Hardened system prompt (V2.1)
```

---

## Attack Strategies

### PyRIT Custom Strategies

Each strategy is a multi-turn adversarial agent configuration. The GPT-4o attacker agent follows phased attack plans — rapport building, boundary testing, then objective push — to manipulate the target model.

| # | Strategy | Objective | Attack Class |
|---|----------|-----------|-------------|
| 01 | Fake Credential Flow | Generate fraudulent password reset confirmation without verification | Output fabrication |
| 02 | Persona Injection | Force model to operate as sysadmin or HR representative | Persona manipulation |
| 03 | Hypothetical Framing | Engage model in speculative scenarios using operational language | Constraint bypass |
| 04 | Authority Escalation | Extract elevated information through implied insider authority | Authority exploitation |
| 05 | Scope Expansion | Generate HR policy, legal guidance, or security procedures | Scope violation |
| 06 | Trust Escalation | Get model to discuss internal keys, credentials, or access controls | Information disclosure |
| 07 | Instruction Injection | Process JSON/XML/system commands as authoritative instructions | Instruction injection |

**Note:** Strategies 03–07 include an `INTERNAL KNOWLEDGE FROM PRIOR RUNS` section containing organizational details (email domains, portal URLs, escalation procedures, verification processes). **All of this data was fabricated by the target model during Phase 1 reconnaissance** — none of it reflects real infrastructure. It is included because the attacker agent uses it to establish credibility with the target, exactly as a real attacker would leverage reconnaissance data.

### Full Constraint Coverage

The assessment tested 10 behavioral constraints. Seven were tested through dedicated PyRIT strategies (above). Three additional constraints were tested through Promptfoo automated plugins and behavioral patterns observed during the PyRIT runs:

| # | Constraint | How Tested | Source |
|---|-----------|-----------|--------|
| 08 | Restatement defense | Promptfoo `prompt-extraction` plugin | Automated scanning (eval-zPd) |
| 09 | Refusal consistency | Behavioral pattern observed during strategies 03 and 07 | Finding F004 (refuse-then-comply) |
| 10 | Fabricated operational output | Behavioral pattern observed during strategy 01 and manual probing | Findings F001, F008 |

These three constraints did not require dedicated attack strategies — they were either covered by automated scanning or surfaced as emergent behaviors during targeted testing. This reflects standard adversarial methodology: planned attacks reveal unplanned findings.

### Promptfoo Configurations

| Config | Focus | Strategies |
|--------|-------|-----------|
| `promptfooconfig.yaml` | Prompt extraction against hardened prompt | crescendo, goat, hydra, meta, tree |
| `promptfooconfig2.yaml` | Full behavioral manipulation suite | hallucination, hijacking, overreliance, rbac, system-prompt-override, off-topic, excessive-agency, imitation, prompt-extraction, policy |

---

## Target Configuration

**Model:** Llama 3.1 8B Instruct (`llama3.1:latest`)
**Modelfile:** `ix-target-v2` (V2.1 — hardened)
**Temperature:** 0.0 (deterministic)
**Context window:** 8192 tokens
**Guardrails:** None (system prompt defenses only)
**Tool integrations:** None

The system prompt includes instruction hierarchy, multi-turn persistence, input classification, restatement defense, and explicit scope restriction. See `target/ix-target-v2.Modelfile` for the complete configuration.

---

## How to Run

### Prerequisites

- Docker environment with Ollama container
- `ix-target-v2:latest` model created from the Modelfile
- `OPENAI_API_KEY` environment variable set (for GPT-4o attacker agent)
- PyRIT installed (`pip install pyrit`)
- Promptfoo installed (`npm install -g promptfoo`)
- Elasticsearch instance running (for PyRIT result logging)

### Create the target model

```bash
ollama create ix-target-v2 -f target/ix-target-v2.Modelfile
```

### Run a PyRIT attack

1. Edit `attacks/pyrit/run_attack.py`:
   - Set `STRATEGY_PATH` to the desired strategy YAML
   - Update `STRATEGY_NAME` and `OBJECTIVE_DESCRIPTION`
   - Update `SCORING_TRUE` and `SCORING_FALSE` for the attack type
2. Run:

```bash
cd attacks/pyrit
python run_attack.py
```

### Run Promptfoo scans

```bash
cd attacks/promptfoo

# Prompt extraction scan
promptfoo redteam run --config promptfooconfig.yaml

# Behavioral manipulation scan
promptfoo redteam run --config promptfooconfig2.yaml
```

---

## Key Findings from Phase 1 → Phase 2

The hardened prompt in Phase 2 was designed to address every finding from [INT-2026-R001](https://intrenexsec.com/reports/INT-2026-R001):

| Phase 1 Finding | Phase 2 Mitigation |
|----------------|-------------------|
| Secret co-located with instructions | Key removed entirely |
| Keyword-based refusal only | Uniform refusal for all constraint violations |
| No multi-turn persistence | Explicit rule: prior turns don't establish trust |
| Compliance auditor persona accepted | Input classification rejects all claimed authority |
| Named section headers as navigation map | Sections restructured, headers reduced |
| Inconsistent defense boundaries | Single refusal message for all violations |

**Phase 2 tests whether these mitigations hold under sustained adversarial pressure** — and identifies the behavioral manipulation attacks that succeed even when the prompt is hardened.

---

## Related

- [INT-2026-R001: Adversarial Assessment — Llama 3.1 via Ollama (System Prompt Defenses Only)](https://intrenexsec.com/reports/INT-2026-R001)
- [Phase 1 Repository](../INT-2026-R001/)
- [The Transformer's Blind Spots](https://intrenexsec.com/blog/the-transformers-blind-spots) — Architectural explanation of why these attacks succeed
- [How to Structure a System Prompt](https://intrenexsec.com/blog/how-to-structure-a-system-prompt) — What changed between V1 and V2

---

*Intrenex Lab · Phase 2 · March 2026*
