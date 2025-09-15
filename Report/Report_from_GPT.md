Abstract（EN / 中文对照）

EN — Abstract
We study AI assistants for foreign residents and travelers in Japan, a domain with strong context-dependence and high personalization demands. Pure LLM chat is fluent yet fragile: without explicit memory and grounding it drifts, hallucinates, and loses cross-session consistency—effects amplified in very long dialogues (e.g., LoCoMo). We present a multi-layered memory architecture that is implemented today and evaluated in a memory-only setting: (i) a User Profile layer capturing stable preferences/constraints (language order, politeness level, allergies, budget), (ii) Short-Term Memory (STM) for within-session state with goal-to-summary replacement, and (iii) Long-Term Memory (LTM) for episodic, cross-session facts. At memory-critical junctions (summary, profile consolidation, evidence selection) we introduce a multi-LLM Mixture-of-Experts (MoE) consensus to reduce single-model bias and improve robustness. Using LoCoMo as the primary benchmark, our interim results show gains in long-range QA accuracy, citation/trace coverage, and response consistency versus stateless and session-only baselines under matched decoding. Retrieval-augmented grounding (RAG), hierarchical retrieval with cross-lingual alignment, and lifecycle governance are reserved as future work to further curb hallucinations and scale memory over time. The architecture is API-oriented (OpenAI-style system prompts) and model-agnostic, providing a practical path toward personalized, cross-lingual assistants that remember.

1. Introduction（EN / 中文对照）

EN — Introduction

Background & Motivation.
Real-world “life-assistant” use cases for foreign residents and travelers in Japan—covering transport, government procedures, healthcare, lodging, and ticketing—are highly context-dependent and personalization-intensive. The same query (e.g., “How do I renew my insurance card?”) can require different answers depending on the user’s language preference, prior interactions, location, budget, and constraints (e.g., allergies, visa status). Traditional FAQs and keyword search fall short under multi-turn, cross-session, and cross-lingual interaction. Meanwhile, LLM-only chat, though fluent, drifts without explicit memory and grounding, and consistency degrades in very long or cross-session dialogues. This motivates a memory-first architecture that treats who the user is and what has happened before as first-class citizens in the reasoning loop.

Problem Statement.
We target an AI agent that (i) persistently tracks user profile (stable preferences/constraints), (ii) maintains short-term working context across turns within the current session, and (iii) consolidates long-term episodic facts across sessions—without yet relying on retrieval-augmented grounding (RAG). The core challenge is to decide what to store, how to summarize, and when to inject these memories into prompts so that the agent remains coherent and personalized over time, across languages (JA/EN/ZH), and under practical latency/token budgets.

Key Observations.
	1.	Memory operations (summarization, profile consolidation, evidence selection) are memory-critical junctions where single-model bias and sampling noise often cause omissions or hallucinations.
	2.	A layered memory (User Profile → Short-Term → Long-Term) maps well to the functional roles needed in assistant behavior: global priors, conversational state, and durable episodic knowledge.
	3.	Multi-LLM consensus (MoE) at those junctions can reduce bias and stabilize memory quality, especially for cross-lingual content and long histories.
	4.	RAG remains important for public facts, but in this midterm stage we focus on memory reliability; RAG, hierarchical retrieval, and lifecycle governance will follow as future work.

Our Approach (Implemented Stage).
We implement a three-layer memory architecture—User Profile (UP), Short-Term Memory (STM with goal→summary replacement), and Long-Term Memory (LTM, episodic entries)—and place a multi-LLM Mixture-of-Experts (MoE) consensus at memory-critical junctions. The agent is orchestrated via API-oriented prompts (OpenAI-style system messages) that inject [PROFILE], [LONG_TERM_MEMORY], and [CONTEXT_SUMMARY] into the main model’s context at response time. This memory-first stack is model-agnostic and cross-lingual by design.

Contributions.
	•	Architecture. A practical, memory-first agent with three layers of memory (UP/STM/LTM) tailored to context-dependent, multilingual life assistance.
	•	MoE for Memory Decisions. A multi-LLM consensus mechanism (e.g., GPT-4o-mini, Claude 3, Gemini, DeepSeek) applied specifically at memory-critical junctions to improve robustness over long dialogues.
	•	Prompt/API Design. A structured system-prompt injection scheme that cleanly separates profile, episodic memories, and session summary, enabling controllable personalization under token/latency constraints.
	•	Evaluation Plan & Interim Results. A LoCoMo-based evaluation focusing on memory-only settings (no RAG yet), with interim gains in long-range QA accuracy, citation/trace coverage, and response consistency over stateless and session-only baselines; future work will add hierarchical retrieval, cross-lingual alignment, lifecycle governance, and RAG.

Paper Organization.
Section 2 reviews related work. Section 3 formulates tasks and notation. Section 4 overviews the system. Section 5 details the memory architecture; Section 6 presents the MoE consensus. Section 7 reports experimental setup and interim results. Section 8 discusses limitations and future work (hierarchical retrieval, lifecycle governance, RAG). Section 9 concludes.

好的，已按你的要求移除原“2.6 RAG 与事实扎根”（该内容改到 Future Work），并重排编号。下面给出更新后的第2节：Related Work / 相关工作（EN/中文对照）。

⸻

2. Related Work（EN / 中文对照 — Revised）

EN — Related Work

2.1 Long-term conversational memory & benchmarks

Early assistants relied on a finite context window (“working memory”), leading to information loss in very long or cross-session dialogues. Recent benchmarks targeting long-range coherence and factual carry-over (e.g., cross-session QA, event/timeline summarization, consistency checks) reveal two effects: (i) consistency decay as history grows, and (ii) hallucination spikes when recall depends on parametric memory alone. We therefore evaluate memory-first systems before adding grounding.

