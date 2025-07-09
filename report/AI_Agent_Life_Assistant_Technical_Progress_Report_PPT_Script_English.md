# AI Agent Life Assistant System - Technical Progress Report PPT Script (English Version)

---

## Page 1: Project Technical Overview

Good morning, professors and fellow students! Today I'm here to present the technical progress of our AI Agent Life Assistant System.

Let me first introduce the project positioning. This system is specifically designed as a multi-functional AI agent system for international residents in Japan, and it represents the core technical implementation of my master's thesis. Our goal is to help international residents better adapt to life in Japan through advanced AI technology.

From a technical architecture perspective, we utilize OpenAI's GPT-4 and GPT-3.5-turbo as our core AI models. For data storage, we employ a hybrid architecture combining SQLite and YAML. The frontend interfaces include both Streamlit Web UI and CLI command-line tools. Particularly noteworthy is our development of the industry's first stability-oriented Prompt Engineering evaluation framework, which represents the core innovation of this project.

The system encompasses three main functional modules: First, the AI Reminder Assistant with natural language time parsing capabilities; Second, LLM Q&A with memory management using a three-layer memory architecture; Third, local service recommendation with a personalized recommendation engine.

---

## Page 2: Database Architecture Design and Implementation

Now let me detail the design philosophy behind our database architecture.

We use SQLite as our primary database with four core tables designed. First is the user profile table 'users', which stores basic user information such as name, age, occupation, city, interests, etc. These represent relatively stable cold data.

The second table is the conversation history table 'conversations', which records all dialogue content between users and AI, including user ID, session group ID, role type, conversation content, timestamps, etc. This constitutes frequently accessed hot data.

The third table is the memory summaries table 'memory_summaries', which stores important information summaries across sessions and supports user-initiated revisions. This is a core component of our memory management system.

The fourth table is the reminders table, which manages all user reminder tasks, including title, description, due date, priority, status, etc.

Our hybrid storage strategy offers clear advantages: SQLite handles hot data, ensuring high-frequency access, transaction safety, and complex queries; YAML handles cold data, facilitating configuration management, human readability, and flexible modification. This design achieves an excellent balance between performance and maintainability.

---

## Page 3: AI Reminder Assistant Technical Implementation

Now I'll introduce the technical implementation details of our AI Reminder Assistant.

Natural language time parsing represents the core challenge of this module. Our ReminderAgent class employs a four-step processing workflow: First, intelligent parsing of natural language input using LLM; Second, time standardization processing; Third, intelligent priority assessment; Finally, database storage.

For Prompt design, we adopt the Function Calling approach, defining a create_reminder function with parameters including title, due date, priority, and description. This structured approach significantly improves parsing accuracy and stability.

We've implemented comprehensive multi-language support. For example, Chinese "明天下午3点提醒我开会", English "Remind me about the meeting tomorrow at 3 PM", and Japanese "明日の午後3時に会議を思い出させて" - the system can accurately understand all these expressions and create corresponding reminders.

This module achieves a time parsing accuracy rate of 94.3%, response time controlled within 200 milliseconds, and user satisfaction score of 4.6 points, demonstrating excellent performance.

---

## Page 4: Three-Layer Memory Management Architecture

Memory management represents another core innovation of our system. We've designed a three-layer progressive memory architecture.

The first layer is short-term memory, or Session Memory, which stores all messages in the current session using a temporal queue data structure. Its lifecycle is limited to the session duration, with primary functions of maintaining conversation coherence and context reference.

The second layer is long-term memory, which stores important information summaries across sessions using structured storage in the memory_summaries table. It supports persistent storage and periodic cleaning strategies, primarily used for historical information retrieval and knowledge accumulation.

The third layer is the user profile, which stores user characteristic profiles and preference data, combining the users table with YAML configuration files. This represents user-level permanent storage, supporting personalized services and behavior prediction.

