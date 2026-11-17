# FE Bar Context

## 1. Purpose

I am building my own FE Bar submission: a working prototype that solves rebate fraud for a glucose monitor manufacturer in Life Sciences. The executive sponsor is the Director of Rebate Operations, the domain owner is the SVP of Contracting and Rebates, and they measure fraud prevention.

## 2. Non-Negotiable FE Bar Rules

- Build one connected journey starting from raw synthetic or public data: Lakeflow ingestion, Unity Catalog governance, Lakebase operational serving, ML or GenAI, a Genie agent, and a Databricks App. Each stage must consume the previous stage's output. No disconnected demos.
- The evaluator reads text only. Every stage requires committed textual evidence that it ran, including notebook outputs, run logs, query results, or model output. Screenshots and recordings do not count. Source code alone fails the Build domain.
- The GitHub repository must be readable by the evaluator: public, or private EMU connected through the submission form.
- Use synthetic or public data only. Never include real customer data, customer names, people's names, internal system names, or logos in code, data, documentation, commit messages, or the deck.
- This is my own work. Never use or imitate Solution Builder output, and never copy another person's build.
- A business deck in PDF, text, or Markdown format and an AI role-play are required. Prepare them at the end.

## 3. How You Work With Me

- Work in small, verifiable steps. After every step, state what changed, how it was verified, and what comes next.
- Stop and ask before deciding the use case and story, personas, architecture and trade-offs, planted data issues, quality rules, access rules, AI approach, value-case numbers, slide content, or narrative. Present two or three options with pros, cons, and a recommendation. I decide.
- Maintain `BUILD_LOG.md` with the date, what was tried, what failed, what changed, and why. I will use it to explain how I used AI.
- Record every decision I make in `DECISIONS.md`, including the decision, options considered, and rationale. I will rewrite it in my own words.
- Mark every drafted narrative, opinion, and decision section in `README.md`, `DECISIONS.md`, and deck notes with `[YOUR WORDS]` so I can rewrite it myself. The use case, decisions, numbers, and words must be mine.
- Never print, log, or commit tokens, passwords, or connection strings. Never guess a Databricks CLI profile; ask me.

## 4. Engineering Conventions

- Workspace: ask for the workspace URL and CLI profile, then include `--profile <name>` on every Databricks CLI command.
- Store everything in Unity Catalog under `vandelay.rebate_fraud`. Put raw files in a Unity Catalog volume under that schema.
- Deploy everything with a Declarative Automation Bundle: use `databricks.yml` with variables for catalog, schema, warehouse ID, and model endpoints and one target; use `resources/*.yml` for pipelines, jobs, and apps. Commands are `databricks bundle validate`, `databricks bundle deploy`, and `databricks bundle run <resource>`.
- Prefer serverless compute: serverless Lakeflow pipelines, serverless jobs, and a serverless SQL warehouse.
- Implement Lakeflow Spark Declarative Pipelines in SQL unless Python is clearly better.
- Make reruns safe and idempotent. Running a step twice must not create duplicate rows.
- End every notebook task with `dbutils.notebook.exit(json.dumps(summary))`, where `summary` is short JSON describing rows, IDs, pass counts, and other relevant results. Python file tasks must print the same summary. The evidence step reads these summaries because `.py` notebooks do not carry outputs in the repository.
- If Databricks agent skills are installed, load the matching skill before working with each product, including pipelines, Unity Catalog, Lakebase, apps, Genie, MLflow, jobs, and bundles, and follow it.

## 5. Repository Layout

Use this layout:

```text
README.md
FEBAR_CONTEXT.md
USE_CASE.md
BUILD_PLAN.md
EVAL_PROTOCOL.md
DECISIONS.md
BUILD_LOG.md
databricks.yml
resources/
src/data/
src/pipeline/
src/governance/
src/ai/
src/serve/
src/genie/
src/app/
tools/
evidence/
deck/
```

Add `.gitignore` entries for `.databricks/`, `.env`, `*.pem`, local notes, and all credentials.

## 6. Definition of Done for Every Task

A task is done only when its code is committed, deployed, and run successfully in the workspace; verified with a query or API call whose output is shown to me; and recorded with a line in `BUILD_LOG.md`.