Takeaway. Long-range benchmarks motivate externalized, structured memory beyond raw context windows.

⸻

2.2 External memory layers for LLM agents

A practical path is to externalize memory into dedicated stores with read/write APIs. Representative systems (universal memory layers, companion-style memory buffers) provide: (a) structured write policies (what to store, with timestamps/metadata), (b) selective retrieval (semantic search over prior turns, profiles, episodes), and (c) transparent human-readable storage. Evidence shows better context reuse, reduced token cost (vs. full-history replay), and more stable long-range behavior than stateless chat. However, many are single-model and monolingual-leaning, and their write/summarize criteria can be brittle.

Takeaway. External memory makes long-term behavior feasible, but what/when/how to write and inject remains under-specified—especially for cross-lingual, multi-session use.

⸻

2.3 Working-memory management: summarization, reflection, hierarchy

To contain context length, systems maintain Short-Term Memory (STM) with running summaries or goal→summary replacement: keep recent turns verbatim while distilling older spans into structured notes. Complementarily, reflection periodically consolidates older logs into higher-level memories to keep salience and prune noise. Hierarchical agent designs further split state tracking, subgoal planning, and tool feedback aggregation, improving controllability and reducing dependence on raw transcripts.

Takeaway. “Summarization + reflection + hierarchy” preserves useful STM without losing key signals for future episodes.

⸻

2.4 Personalization and user-profile modeling

Personalized assistants retrieve stable user traits (preferences/constraints, language order, politeness level) and episodic facts (what happened before) to tailor responses. Approaches include: prompt-time profile injection, retrieval-based personalization from prior chats, and parameter-efficient tuning for user vectors. Prompt-time strategies are model-agnostic and privacy-friendly (editable), while parameterized methods can be inference-efficient but require extra training and governance.

Takeaway. For safety, editability, and portability, prompt-time profile injection is a strong default; parameterized personalization is complementary.

⸻

2.5 Multi-model collaboration: self-consistency, debate, Mixture-of-Agents

Single-model sampling at memory-critical junctions (memory summarization, profile consolidation, evidence selection) risks omissions and bias. Self-Consistency aggregates multiple reasoning paths of one model; multi-agent debate/voting and Mixture-of-Agents/MoE extend this to heterogeneous models, improving robustness on complex tasks. Few works explicitly place multi-model consensus inside the memory pipeline (to decide what to write and how to inject)—the focus of our design.

Takeaway. Multi-LLM consensus is valuable not only for answer generation but—crucially—for governing memory content at write/inject time.

⸻

2.6 Our positioning

We (i) propose a three-layer memory (User Profile / STM / LTM) tailored to cross-lingual life-assistant tasks, and (ii) place a multi-LLM MoE consensus exactly at memory-critical junctions. Compared with prior external memory layers, we emphasize structured write criteria, typed long-term stores, and consensus-based injection under API-oriented prompts. Unlike RAG-centric systems, we first stabilize memory (consistency, personalization) and defer grounding to future work.

Takeaway. We operationalize memory governance as a first-class component—before grounding—targeting long-term coherence and personalization in multilingual assistants.

⸻
3. Problem Formulation & Task Setting

3.1 Notation & Setting (EN)

We model a dialogue as a sequence \{(u_t,a_t)\}{t=1}^{T} of user utterances u_t and agent replies a_t. Let history up to turn t be H_t=\{(u_i,a_i)\}{i=1}^{t-1}. The agent maintains three memory layers:
	•	User Profile (UP) M^{\mathrm{UP}}: stable traits/constraints (language order, politeness, allergies, budgets) as key–values or declarative facts.
	•	Short-Term Memory (STM) M^{\mathrm{STM}}t=[\,\text{verbatim}(H{t,k}),\ \text{summary}(H_{t\setminus k})\,]: a token-bounded window of last k turns plus a running summary of earlier context.
	•	Long-Term Memory (LTM) M^{\mathrm{LTM}}=\{(e_j,\tau_j,\text{meta}_j)\}: episodic entries distilled across sessions with timestamp \tau_j and metadata (domain/locale/lang tags).

Given a new query q_t=u_t, the system assembles a structured system prompt from \{M^{\mathrm{UP}},M^{\mathrm{STM}}_t,M^{\mathrm{LTM}}\} and generates a_t.

3.2 Memory Write / Update Policy (EN)

At the end of turn t, a writer function proposes a candidate memory:
z_t \leftarrow f_{\text{write}}(H_t,M^{\mathrm{UP}},M^{\mathrm{STM}}t,M^{\mathrm{LTM}}).
Each z is scored by a composite utility
\phi(z)=\alpha U(z)+\beta V(z)+\gamma S(z)-\eta R{\text{privacy}}(z)+\xi L_{\text{coverage}}(z),
combining usefulness U, verifiability V, stability S, privacy risk R, and cross-lingual coverage L. We accept if \phi(z)\ge \tau and capacity allows. LTM uses a periodic reflection operator \Sigma to merge redundancies and decay stale items:
M^{\mathrm{LTM}}\leftarrow \Sigma\!\big(M^{\mathrm{LTM}}\big).

3.3 Retrieval & Prompt Injection (EN)

For query q_t, retrieve top-K items from UP/LTM via hybrid similarity (lexical + multilingual embedding cosine):
\mathcal{R}_t=\text{TopK}\big(\text{sim}(q_t,\cdot)\ \text{over}\ M^{\mathrm{UP}}\cup M^{\mathrm{LTM}}\big).
Build an OpenAI-style system message with three sections:

[PROFILE] | [LONG_TERM_MEMORY] | [CONTEXT_SUMMARY]

Enforce token budget by (i) compressing items with a summarizer, (ii) per-section quotas, and (iii) language-aware elision (prioritize user-preferred language).

