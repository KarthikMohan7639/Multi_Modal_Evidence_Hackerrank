# Evidence Review Agent

This directory contains the AI agent logic for the HackerRank Orchestrate visual evidence review challenge.

## Components
- `agent.py`: Contains the core `evaluate_claim` function that uses OpenAI's GPT-4o-mini structured output to classify the image evidence.
- `main.py`: The execution script that loads `dataset/claims.csv`, evaluates each claim using the agent, and writes predictions to `output.csv`.
- `logging_helper.py`: A utility to comply with the logging rules set out in `AGENTS.md`.
- `evaluation/main.py`: Evaluates the model on `dataset/sample_claims.csv`, compares output against expected labels, and creates an operational analysis report in `evaluation_report.md`.

## Setup
Install requirements from `requirements.txt`.
Make sure `OPENAI_API_KEY` is exported.

## Running
```bash
python main.py
```