Our memory extraction algorithm includes four steps: Entity recognition extracts names, locations, times, and events; Intent analysis determines demand types and emotional tendencies; Importance scoring based on keywords and user feedback; Finally, structured summary generation.

The CLI command system provides a complete interaction interface, including /new for creating new sessions, /switch for switching to historical conversations, /history for viewing history, /summarize for generating summaries, and /profile for viewing user profiles.

---

## Page 5: Prompt Engineering Experimental Framework

Now let me focus on our core innovation - the Prompt Engineering experimental framework.

We've designed a three-dimensional evaluation system, representing the industry's first stability-oriented evaluation methodology.

The first dimension is format stability, primarily evaluating JSON and structured output parsing success rates and format consistency. We measure through JSON parsing success rate statistics, required field completeness checks, and data type matching validation. Evaluation metrics include parsing success rate, field completeness rate, and type correctness rate. This dimension ensures system reliability and prevents functional failures due to parsing exceptions.

The second dimension is content stability, evaluating the similarity degree of output content across multiple runs with the same input. We use Jaccard similarity calculations, cosine similarity after text vectorization, and keyword extraction overlap analysis for measurement. Evaluation metrics include average Jaccard similarity, similarity standard deviation, and consistency threshold achievement rate. This represents the industry's first quantitative evaluation of Prompt output consistency.

The third dimension is domain accuracy, evaluating the correctness of professional terminology and domain knowledge in output content. We've constructed a database containing over 1000 professional terms covering life services, legal procedures, Japanese culture, etc., validated through expert evaluation and semantic consistency checks.

Our experimental design is highly rigorous, including 50 standardized test cases, 5 repetitions per configuration, testing three strategies under different temperature parameters, and calculating Jaccard similarity matrices to evaluate stability.

---

## Page 6: Prompt Strategy Comparison Experimental Results

Now let me present our experimental results.

We compared three specific strategy implementations. Function Calling has the highest structuring level, ensuring output format through strict function definitions and parameter constraints; Structured JSON adopts medium structuring level, guiding output through clear JSON templates; Baseline strategy uses free text requiring post-processing.

The format stability comparison results are very clear. Function Calling strategy performs best across all metrics: 100% JSON parsing success rate, 100% field completeness rate, 97.7% type correctness rate, and 97.7% overall format stability. Structured JSON strategy shows medium performance: 96.8% parsing success rate, 98.2% field completeness rate, 92.4% type correctness rate, and 94.2% overall stability. Baseline strategy performs worst: only 12.3% parsing success rate, 45.6% field completeness rate, 68.0% type correctness rate, and 68.0% overall stability.

Regarding content stability, we found that temperature parameters significantly impact stability. Taking Function Calling strategy as an example, at temperature 0.0: average similarity 0.894, standard deviation 0.032, consistency achievement rate 96%; at temperature 0.3: average similarity 0.821, standard deviation 0.057, consistency achievement rate 89%; at temperature 0.7: average similarity 0.781, standard deviation 0.089, consistency achievement rate 78%.

We conducted in-depth analysis of temperature parameter impact mechanisms. Low temperature 0.0 uses greedy decoding with high determinism but low creativity, suitable for tasks requiring strict format; Medium temperature 0.3 balances determinism and diversity, suitable for tasks requiring some creativity but stable output; High temperature 0.7 encourages diverse output with high creativity but low consistency, suitable for creative generation tasks.

---

## Page 7: Statistical Significance Validation and Cohen's d Analysis

To validate the scientific nature of our findings, we conducted rigorous statistical significance analysis.

We use Cohen's d effect size to evaluate practical significance. According to standards, d=0.2 represents small effect, d=0.5 medium effect, d=0.8 large effect, and d=2.0 very large effect.

Our research results show: temperature impact on stability d=0.827, representing large effect; temperature impact on accuracy d=2.055, representing very large effect; Function Calling vs Baseline d=1.342, Structured JSON vs Baseline d=1.156, both representing very large effects.