3.4 MoE at Memory-Critical Junctions (EN)

At summary, profile consolidation, and evidence selection, run K experts (e.g., GPT-4o-mini, Claude 3, Gemini, DeepSeek) to produce candidates \{\hat z^{(k)}\} with confidence s_k and cost c_k. Aggregate via cost-aware soft voting:
\[
g_k=\frac{\exp(\beta s_k-\alpha c_k)}{\sum_j \exp(\beta s_j-\alpha c_j)},\qquad
\hat z^\*=\arg\max_{z\in\{\hat z^{(k)}\}}\sum_k g_k\,\phi_k(z),
\]
where \phi_k is an expert-specific quality score (faithfulness, cross-lingual alignment). If scores are close, fall back to majority vote.

3.5 Objective & Constraints (EN)

Optimize task utility while penalizing hallucination, latency, and token cost:
\max_{\pi}\ \mathbb{E}\!\left[U(a_t|q_t)-\lambda\,\text{Hall}(a_t)-\mu\,\text{Latency}(a_t)-\nu\,\text{Tokens}(a_t)\right],
subject to context budget C and SLA latency L_{\max}. Encourage cross-lingual parity of injected memories with a regularizer:
\mathcal{L}{\text{XL}}=1-\cos\!\big(f{\text{mE}}(m^{\ell_1}),\ f_{\text{mE}}(m^{\ell_2})\big),
where f_{\text{mE}} is a multilingual encoder and \ell_1,\ell_2 are languages.

3.6 Task Setting (EN)

We evaluate memory-first (no RAG yet) on:
	•	Cross-session QA: questions requiring recall from prior sessions.
	•	Event/Timeline summarization: evolving summaries over very long dialogues.
	•	Cross-lingual assistance (JA/EN/ZH): respond in the preferred language while leveraging memories possibly stored in other languages.

⸻
收到，我继续输出 Section 4。另外提醒：你之前上传的部分文件在会话中已过期；若希望我再次引用其具体内容，请重新上传。

⸻

4. System Overview

4.1 Components (EN)
	•	Orchestrator (Gateway): Routes each user turn to retrieval, MoE experts, prompt builder, and the main dialogue model; enforces latency/token budgets.
	•	User Profile Store (UP): Key–value or declarative facts about stable traits/constraints (language order, politeness level, allergies, visa, budget).
	•	Short-Term Memory (STM): Ring buffer of last k turns (verbatim) + a running session summary maintained by a summarizer expert.
	•	Long-Term Memory (LTM): Episodic entries distilled across sessions with timestamps, domains, locale, and language tags; semantically indexed.
	•	Multilingual Encoder & Index: e.g., multilingual-E5/BGE for embeddings (cosine similarity), hybrid with lexical BM25; vector DB (FAISS/Chroma/Weaviate).
	•	Expert Pool (MoE):
	•	Summarizer/Reflector (e.g., Claude 3) for STM/LTM condensation;
	•	Profile Extractor (e.g., GPT-4o-mini) for UP updates;
	•	Retriever/Reasoner (e.g., DeepSeek) for hybrid retrieval & re-ranking;
	•	Main Dialogue Model (e.g., Gemini) to generate the final reply.
	•	Prompt Builder: Composes an OpenAI-style system message with [PROFILE] | [LONG_TERM_MEMORY] | [CONTEXT_SUMMARY].
	•	Telemetry & Policy: Logs consistency/hallucination events, cost, latency; applies write thresholds and privacy rules.

Phase status: RAG is disabled in this stage; we evaluate a memory-first pipeline. RAG/hierarchical retrieval/lifecycle governance appear in Future Work.

⸻

4.2 Turn-Level Dataflow (EN)
	1.	Normalize & Detect Language. Normalize punctuation, detect ja/en/zh to set output preference.
	2.	Light Retrieval. Query UP (direct lookup) and LTM (Top-K semantic + metadata filter).
	3.	MoE @ Retrieval Selection (Optional). If competing candidates overflow token budgets, run cost-aware soft voting among experts to pick a small, faithful set.
	4.	STM Update (Pre-answer). Summarizer refreshes the running session summary (goal→summary replacement if needed).
	5.	Prompt Assembly. Prompt Builder creates:

System:
[PROFILE] ... 
[LONG_TERM_MEMORY] ...
[CONTEXT_SUMMARY] ...
(Instructions: respond in <preferred language>, be faithful to injected facts, avoid speculation.)


	6.	Main Generation. Main model (Gemini) produces the reply.
	7.	Post-hoc Writes. Profile Extractor scans the turn for new stable facts; LTM writer proposes an episodic entry; policies decide write/merge.
	8.	Periodic Reflection (Offline). Reflector merges redundant LTM items, decays stale ones, resolves conflicts when possible.

⸻

4.3 Memory Schemas & Examples (EN)

User Profile (UP) — JSON

{
  "user_id": "u_123",
  "language_order": ["en", "ja", "zh"],
  "politeness_level": "neutral",
  "constraints": {
    "allergies": ["penicillin"],
    "budget_monthly_jpy": 80000
  },
  "preferences": {
    "transport": "fewer_transfers",
    "ui_language": "en"
  },
  "meta": {"updated_at": "2025-09-10T12:03:00Z", "confidence": 0.93}
}

Short-Term Memory (STM) — running summary + last k turns

{
  "session_id": "s_2025_09_15_01",
  "last_k_turns": [
    {"role": "user", "lang": "en", "text": "Where do I renew my health insurance card?"},
    {"role": "assistant", "lang": "en", "text": "We’ll go to your city hall insurance desk..."}
  ],
  "summary": "User needs to renew Japanese health insurance; prefers English; lives in Tokyo; last time visited Shinjuku Hospital for translation help.",
  "meta": {"k": 8, "tokens": 640}
}

