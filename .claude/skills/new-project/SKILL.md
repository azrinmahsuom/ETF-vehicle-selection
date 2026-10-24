---
description: Project intake. Interviews the owner, writes docs/brief.md, and fills the README placeholders. Run once at the start of every new project.
disable-model-invocation: true
---

Run the intake for this new project.

1. Read `AGENTS.md`, `docs/brief.md` and `README.md`.
2. Ask the owner the brief's questions **one at a time**, in order. For each, show the question, a one-line example, and your suggested default where one exists. Wait for the answer before asking the next.
   - After question 2, skip question 5 and question 14 for a Tool, and question 11 for Research.
   - If an answer is vague (e.g. "analyse REITs"), ask one follow-up to make it specific and testable. Don't ask more than one.
   - Never answer a question on the owner's behalf. The hypothesis in particular must be in their words.
3. Write the answers into `docs/brief.md`, replacing every `{{placeholder}}`. Anything the owner was unsure about goes under "Open questions".
4. Fill the README placeholders that the brief now answers (title, thesis line, question, universe/period, method, status "In progress", data sources). Replace `{{repo-name}}` with the repo folder name. Leave the headline result, key findings and chart as `TBD`.
5. Rename `{{One-line project description}}` in `pyproject.toml` to the goal.
6. Add a dated first entry to `docs/decisions.md` recording the scope.
7. Remove the "Start here" block from the top of `README.md`.
8. Show a short summary of the brief, list any open questions, and propose the first two build steps. Ask before committing.