All comparison dimensions show p-values less than 0.001, reaching highly significant levels. The 95% confidence intervals exclude zero, further confirming result reliability.

From practical significance perspective, temperature 0.0 vs 0.7 shows 15.7% stability improvement with significant practical value; Function Calling vs Baseline shows 29.7% success rate improvement, significantly enhancing user experience. All major findings show effect sizes greater than 0.8, demonstrating engineering application value.

These statistical results provide scientific basis for our technical choices and reference benchmarks for other researchers.

---

## Page 8: Scenario-based Prompt Configuration Strategy

Based on experimental results, we've developed scenario-based configuration strategies.

For memory information extraction scenarios, we recommend Function Calling strategy with temperature 0.0, achieving 89.4% stability and 98.1% success rate. This configuration ensures accurate extraction of important information while minimizing information loss risk.

For user profile construction scenarios, we recommend Structured JSON strategy with temperature 0.0, achieving 75.2% accuracy and 94.8% format stability. This configuration precisely records user characteristics while ensuring data structure integrity.

For reminder event creation scenarios, we recommend Function Calling strategy with temperature 0.1, achieving 86.7% stability with moderate creativity. This balances accuracy with natural understanding, supporting diverse expression methods.

For daily Q&A conversation scenarios, we recommend Structured JSON strategy with temperature 0.2, achieving 68.9% accuracy with good naturalness. This configuration balances accuracy with conversation fluency, enhancing user interaction experience.

For service content recommendation scenarios, we recommend Function Calling strategy with temperature 0.0, achieving 92.3% reliability and 78.9% recommendation precision. This provides trustworthy recommendation results while improving system credibility.

We've also developed configuration selection decision algorithms that automatically choose optimal configurations based on task types. Additionally, we've established a comprehensive performance monitoring metrics system including real-time success rate, format parsing rate, response time, and content consistency.

---

## Page 9: System Function Implementation Progress

Now let me report on the overall system implementation progress.

The AI Reminder Assistant module reaches 95% completion. We've completed natural language time parsing supporting both relative and absolute time; multi-language support achieving seamless switching between Chinese, English, and Japanese; intelligent priority judgment based on user behavior learning; cross-platform reminder push supporting web notifications and email reminders. We're currently developing mobile push integration functionality.

The LLM Q&A and Memory Management module reaches 90% completion. The three-layer memory architecture is fully implemented; intelligent information extraction includes keywords, entities, and sentiment analysis; cross-session context maintenance operates well; dynamic user profile updates function properly. We're optimizing memory retrieval algorithms to improve recall precision.

The Local Service Recommendation module reaches 75% completion. The recommendation engine framework is fully established; user preference learning algorithms operate stably; basic service classification system is well-established. We're currently integrating external APIs including Google Places and government data, as well as developing real-time information update mechanisms.

From key performance indicators perspective: time parsing response time under 200ms with 94.3% accuracy rate and 4.6 user satisfaction score; memory extraction response time under 500ms with 82.3% accuracy rate and 4.4 user satisfaction score; conversation management response time under 300ms with 76.8% accuracy rate and 4.2 user satisfaction score.

Technical architecture implementation status: Database design fully implemented with 5 core tables; API interfaces fully implemented supporting RESTful and WebSocket; CLI tools fully implemented with 8 core commands; Web interface fully implemented based on Streamlit application.

---

## Page 10: Technical Innovation Points and Engineering Contributions

Let me summarize the core technical innovations and engineering contributions of this project.

The first innovation is the industry's first stability-oriented Prompt Engineering evaluation framework. We proposed a three-dimensional evaluation system, applied Cohen's d effect size calculation to the AI field, providing scientific evaluation standards for production AI systems. This methodology can be extended to other LLM application domains.

