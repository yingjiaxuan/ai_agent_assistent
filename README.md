
---

# 🇯🇵 AI Agent Web App: Life Assistant for Living in Japan DEMO1.0

## 🧠 Project Goal

Develop a web application based on AI Agent architecture to provide international students and workers living in Japan with three intelligent supports: **task reminders**, **intelligent Q&A with personalized memory management**, and **local life service recommendations**, enhancing life efficiency and reducing task burdens.

---

## 🧩 Core of Agent Architecture: Observe → Think → Act

| Stage    | Description                                  | Technical Means                           |
|----------|----------------------------------------------|-------------------------------------------|
| Observe  | Perceive user input and environment information | Form input, database reading, API interface, context analysis |
| Think    | Analyze information, reason and judge        | GPT-3.5 reasoning, rule triggering, prompt engineering        |
| Act      | Provide action suggestions and feedback      | Proactive reminders, text generation, UI updates                |

---

## 📅 Feature One: AI Reminder Agent

### 🎯 Goal

Record and understand user tasks, proactively generate reasonable reminder strategies, and optimize task order.

### 🔧 Module Functions

| Intelligent Stage | Function Description                           | Example                                       |
|-------------------|------------------------------------------------|-----------------------------------------------|
| Observe           | Record tasks and categorize                    | Add: "Hitachi ES deadline 5/10"               |
| Think             | LLM analyzes categories and time, determines priority and action timing | Generate: "Submit recommendation letter by 5/7, prepare in advance" |
| Act               | Proactively remind and output optimized schedule | Today's reminder: Combine 3 pieces of information, suggest completing ES first |

---

## 🤖 Feature Two: LLM Q&A Assistant + Memory (LLM + Memory Agent)

### 🎯 Goal

Provide users with intelligent answers and automatically build personal memory files to enhance personalized recommendations and context-based reasoning.

### 🔧 Module Functions

| Intelligent Stage | Function Description                                 | Example                                       |
|-------------------|------------------------------------------------------|-----------------------------------------------|
| Observe           | Record questions and summary of answers              | Ask: "How do I write an internship email?"    |
| Think             | Enhance prompts with memory information (e.g., major, school) | Answer: "Emphasize your modeling experience with your information chemistry background" |
| Act               | Output personalized answers; periodically generate memory documents and auto-remind reviews | "Remember to update your progress in the Hitachi interview" |

---

## 📍 Feature Three: Contextual Life Assistant

### 🎯 Goal

Provide users with life suggestions such as festivals, weather, and short trips based on time, location, and schedule.

### 🔧 Module Functions

| Intelligent Stage | Function Description                                        | Example                                         |
|-------------------|-------------------------------------------------------------|------------------------------------------------|
| Observe           | Perceive location, weather, holidays, user schedule         | Location: Sapporo, Weather: Sunny, Golden Week approaching |
| Think             | Determine user's free time and holiday opportunities        | Determine no tasks on the weekend, infer suitable for short trips |
| Act               | Generate recommendation: "Hokkaido Cherry Blossom Festival opens this week, suitable for weekend visit" | Attach map/transport/activity links |

---

## 🧱 System Architecture Diagram

```
+---------------------+
|  User Interface     |
|  (Streamlit Tabs)   |
+---------------------+
        ↓           ↓
+---------------------+   +-------------------+
| Reminder Agent      |   | LLM+Memory Agent  |
| - Categorize tasks  |   | - Record questions|
| - Time strategy advice| | - Personalized replies|
| - Merge task reminders| | - Generate memory summaries|
+---------------------+   +-------------------+
        ↓           ↓
     +------------------------+
     |  Contextual Life Agent |
     | - Festival/weather/activity recommendations |
     | - Smart push based on schedule|
     +------------------------+
```

---

## 🔧 Tech Stack

| Module         | Technology                        |
|----------------|-----------------------------------|
| Frontend UI    | Streamlit                         |
| Backend Language  | Python                           |
| Intelligent Module | OpenAI GPT-3.5 (can be replaced with local models)|
| Storage        | SQLite + Markdown/YAML memory documents |
| Third-Party APIs | Weather API, Holiday API (e.g., HolidayAPI), etc. |

---