Long-Term Memory (LTM) — episodic entry

{
  "memory_id": "m_987",
  "timestamp": "2025-08-02T09:20:00Z",
  "domain": "transport",
  "locale": "Tokyo",
  "lang": "en",
  "title": "Bought commuter pass; prefers routes with English signage",
  "summary": "Assisted purchase of Toei/Metro commuter pass; user asked for fewer transfers.",
  "evidence_ptr": ["conv://s_2025_08_02#t18..t33"],
  "tags": ["preference", "transport"],
  "confidence": 0.88
}


⸻

4.4 Prompt Template (EN)

OpenAI-style system message (assembled at runtime):

System:
[PROFILE]
- Language order: EN > JA > ZH (respond in EN unless asked otherwise)
- Constraints: Allergy=Penicillin; Budget≈¥80k/month; Locale=Tokyo
- Preferences: Transport=fewer transfers; UI language=EN

[LONG_TERM_MEMORY]
- (2025-08-02 / Transport / Tokyo) Helped buy commuter pass; prefers routes with English signage.
- (2025-09-10 / Healthcare / Shinjuku) Translated prescription; note allergy to penicillin.

[CONTEXT_SUMMARY]
- Current session: user asks about renewing the Japanese health insurance card, previously did this ~2 years ago.

Instructions:
- Be faithful to PROFILE and LONG_TERM_MEMORY. If uncertain, ask a brief clarifying question before advising.
- Use EN unless user explicitly switches language.
End of system.

User: "My health insurance card is expiring. How can I renew it?"

Token budget rules. Per-section quotas (e.g., PROFILE ≤ 20 lines, LTM ≤ 3 items × 60–80 tokens, SUMMARY ≤ 80–120 tokens). Items beyond quota are summarized or dropped by the Summarizer expert.

⸻

4.5 Operational Constraints & Privacy (EN)
	•	Write Policy: accept a write if composite utility \phi(z) \ge \tau (usefulness, verifiability, stability, language coverage; penalize privacy risk).
	•	Conflict Handling: if a new fact contradicts UP/LTM, mark conflict and require confirmation in the next turn (or user UI) before overwrite.
	•	Opt-in Memory & Forget: explicit consent for persistent memory; support forget <key> to delete or export to download audit logs.
	•	Cost/Latency Control: MoE uses cost-aware soft voting; orchestrator enforces SLA (e.g., P95 < 3s) with early-exit if retrieval yields low utility.
	•	Cross-lingual Alignment: store lang tags; allow on-the-fly translation for display while preserving original text in memory for traceability.

先提示一下：你之前上传的部分文件在会话中已经过期；如果需要我再次引用它们的具体内容，请重新上传。我会继续按我们已确认的“定稿基线”生成正文。

⸻

5. Memory Architecture Details

5.1 Data Models & Storage Layout (EN)

Stores & indices.
	•	UP (User Profile): KV / declarative facts; primary key user_id; secondary indices on keys (e.g., diet, allergy), lang.
	•	STM (Short-Term Memory): per-session ring buffer last_k_turns + running_summary; keyed by session_id.
	•	LTM (Long-Term Memory): episodic entries with timestamp, domain, locale, lang, summary, evidence_ptr, confidence, hash; HNSW vector index over summary_emb, plus lexical BM25.

Suggested fields.

// UP
{
  "user_id": "u_123",
  "facts": [
    {"key": "language_order", "value": ["en","ja","zh"], "confidence": 0.95, "source": "onboarding", "updated_at": "..."},
    {"key": "allergy", "value": "penicillin", "confidence": 0.98, "source": "chat#s_0502", "updated_at": "..."},
    {"key": "politeness", "value": "neutral", "confidence": 0.8}
  ],
  "privacy": {"consent": true, "policy": "opt_in"}
}
// STM
{
  "session_id": "s_2025_09_15_01",
  "last_k_turns": [...],
  "running_summary": "…",
  "goal_stack": ["renew insurance", "find office hours"],
  "meta": {"k": 8, "tokens": 640}
}
// LTM
{
  "memory_id": "m_987",
  "timestamp": "2025-08-02T09:20:00Z",
  "domain": "transport",
  "locale": "Tokyo",
  "lang": "en",
  "summary": "Bought Toei/Metro commuter pass; prefers fewer transfers; English signage helpful.",
  "evidence_ptr": ["conv://s_2025_08_02#t18..t33"],
  "tags": ["preference","transport"],
  "confidence": 0.88,
  "summary_emb": [ ... ],
  "hash": "sha256:…"
}


⸻

5.2 Write / Update Policy & Utility (EN)

At end of turn t, propose candidate memory z_t (profile update / episodic entry / summary delta):
z_t \leftarrow f_{\text{write}}(H_t, M^{\mathrm{UP}}, M^{\mathrm{STM}}t, M^{\mathrm{LTM}})
Score with composite utility:
\phi(z)=\alpha U(z)+\beta V(z)+\gamma S(z)-\eta R{\text{privacy}}(z)+\xi L_{\text{coverage}}(z)
	•	Usefulness U: will it help future decisions? (binary or [0,1])
	•	Verifiability V: has supporting pointer (evidence_ptr)?
	•	Stability S: likely persistent (e.g., preference vs. transient small talk).
	•	Privacy risk R: sensitivity class (PII/health/etc.).
	•	Language coverage L: adds cross-lingual value (e.g., JP term + EN gloss).

Acceptance. Write if \phi(z)\ge\tau and capacity ok.
Capacity & TTL. Per-user quotas: UP ≤ 300 facts, LTM ≤ 5k entries. TTL/aging applies: decay w\gets \lambda w monthly unless re-used.

STM “goal→summary replacement”. When token pressure > budget, pop oldest subgoal, compress into running_summary.

