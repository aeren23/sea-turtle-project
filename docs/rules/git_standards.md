## 5. Git & GitHub Workflow Rules (MANDATORY)

When making changes to the codebase, you must respect the synchronization between the local environment and the remote repository.

1. **Local Changes First:** DO NOT use the GitHub MCP to commit code directly to the remote repository. If you modify, create, or delete files locally, you MUST use the terminal/shell tool to execute standard git commands:
   - `git add .` (or specific files)
   - `git commit -m "feat(module): description"` (Use Conventional Commits)
   - `git push`
2. **When to use GitHub MCP:** ONLY use the GitHub MCP for repository management tasks that do not involve committing local file changes. Examples:
   - Reading open Issues or Pull Requests.
   - Creating a new Issue.
   - Reviewing code on a remote branch.
3. **Commit before Logging:** Always complete your local `git commit` BEFORE appending your final status to `docs/project_log.md`.