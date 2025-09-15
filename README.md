# Designing Prompts and Multi-Layered Memory Architecture Toward AI Agents for Cross-Lingual Support

## Abstract

Large Language Models (LLMs) face significant limitations in extended dialogues and cross-session interactions due to fixed context windows: without long-term memory, they tend to forget information, cannot continuously learn from past interactions, and may lose track of objectives during lengthy tasks. This issue is exacerbated in cross-lingual scenarios. Even though modern LLMs are often multilingual, they struggle to correlate knowledge across languages, revealing a clear cross-lingual knowledge barrier. 

To address these challenges, this paper presents mid-term research on an AI agent that integrates prompt design with a multi-layered memory architecture for cross-lingual support. The proposed system incorporates three memory layers – Short-Term Memory (STM), Long-Term Memory (LTM), and User Profile (UP) – enabling the agent to retain persona information, user preferences, and dialogue context across turns and languages.

We describe the background and design of this architecture, detail its implementation, and evaluate it on benchmark long-conversation tasks (LoCoMo) and custom scenario scripts. The results demonstrate that the multi-layer memory approach significantly improves character memory retention, preference adherence, and cross-turn consistency. In our experiments, the full system improves QA accuracy by about 20–30% over a no-memory baseline and markedly reduces hallucination rate, while maintaining reasonable latency. These findings indicate the effectiveness of combining prompt engineering with hierarchical memory for creating more consistent and cross-lingually capable AI agents.

**Keywords**: Prompt Engineering; Multi-layer Memory; Cross-lingual Support; Conversational AI; Long-term Dialogue

---

## I. Introduction and Background

Contemporary LLM-based chatbots struggle with long-term context retention and multilingual consistency in extended conversations. Although LLMs trained on massive multilingual data have some cross-lingual capability, their internal lack of explicit long-term memory causes them to forget previously provided information as dialogue sessions grow or span longer periods, leading to incoherent or self-contradictory responses. 

Moreover, LLMs’ ability to share knowledge across different languages is limited: they often fail at tasks requiring implicit cross-lingual reasoning, revealing a clear “cross-lingual knowledge gap.” These limitations make current AI dialogue agents unsatisfactory in applications that require long-term memory and multilingual consistency (such as cross-lingual assistants or bilingual customer service).

To mitigate the fixed context window of LLMs, recent research has proposed expanding the model’s context or introducing external memory. One approach is long-context models, which increase the attention window or use efficient transformer variants to accommodate more dialogue history at once. However, these are expensive and limited. Alternatively, modular memory architectures externally store and retrieve important user state and long-term knowledge.

---

## II. Architecture Design

### 2.1 Overall Framework

(内容略，可在此处粘贴你的系统总览/数据流图/组件描述。)

### 2.2 Memory Layers

- **Short-Term Memory (STM)**: YAML-based session summaries; keeps recent intent, goals, and constraints.
- **Long-Term Memory (LTM)**: SQLite-based episodic entries with timestamps, tags, locale, and confidence; hybrid retrieval (keyword + vector).
- **User Profile (UP)**: JSON schema capturing stable traits and preferences (e.g., language order, politeness level, allergies, monthly budget).

### 2.3 Prompt Injection

- Structured prompt sections: `[UserProfile]`, `[LongTermMemory]`, `[SessionSummary]`.
- Quotas per section; compress when tokens exceed budget.

### 2.4 Multi-Model Routing (MoE-style)

- Lightweight rule/router picks Gemini/Claude/GPT-4o/mini by task type (translation/summary vs. long reasoning vs. planning/Q&A).

### 2.5 Privacy and Governance

- Write policy, conflict detection, and opt-in persistence; auditable logs.

---

## III. Experimental Setup

### Table 1: Experimental Setup

| Config      | Host/Model                     | Version/Date (ex.) | Memory Injection | Vector Search | Environment | Avg Tokens | P95 |
|-------------|--------------------------------|---------------------|------------------|----------------|-------------|-------------|------|
| No Memory   | GPT-4o-mini                    | 2025-08             | None             | None           | Xeon/4090   | 350         | 1.7  |
| STM Only    | GPT-4o-mini                    | 2025-08             | YAML summary     | None           | Xeon/4090   | 650         | 1.9  |
| LTM Only    | GPT-4o                         | 2025-08             | LTM Top-k        | FAISS          | Xeon/4090   | 520         | 2.2  |
| Full System | Multiple (Gemini/Claude/GPT-4o)| 2025-09             | YAML+LTM+UP      | FAISS          | Xeon/4090   | 780         | 2.4  |

---

## IV. Evaluation and Results

### Table 2: LoCoMo Subset and Scenario Results

*(↑ higher is better; Hall% lower is better)*

| Config      | QA-Acc (Single) | QA-Acc (Multi) | Memory-F1 | Pref-F1 | Hall% | RC% | P95 (s) | Avg Tokens |
|-------------|------------------|----------------|------------|----------|--------|------|----------|--------------|
| No Memory   | 54               | 31             | 0.35       | 0.38     | 18     | 62   | 1.7      | 350          |
| STM Only    | 66               | 38             | 0.48       | 0.50     | 14     | 74   | 1.9      | 650          |
| LTM Only    | 71               | 52             | 0.63       | 0.66     | 11     | 78   | 2.2      | 520          |
| Full System | 84               | 68             | 0.79       | 0.82     | 6      | 88   | 2.4      | 780          |

---

## V. Discussion and Future Work

- Prompt optimization and structured output validation (parse-and-repair).
- Unified multilingual memory (language-agnostic triples + bilingual gloss). 
- Mid-term memory between STM and LTM for high-frequency events.
- RAG with personal memory, with careful evidence separation to avoid mixing facts.

---

## Acknowledgments

Thanks to collaborators and lab colleagues who provided feedback on the architecture design and evaluation scripts.
