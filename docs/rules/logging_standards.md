# Global Logging Protocol & Standards

## 1. Purpose
This document defines the strict logging rules for all agents, orchestrators, and AI tools (CrewAI, Claude Code, VS Code Agents, Antigravity) operating within the SeaTurtle Photo-ID project. Maintaining a chronological, highly structured, and clean project log is critical.

## 2. Target Log File
**ALL** logs must be appended to the following file:
👉 `docs/project_log.md`

## 3. Trigger Conditions (When to Log)
You MUST append a new entry to the target log file immediately when:
* You complete a specific task, research assignment, or code generation.
* You make a crucial architectural, preprocessing, or machine learning decision.
* You encounter a significant error, bug, or exception.
* You successfully resolve a previously encountered issue.

## 4. Strict Formatting Rules
1. **NEVER overwrite** the `docs/project_log.md` file. Always **APPEND** to the end of the file.
2. Every entry must begin with a horizontal rule (`---`) to separate it from previous logs.
3. You must strictly use the exact Markdown template provided below.

## 5. Mandatory Log Template
Copy the format below and fill in the bracketed `[...]` information accurately for every log entry:

---
### [YYYY-MM-DD HH:MM:SS] — [Agent or Tool Name]
* **Action/Task:** [A brief, 1-2 sentence summary of what was attempted or completed]
* **Files Affected:** [List of files created, modified, or read. e.g., `src/preprocessing.py`, `docs/specifications/spec.md`. Write "None" if no files were touched]
* **Details/Decisions:** [Short description of the research findings, code logic implemented, or architectural decision made]
* **Issues & Resolutions:** [Describe any errors encountered and how they were fixed. If no issues occurred, write "None"]

---

## 6. Author Identity Guidelines
When filling out the `[Agent or Tool Name]` field, use your designated identity so the orchestrator knows who did what:
* If you are a CrewAI Agent, use your Role Name (e.g., `CV Researcher`, `Deep Learning Strategist`).
* If you are Claude Code or VS Code, use your tool name (e.g., `Claude Code`, `VS Code Custom Agent`).
* If you are Antigravity or a terminal execution, use `Antigravity / CLI Execution`.