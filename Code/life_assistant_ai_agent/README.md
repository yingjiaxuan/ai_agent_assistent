# AI Agent Life Assistant Web App: Life Assistant for Living in Japan

This web application is designed to provide international students and workers living in Japan with intelligent support such as task reminders, intelligent Q&A with personalized memory management, and local life service recommendations. The application uses Flask for the backend, Streamlit for the frontend, and integrates with OpenAI's GPT-3.5 for AI capabilities.

## Features

1. **Task Reminders**: Add, view, and manage your reminders.
2. **Intelligent Q&A + Memory Agent**:
   - **Q&A System**: Integrate with GPT for life consultation, Japanese writing, and institutional Q&A.
   - **Memory Construction**: Extract and construct YAML/Markdown files from questions.
   - **Memory-Enhanced Q&A**: Use memory to enhance prompts for each conversation.
   - **Memory Review and Export**: View, edit, and download complete personal memory summaries.
3. **Contextual Life Assistant**:
   - **Context Information**: Fetch weather, holidays, and free time periods.
   - **GPT-Generated Life Suggestions**: Provide suggestions like attending local events.
   - **Prompt Push Logic**: Automatically display daily life suggestions or activate them on a schedule.

## Installation

First, ensure you have the required libraries installed:

```bash
pip install Flask streamlit openai pyyaml requests
```

## Folder Structure

```plaintext
/life_assistant_ai_agent/
├── app.py                  # Main entry point with Streamlit routes
├── agents/
│   ├── reminder.py         # Reminder-related functions and GPT integration
│   ├── memory_agent.py     # Memory extraction and Q&A enhancement
│   └── context_agent.py    # Holiday and weather recommendation logic
├── data/
│   └── reminders.db        # SQLite database
├── memory/
│   └── user_memory.yaml    # Memory content (human-readable)
├── utils/
│   └── prompts.py          # All prompt templates managed here
├── assets/                 # Icons, images, static files
├── .env                    # Environment variables (API keys)
└── README.md
```

## Usage

### Backend

1. **Set up the Flask backend**:
   - Create the necessary Python files in the `agents` directory.
   - Initialize the OpenAI API with your API key in `.env`.
   - Set up the SQLite database in the `data` directory.
   - Define routes for reminders, Q&A, memory management, and contextual life suggestions in `app.py`.

2. **Run the Flask backend**:
   ```bash
   python app.py
   ```

### Frontend

1. **Set up the Streamlit frontend**:
   - Design a modern UI with Streamlit, using a sidebar for navigation and modern elements like cards, icons, and colors suitable for users aged 18-25.
   - Include features for adding reminders, viewing reminders, asking questions, viewing memory, and receiving life suggestions.

2. **Run the Streamlit frontend**:
   ```bash
   streamlit run app.py
   ```

## Running the Application

1. **Start the Flask backend by running `app.py`**:
   ```bash
   python app.py
   ```

2. **Start the Streamlit frontend by running `streamlit run app.py`**:
   ```bash
   streamlit run app.py
   ```

This setup creates a web application where users can add reminders, view reminders, ask questions to the AI, view the memory of previous questions and answers, and receive contextual life suggestions.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

This `README.md` file provides an overview of the project, installation instructions, usage details, and how to run the application along with an example of a modern UI design suitable for users aged 18-25. The folder structure is also clearly outlined to help organize the codebase effectively.