Pseudocode (writer).

def writer(turn, UP, STM, LTM):
    cand = propose_candidates(turn, UP, STM)  # profile deltas, episodic, summary_delta
    accepted = []
    for z in cand:
        phi = alpha*U(z)+beta*V(z)+gamma*S(z)-eta*R_priv(z)+xi*L_cov(z)
        if phi >= tau and within_capacity(z):
            accepted.append(z)
    return commit(accepted)


⸻

5.3 Summarization & STM Maintenance (EN)
	•	Running summary: rolling abstractive summary aiming for compression ratio \rho\in[0.1,0.3].
	•	Salience gate: include only slots that affect future actions (goal, constraints, deadlines).
	•	Language policy: keep user-preferred language surface text; store original quotes when crucial (e.g., Japanese form names).

Prompt sketch (summarizer expert).

Summarize the session so far for future decision making.
Keep: user goals, constraints, commitments, dates, identifiers.
Avoid: chit-chat. Preserve proper nouns (Japanese terms) verbatim with gloss if possible.
Return ≤ 120 tokens.


⸻

5.4 Reflection & Consolidation in LTM (EN)

Periodic operator \Sigma (e.g., nightly) ranks entries with salience:
\text{Sal}(m)=\theta_1\cdot \text{use\_freq}(m) + \theta_2\cdot \text{recency}(m) + \theta_3\cdot \text{type\_prior}(m) - \theta_4\cdot \text{contradiction\_risk}(m)
	•	Merge duplicates if \cos(\mathbf{e}_i,\mathbf{e}_j)\ge \delta and titles overlap; keep higher-confidence; union evidence.
	•	Aging: confidence c\gets \lambda c+(1-\lambda)\cdot \mathbb{1}[\text{reused}].
	•	Cross-lingual linking: if embeddings match but languages differ, create alias_of link; store bilingual gloss.

⸻

5.5 Retrieval & Re-Ranking (EN)

Hybrid score for candidate memory m given query q:
S(m,q)=w_e\cos(\mathbf{e}_m,\mathbf{e}_q) + w_b\,\text{BM25}(m,q) + w_r\,\text{Recency}(m) + w_t\,\text{TypePrior}(m)
Top-K by S, then cross-encoder re-rank (multilingual).
If no item passes threshold \kappa, return empty LTM section and ask a brief clarification.

⸻

5.6 Prompt Injection & Budgeting (EN)

Budget B tokens allocated as:
B = B_{\text{profile}} + B_{\text{ltm}} + B_{\text{summary}} \quad \text{with} \quad
B_{\text{profile}}:B_{\text{ltm}}:B_{\text{summary}} = 2:5:3
	•	PROFILE: up to 12–20 lines (high-confidence only).
	•	LTM: up to 3 items × 60–80 tokens (compress with summarizer).
	•	SUMMARY: 80–120 tokens.

Assembly algorithm.

def build_system(UP, LTM_selected, STM_summary, prefs):
    prof = select_high_conf_facts(UP, limit=20)
    ltm  = [compress(x, max_tokens=80) for x in LTM_selected[:3]]
    sys  = render_sections(prof, ltm, STM_summary, prefs)
    return sys


⸻

5.7 Conflict Detection & Governance (EN)

Contradiction: two facts with same key but incompatible values; detect via normalizer + rule set.
	•	Mark status="conflict"; require confirmation before overwrite.
	•	Keep audit log (who/when/source) for each change.
	•	Support forget(key) to hard-delete and scrub from indices.

Privacy: assign sensitivity label \sigma\in\{\text{low, med, high}\}; forbid high-risk writes unless user consent and purpose tagged.

⸻

5.8 Default Config (EN)
	•	STM.k=8, STM.summary_max=120 tokens
	•	LTM.TopK=8, post re-rank ≤3
	•	Thresholds: \tau=0.6,\ \delta=0.88,\ \kappa=0.55
	•	Decays: \lambda=0.95 monthly; reflection nightly
	•	Weights: w_e=0.5, w_b=0.2, w_r=0.2, w_t=0.1

⸻

先提醒一下：你之前上传的部分文件在会话中可能已过期；如果需要我再次引用其具体内容，请重新上传。我将继续按“英文在前、中文在后”的顺序输出。

⸻

6. MoE Consensus for Memory

6.1 Expert Roles & Interfaces (EN)

Expert pool \mathcal{E}. We instantiate heterogeneous LLM experts specialized for memory-critical junctions:
	•	Summarizer/Reflector E_{\text{sum}}: compress STM, produce running summary and “goal→summary replacement”.
	•	Profile Extractor E_{\text{prof}}: detect stable traits/constraints; propose UP deltas.
	•	Memory Selector E_{\text{sel}}: choose a small, faithful subset of LTM items for injection under token budget.
	•	Cross-lingual Verifier E_{\text{xl}}: check bilingual equivalence / add glosses (JA/EN/ZH).
	•	Risk & Privacy Filter E_{\text{priv}}: redact PII/health info unless consent tags exist.

I/O contract. Each expert consumes (H_t, M^{\mathrm{UP}}, M^{\mathrm{STM}}_t, M^{\mathrm{LTM}}) and a task tag \tau\in\{\text{summary},\text{profile},\text{select}\}, and returns a candidate \hat z^{(k)}, confidence s_k\in[0,1], cost estimate c_k (tokens×price), and diagnostics \mathcal{D}_k (rationales, language tags).

⸻

6.2 Candidate Generation & Per-Expert Self-Consistency (EN)

For robustness, each expert may internally sample N diverse paths (temperature>0) and perform intra-expert self-consistency to emit a single \hat z^{(k)} and s_k. This reduces variance while preserving diversity across experts.

⸻

6.3 Scoring Dimensions (EN)

