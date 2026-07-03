# Fort Fantastic — AI Decision Support System

Artifact accompanying the bachelor thesis:

> **Data-Governed AI Decision Support for Serious Game-playing**
> Otmane Messaoudi, Free University of Bozen-Bolzano, 2026

## Overview

A desktop chat application that provides AI-generated decision support for
players of the Fort Fantastic business simulation (BuGaSi GmbH). The system
operates in two modes:

- **Governed** — recommendations are grounded in a validated, database-backed
  knowledge base of the game's attractions, activity cards, and infrastructure,
  extracted from the official simulation manuals.
- **Ungoverned** — the model relies solely on general reasoning with no access
  to the knowledge base.

Every player–AI exchange is logged (mode, response text, token usage) to an
SQLite database for analysis. The empirical comparison between the two modes
forms the core of the thesis's results chapter.

## Project Structure

```
FortFantastic/
├── chat_assistant.py        # Main application (Tkinter chat UI)
├── analyze_interactions.py  # Analyzes logged interactions from the DB
├── .gitignore
└── db/
    ├── schema.sql           # SQLite database schema
    ├── setup_database.py    # Creates the database from schema
    └── seed_data.py         # Populates the database with game data
```

## Requirements

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)

## Setup

**1. Clone the repository**

```bash
git clone https://github.com/ottovanbebber/FortFantastic.git
cd FortFantastic
```

**2. Create a virtual environment and install dependencies**

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
pip install anthropic pillow python-dotenv
```

**3. Configure your API key**

Create a `.env` file in the project root and add your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

**4. Set up the database**

```bash
python db/setup_database.py
python db/seed_data.py
```

**5. Run the application**

```bash
python chat_assistant.py
```

## Usage

- Type a situation description and press Enter or click the send button
- Click the camera icon to attach a screenshot of the game before sending
- Click the **GOVERNED / UNGOVERNED** badge in the header to toggle modes
- Click the **↻** button to reset conversation context between decision points

## Analyzing Results

After running evaluation sessions, export the interaction log:

```bash
python analyze_interactions.py --csv results.csv
```

This produces a CSV with auto-counted card references, order codes, monetary
figures, word counts, and token usage per response, paired by situation text
across the two modes.

## License

This repository is released for academic reproducibility purposes.
The Fort Fantastic simulation and its associated materials are the property
of BuGaSi GmbH, Unna, Germany.