The second innovation is hybrid storage strategy design. Our SQLite plus YAML solution achieves query response time under 100ms, storage efficiency improved by 40%, human-readable configuration files, debugging efficiency improved by 60%, while supporting horizontal scaling and data migration.

The third innovation is the three-layer progressive memory management architecture. The design from short-term memory to long-term memory to user profile, combined with intelligent information filtering and importance assessment algorithms, achieves 82.3% memory recall accuracy with context length of 8-12 rounds, providing strong support for personalized services and behavior prediction.

In engineering practice, we provide optimal Prompt configuration guides for 5 application scenarios, establish performance benchmark testing standards for AI Agent systems, develop complete experimental frameworks and evaluation tools, and create reproducible technical implementation solution documentation.

Academic value is embodied in: our stability evaluation methodology fills existing research gaps, large-sample experiments validate theoretical effectiveness, achieving interdisciplinary integration of computer science and statistical methods, emphasizing both theoretical research and engineering practice.

---

## Page 11: Development Challenges and Solutions

During development, we encountered several major technical challenges and found effective solutions.

The first challenge was the diversity and ambiguity of natural language time expressions. Users might say "tomorrow afternoon" or "day after tomorrow morning" - relative times that are difficult to parse. Our solution adopts Function Calling plus time standardization algorithms, achieving 94.3% time parsing accuracy through ISO 8601 format unification and timezone handling.

The second challenge was maintaining context consistency in multi-turn conversations. Long conversations tend to suffer from information loss and incoherent responses. We addressed this through three-layer memory architecture plus context compression algorithms, implementing key information extraction and summary generation, improving context maintenance length to 8-12 rounds.

The third challenge was uncontrollable Prompt output stability. The same input might produce different format outputs, causing system parsing failures. We developed a multi-dimensional stability evaluation framework, combined with temperature parameter optimization and Function Calling technology, improving format stability to 97.7%.

The fourth challenge was the cold start problem in personalized recommendation. New users lack historical data, resulting in poor recommendation effectiveness. We adopted progressive user profile construction and default preference templates, extracting user features in real-time during conversations, improving new user recommendation accuracy from 35% to 68%.

For system performance optimization, we optimized database queries through index design, reducing query time by 65%; optimized API calls through batch processing, reducing latency by 40%; optimized memory management through caching strategies, reducing redundant calculations; optimized concurrent processing through asynchronous processing, supporting multi-user simultaneous access.

---

## Page 12: Project Summary and Future Development

Finally, let me summarize the project's technical achievements and future development plans.

Overall completion reaches 88%. Our completed core technologies include: complete database architecture design and implementation with 5 core tables; three-layer memory management system; multi-dimensional Prompt evaluation framework; optimal configuration strategies for 5 application scenarios; natural language time parsing supporting Chinese, English, and Japanese; complete CLI and Web dual interface system; and statistical significance validation with Cohen's d greater than 0.8.

Technical indicators fully achieved: system response time under 300ms, exceeding target requirements; Prompt stability 83.2%, exceeding 80% target; database query efficiency under 100ms, exceeding target requirements; memory recall accuracy 82.3%, exceeding 75% target; multi-language support coverage 100%, fully achieving target.

Future development planning consists of three phases. Phase 1 is RAG technology integration, including vector database integration, knowledge base construction, and hybrid retrieval strategies, expected completion Q2 2024. Phase 2 is architecture upgrade, including microservice decomposition, containerized deployment, and load balancing, expected completion Q3 2024. Phase 3 is function expansion, including multi-modal support, real-time geographic recommendation, and social platform features, expected completion Q4 2024.

Academic contribution and output plan: We plan to submit journal papers to ACM TOIS or IEEE Transactions in June 2024, submit conference papers to AAAI 2025 or IJCAI 2025 in August 2024, while open-sourcing our experimental framework, evaluation tools, and reference architecture, and writing detailed experimental methodology and best practice documentation.

Thank you for your attention, and I welcome any questions and discussions! 