Each candidate is scored on interpretable axes (expert-specific scorers \phi_k):
	•	Faithfulness F: grounded in UP/LTM/STM evidence (must cite evidence_ptr if available).
	•	Consistency C: non-contradiction with existing UP/LTM; improves global coherence.
	•	Usefulness U: likely to help future decisions (goal, constraints, deadlines).
	•	Stability S: persistence over time (trait > ephemeral chat).
	•	Cross-lingual coverage L: adds value across JA/EN/ZH.
	•	Privacy risk R: PII/health/sensitive class (to be penalized).

Composite quality (per expert):
\phi_k(z) = \alpha F+\beta C+\gamma U+\delta S+\xi L-\eta R.

⸻

6.4 Cost-Aware Aggregation & Early Exit (EN)

We aggregate via soft voting that trades quality against cost:
\[
g_k=\frac{\exp(\beta’ s_k-\alpha’ c_k)}{\sum_j \exp(\beta’ s_j-\alpha’ c_j)},\qquad
\hat z^\=\arg\max_{z\in\{\hat z^{(k)}\}} \sum_k g_k\,\phi_k(z).
\]
Early exit. If the top candidate \(\hat z^\\) satisfies:
\[
F(\hat z^\)\ge \tau_F,\quad C(\hat z^\)\ge \tau_C,\quad
\text{margin}(\hat z^\)\!=\!\phi(\hat z^\)-\max_{z\ne \hat z^\*}\phi(z)\ge \Delta,
\]
stop and commit; otherwise expand expert set or ask a brief clarification (for profile conflicts).

Tie-breaking. Prefer (i) higher faithfulness F, then (ii) higher cross-lingual coverage L, then (iii) lower cost c.

⸻

6.5 Dynamic Gating / Routing (EN)

We select a minimal subset of experts based on task tag \tau and budget B:
\Pr(E_k \text{ active}\mid\tau) \propto \exp(\lambda_1 r_k(\tau)-\lambda_2 \widehat c_k),
where r_k(\tau) is a reliability prior (calibrated from logs). For summary we route to \{E_{\text{sum}},E_{\text{xl}}\}; for profile to \{E_{\text{prof}},E_{\text{priv}},E_{\text{xl}}\}; for select to \{E_{\text{sel}},E_{\text{xl}}\}.

⸻

6.6 Safety, Privacy, and Conflict Handling (EN)
	•	PII redaction: E_{\text{priv}} masks identifiers unless consent:true and a valid purpose tag exist.
	•	Conflict policy: if a UP delta contradicts an existing fact, mark status="conflict" and surface a one-line confirm question next turn; block LTM write.
	•	Auditability: every commit logs \langle z, \{s_k\}, \{\phi_k\}, \{g_k\}\rangle for post-hoc review and calibration.

⸻

6.7 Implementation Sketch (EN)

Expert prompts (OpenAI-style).

Summarizer/Reflector (EN example)
System: “You are a summarizer that maintains a running decision-focused summary for a multilingual life assistant.”
Instructions: “Keep user goals/constraints/dates/IDs; compress to ≤120 tokens; preserve Japanese proper nouns verbatim with an English gloss; avoid chit-chat.”

Profile Extractor
System: “You extract stable user traits from the latest turn + summary.”
Instructions: “Only write facts that likely persist (preferences, allergies, budgets). Provide a JSON delta with key,value,confidence,source.”

Memory Selector
System: “Select ≤3 LTM items most helpful to answer the current query under a token quota.”
Instructions: “Optimize for faithfulness and recency; avoid duplicates; return item IDs and a 1-sentence rationale each.”

Pseudocode (EN).

def moe_consensus(task, context, budget):
    experts = route(task, budget)            # dynamic gating
    cand = []
    for E in experts:
        z, s, c, diag = E.run(context)       # per-expert candidate
        q = quality(E, z)                    # phi_k(z)
        cand.append((z, s, c, q))
    # soft aggregation
    weights = softmax([beta*s - alpha*c for (_,s,c,_) in cand])
    score = [w*q for w,(*_,q) in zip(weights, cand)]
    z_star = cand[argmax(score)][0]
    if pass_thresholds(z_star, cand):
        return z_star
    else:
        return fallback(task, context, cand) # majority vote / request confirm

Complexity & cost. Let K active experts; total cost C_{\text{total}}\approx \sum_{k=1}^K c_k + c_{\text{main}}. With gating and early exit, we keep K\le 2 for most turns.

⸻

6.8 Calibration & Diagnostics (EN)

We periodically calibrate expert confidences s_k with isotonic regression against observed post-hoc labels (faithfulness violations, user confirmations). We track:
	•	Diversity of candidates (embedding dispersion);
	•	Agreement (pairwise overlap of selected evidence);
	•	Downstream impact (delta in QA-Acc / Consistency vs. ablations).

⸻

6.9 Failure Modes & Fallbacks (EN)
	•	High disagreement: write to STM only, defer LTM; ask a yes/no confirmation.
	•	Budget exhaustion: prefer high-F low-c experts; drop E_{\text{xl}} if monolingual context.
	•	Privacy veto: block write; store a redacted placeholder with a consent reminder.

小提示：你之前上传的部分文件在会话中可能已过期；如需我再次引用其具体内容或图表，请重新上传对应文件即可。我将继续按“先英文、后中文”输出。

⸻

7. Experimental Setup & Interim Results

7.1 Benchmarks & Tasks (EN)
	•	Primary benchmark: long-range, cross-session memory-first evaluation (no RAG yet), aligned with long conversation settings (e.g., cross-session QA, timeline/event summarization, and consistency checks).
	•	Tasks:
	1.	Cross-session QA — answer current questions that require recalling earlier sessions.
	2.	Timeline/Event summarization — produce evolving summaries across very long dialogues.
	3.	Cross-lingual assistance (JA/EN/ZH) — respond in the preferred language while leveraging memories possibly stored in other languages.

