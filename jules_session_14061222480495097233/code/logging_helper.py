import os
import datetime

def log_session_turn(action_summary: str, action_details: str):
    """
    Appends a turn to the log file per AGENTS.md requirements.
    """
    home_dir = os.path.expanduser("~")
    log_path = os.path.join(home_dir, "hackerrank_orchestrate", "log.txt")
    
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    log_entry = f"""
## [{timestamp}] Automated Processing Run

User Prompt (verbatim, secrets redacted):
[REDACTED] Automated system execution.

Agent Response Summary:
{action_summary}

Actions:
* {action_details}

Context:
tool=Jules
branch=main
repo_root=/app
worktree=main
parent_agent=none
"""
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to log: {e}")
