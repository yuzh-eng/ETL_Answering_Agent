# ETL Migration Training Agent

## Project Overview
This is a training agent designed to help developers master the migration of Oracle/DataStage code to Snowflake.
The system generates "bad code" scenarios and asks the user to fix them according to new standards.

## Tech Stack
- **Language**: Python 3.8+
- **Frontend**: Streamlit
- **Database**: SQLite (built-in)
- **AI/Logic**: Currently Regex-based (Phase 1), extensible to LLM (Phase 2).

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Run the Streamlit app:
```bash
streamlit run app.py
```

## Features (Phase 1)
- **User Session**: Tracks progress by User ID.
- **Pattern-based Training**:
    - P1: Date Conversion (TO_DATE -> TO_TIMESTAMP_NTZ)
    - P2: Full-width Character Cleaning
    - P3: Null Handling (DataStage)
    - P4: Mixed Scenarios
- **Mistake Notebook**: Automatically records failed attempts for review.
- **Instant Feedback**: Regex-based validation of user code.

## File Structure
- `app.py`: Main Streamlit application entry point.
- `database.py`: SQLite database connection and schema management.
- `logic.py`: Question generation and answer validation logic.
- `requirements.txt`: Python dependencies.
- `etl_training.db`: SQLite database file (auto-generated).

## Roadmap
- [x] Phase 1: MVP with Regex validation and local SQLite.
- [ ] Phase 2: Integrate OpenAI/Gemini for dynamic question generation and semantic code review.
- [ ] Phase 3: Deployment to Streamlit Community Cloud.