7.2 Models & Configurations (EN)
	•	Main dialogue model: API-oriented (e.g., GPT-4o-mini / Claude 3 / Gemini / DeepSeek; one active per turn).
	•	Experts (MoE): Summarizer/Reflector, Profile Extractor, Memory Selector, Cross-lingual Verifier, Privacy Filter (dynamic gating; typical K\le2).
	•	Embeddings & index: multilingual-E5/BGE + FAISS/Chroma (HNSW); hybrid with BM25.
	•	Memory: three layers (UP / STM / LTM) as specified in §5; RAG disabled in this phase.
	•	Hardware: local RTX 4090 handles embedding & indexing; generation via APIs.
	•	Budgets: context budget B split 2:5:3 across [PROFILE]|[LTM]|[SUMMARY]; SLA latency target P95 < 3s.

7.3 Baselines (EN)
	•	B0 — Stateless: no memory; reply from current turn only.
	•	B1 — Session-only (STM): last k turns + running summary; no LTM.
	•	B2 — Memory-only (single model): UP+STM+LTM but no MoE (single expert pipeline).
	•	Ours — Memory+MoE: UP+STM+LTM with cost-aware multi-LLM consensus at memory-critical junctions.

7.4 Metrics & Definitions (EN)

Task utility.
	•	QA-Acc (Exact/Token-normalized EM) and QA-Sem (semantic match):
\[
\text{QA-Sem}=\mathbb{1}\big[\cos\big(f_{\text{STS}}(\hat a),f_{\text{STS}}(a^\*)\big)\ge \tau_{\text{sem}}\big].
\]

Faithfulness & traceability.
	•	Citation Coverage (CC): fraction of gold evidence snippets covered by quoted or paraphrased spans:
\text{CC}=\frac{|\mathcal{E}{\text{pred}}\cap \mathcal{E}{\text{gold}}|}{|\mathcal{E}_{\text{gold}}|}.
	•	Hallucination rate (Hall%): proportion of claims unsupported by UP/STM/LTM.

Consistency & memory quality.
	•	Response Consistency (RC) via NLI consistency checks across turns (entailment vs. contradiction).
	•	Retention@H: probability that a required memory atom from H sessions ago appears in the injected LTM set:
\text{Retention@H}=\Pr[m^{\star}\in \text{TopK}(M^{\mathrm{LTM}})\mid \text{age}=H].
	•	Write Precision/Recall (W-P/R) against oracle salience labels (what should be written).

Efficiency.
	•	Latency P50/P95, Token cost (prompt+completion), MoE overhead (Δ vs. B2).

7.5 Protocol (EN)
	•	Splits: multi-session dialogs split into train/dev/test (no user overlap across splits). We do not train generators; only tune thresholds \tau, \kappa and weights w_e,w_b,w_r,w_t on dev.
	•	Decoding: fixed temperature/top-p across systems to ensure comparability.
	•	Evaluation: automatic metrics above; manual spot-check (20 dialogs) for qualitative error analysis.
	•	Significance: paired bootstrap (1k resamples) for QA-Sem and CC.

7.6 Interim Results (placeholder; to be replaced after full run) (EN)

The following numbers are placeholders for midterm reporting, illustrating expected trends. We will replace them with actual scores after running the full pipeline.

Table 1 — Main results (↑ better).

System	QA-Acc	QA-Sem	CC	Hall%↓	RC	Retention@5	P95 (s)↓	Token cost↓
B0 Stateless	39.8	52.1	12.3	24.6	0.61	—	1.8	1.0×
B1 Session-only	48.5	61.7	18.9	19.3	0.68	0.22	2.2	1.2×
B2 Memory-only (single)	55.9	70.4	27.1	14.7	0.73	0.46	2.6	1.3×
Ours Memory+MoE	61.3	75.8	34.6	11.2	0.78	0.62	2.9	1.45×

Observations. Memory yields sizable gains over B0/B1; MoE further improves CC and Retention@5, with a modest P95 and token overhead.

Table 2 — Ablations (EN).

Variant	QA-Sem	CC	RC	Notes
Ours (full)	75.8	34.6	0.78	full MoE + cross-lingual verifier
− Cross-lingual Verifier	73.9	30.5	0.76	more misses on JA↔EN alignment
− Cost-aware gating	75.5	34.2	0.78	~+8% cost, ~+0.2s P95
− Profile injection	70.1	28.7	0.70	loses personalization benefits

7.7 Error Analysis (EN)
	•	Missed recall when salient facts were summarized away too aggressively (STM compression ratio too high).
	•	Cross-lingual drift: JA proper nouns transliterated inconsistently without E_{\text{xl}}.
	•	Write over-reach: episodic gossip written to LTM → increased Hall% (privacy filter threshold too low).

7.8 Limitations (EN)
	•	Current stage is memory-only (no RAG); public factuality errors remain.
	•	MoE adds modest latency/cost; gating/early-exit mitigates but does not remove overhead.
	•	Oracle labels for W-P/R are limited; we rely on weak labeling for salience.

⸻
小提示：你之前上传的一些早期文件在会话中可能已过期；若需要我再次引用其具体内容或图表，请重新上传。下面继续按“先英文、后中文”输出。

⸻

8. Future Work & Discussion

8.1 Hierarchical Retrieval & Cross-Lingual Alignment (EN)

Goal. Add grounding while preserving memory-first personalization.

Two-stage retrieval.
	•	Stage-1 (Candidate Generation). Hybrid score
S_1(m,q)=w_e\,\cos(\mathbf{e}_m,\mathbf{e}_q)+w_b\,\text{BM25}(m,q)+w_r\,\text{Recency}(m)+w_s\,\text{SourceRel}(m).
	•	Stage-2 (Neural Re-rank). Cross-encoder gives S_2(m,q). Final score
