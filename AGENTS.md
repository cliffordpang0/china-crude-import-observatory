# Project Instructions

## Mission

Read PRD.md before implementing. Build the China Crude Import Observatory in this project directory as a resume-quality quantitative research project using real official data. The user's priorities are usable public data, actual analytical results and relevance to Trafigura China and bp China commercial graduate roles.

## Workspace And Ownership

- Work in C:\Users\User\Desktop\AI experiments\China Crude Import Observatory.
- Treat unrelated files and other projects as user-owned. Preserve them.
- Respect the active filesystem and network permissions. Request narrowly scoped escalation when required; this document does not grant tool permissions.
- Use apply_patch for manual code and documentation edits. Keep raw downloaded files under data/raw, derived data under data/processed and reports under outputs.
- The handoff includes audit samples in work/data-audit. They are reference snapshots, not the entire dataset. Use them to reproduce initial checks and then audit the selected full historical window.

## Data Integrity

- No invented observations or fabricated results. No paid data dependencies.
- Source and record every observation from official JODI or Chinese government publications.
- JODI China refinery intake is supply-derived and circular with imports. Use independent NBS surveyed crude-processing volume for refinery-demand features.
- Missing inventories remain missing. Supply-processing residuals are indicative and cannot be called measured inventory changes.
- Handle January-February aggregation explicitly. Retain source units, metadata, publication timing and quality flags.
- Assessment code 3 means data has not been assessed. Numeric completeness does not imply data reliability.
- Do not bypass login, CAPTCHA or other access controls. Use official public releases or document the limitation.

## Modelling And Interpretation

- Start with simple benchmarks and interpretable models. Keep feature counts modest relative to sample size.
- Use chronological out-of-sample evaluation and lag features by actual or conservative publication availability.
- Never use realised future activity, random splits or full-sample preprocessing in backtests.
- If historical vintages are unavailable, label revised-data evaluation honestly.
- Report negative findings and uncertainty. Do not promise outperformance or trading profitability.
- Separate observed data, forecasts, accounting scenarios and commercial judgment in outputs.

## Engineering And Delivery

- Prefer a modest Python pipeline and local Streamlit app. Keep dependencies and structure simple; follow existing project conventions if any emerge.
- Add focused tests for financially meaningful failure modes: parsing, units, missing values, temporal alignment and leakage.
- Deliver PRD.md, AGENTS.md, README, reproducible commands, real data audit, forecast results, scenarios, dashboard and research memo.
- Start and verify the local dashboard on an available port. Report its URL and any unresolved material limitations.
- Produce resume wording only from actual work and measured results.
- Keep user updates concise and explain findings and decisions in plain language.