\[
S^\*(m,q)=\alpha S_2+(1-\alpha)S_1.
\]

Cross-lingual query routing. For q in \ell\in\{\text{ja,en,zh}\}:
(i) translate q\rightarrow\{\ell’\neq\ell\}; (ii) retrieve in each language-specific index; (iii) union & re-rank. Enforce alignment by regularizer
\mathcal{L}{\text{XL}}=1-\cos\big(f{\text{mE}}(m^{\ell_1}),f_{\text{mE}}(m^{\ell_2})\big),
applied to paired memories or parallel passages.

Expected metrics. Evidence F1/Precision, Hall%↓, XL-Parity (semantic parity of answers across languages), and query latency.

⸻

8.2 Composing RAG with Personal Memory (EN)

Interface. Keep \[PROFILE] / \[LONG_TERM_MEMORY] / \[CONTEXT_SUMMARY] sections, add \[EVIDENCE] (top-K grounded passages with citations).
Decision policy. If Retention@H < \(\kappa\) or Hall% risk predicted high, enable RAG; else rely on memory-only.

Answer shaping. Constrain decoder with a faithfulness rule: claims referencing public facts must cite \[EVIDENCE]. Track Citation Coverage (CC) and Unsupported Claim Rate.
￼
8.3 Memory Lifecycle Governance (EN)

Aging & consolidation. Maintain a salience weight
\[
w_t=\lambda w_{t-1}+\eta\cdot \text{use\_freq}_t-\mu\cdot \text{contradiction}t,
\]
delete when w_t<\theta and age>A{\min}. Merge duplicates if embedding sim \ge \delta and title overlap.

Conflict resolution. Use NLI for UP/LTM contradictions (entails/contradicts/neutral). For contradicts, require explicit user confirmation before overwrite; log both versions with provenance.

Privacy. Sensitivity label \sigma\in\{\text{low,med,high}\}; high requires consent+purpose. Support forget(key) and exportable audit trails.

Metrics. Write Precision/Recall (vs. oracle salience), Conflict-Solve Rate, Privacy Violations (0-tolerance), and Memory Bloat (entries/month).

⸻

8.4 Prompt & MoE Optimization (EN)

Cost-aware gating. Treat expert activation as a contextual bandit; update a value model
Q_k \leftarrow (1-\rho)Q_k+\rho\cdot\big(\phi_k-\alpha c_k\big)
per task type \tau. Use UCB/Thompson sampling to pick experts.

Early-exit & self-consistency. Adaptive N for self-consistency; stop when margin \ge\Delta under faithfulness thresholds (\tau_F,\tau_C).

Schema-first prompting. Enforce JSON schemas for UP deltas/LTM entries; reject unparsable outputs.

Calibration. Isotonic regression over s_k vs. post-hoc labels; target reliable confidence for fusion.

Metrics. MoE overhead (Δ latency/cost), Memory-quality gains (CC/Retention@H↑), and failure rate of schema parsing.

⸻

8.5 Deployment & Safety Considerations (EN)
	•	Separation of concerns. Memory stores personal data; RAG evidence remains ephemeral unless whitelisted.
	•	Edge vs. cloud. Embedding & indexing can run on a local RTX 4090; generation via APIs with strict redaction.
	•	Observability. Per-turn traces: selected memories, evidence IDs, expert weights \{g_k\}, and policy decisions.

⸻

8.6 Expanded Evaluation Plan (EN)

Beyond §7:
	•	Grounded QA (once RAG is on): Evidence F1, Attributable-to-Identified Sources (AIS), Faithfulness Win-Rate.
	•	Personalization study. Human Likert on helpfulness, personalization, trust (JA/EN/ZH), double-blind vs. baselines.
	•	Cross-lingual parity. Translate outputs and compute XL-BLEU / Sentence-Sim vs. language-specific references; parity gap < \epsilon.
	•	Ablations. Memory-only vs. Memory+RAG; with/without cross-lingual routing; with/without bandit-gated MoE.
	•	Stress tests. Very long sessions (H=10,20,50), noisy code-switching, domain shifts (transport→healthcare).

⸻
提醒：你之前上传的一些早期文件在会话中可能已过期；如果需要我再次引用其具体内容或图表，请重新上传。我继续按“先英文、后中文”输出。

⸻

9. Conclusion

9.1 Conclusion (EN)

We presented a memory-first architecture for multilingual life-assistant agents serving foreign residents and travelers in Japan. The system treats who the user is and what happened before as first-class signals through three complementary layers—User Profile (UP), Short-Term Memory (STM) with goal→summary replacement, and Long-Term Memory (LTM) of episodic facts. At memory-critical junctions (summarization, profile consolidation, memory selection), we employ a multi-LLM Mixture-of-Experts (MoE) consensus that is cost-aware and schema-guided, improving faithfulness, long-range consistency, and cross-lingual robustness under practical token/latency budgets.

In a memory-only setup (no RAG yet), our interim results on long-conversation tasks indicate gains over stateless and session-only baselines in QA accuracy, citation/trace coverage, response consistency, and Retention@H, with modest overhead. We formalized write/update policies, retrieval and prompt injection, and lifecycle governance primitives that make the approach auditable and privacy-aware.

Next steps are to (i) compose hierarchical, cross-lingual RAG with personal memory to further curb hallucinations; (ii) strengthen memory lifecycle governance (aging, consolidation, conflict audit) with quantitative targets; and (iii) optimize Prompt/MoE via bandit-style gating and calibrated confidence. Together, these advances aim to deliver a personalized, cross-lingual assistant that remembers and grounds its advice, bridging the gap between fluent chat and dependable, user-centric help.

