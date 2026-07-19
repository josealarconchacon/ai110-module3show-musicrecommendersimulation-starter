# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**Prompts used:**

<!-- Paste the key prompts you gave the agent -->

**What did the agent generate or change?**

<!-- List the files edited, code generated, or commands run -->

**What did you verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

I used a Strategy pattern, but a lightweight version of it. Instead of a full class hierarchy with a separate class per scoring mode, I used a single frozen `ScoringWeights` dataclass to represent a scoring strategy, and a dict mapping mode names to instances of it.

**How did AI help you brainstorm or implement it?**

I wanted to support multiple scoring modes (default, mood-first, energy-focused) without copy-pasting my `score_song` logic three times. I asked the AI whether a Strategy pattern made sense here, and we talked through two options: a full polymorphic Strategy (a `ScoringStrategy` base class with a separate subclass and `.score()` method per mode) versus a simpler weights-object approach.

The AI's reasoning, which I agreed with, was that all three of my modes use the exact same formula, genre match, mood match, energy closeness, acoustic match, and only differ in the numeric weights applied to each part. A full class-per-mode Strategy only pays for itself if a mode needs genuinely different logic, like a nonlinear energy curve instead of linear closeness. Since none of my modes need that, going with separate classes would have been unnecessary abstraction for what is really just configuration data. The weights-object version keeps the scoring logic in one place while still being easy to upgrade later: if a future mode ever needs different logic and not just different numbers, `ScoringWeights` can become an ABC with a `.score()` method without changing how callers use it.

**How does the pattern appear in your final code?**

In `src/recommender.py`, the "strategy" is the `ScoringWeights` frozen dataclass (holds `genre`, `mood`, `energy`, `acoustic`), and `SCORING_MODES` is the registry of named strategies (`"default"`, `"mood-first"`, `"energy-focused"`), each with different weight values. `score_song` and `recommend_songs` both take a `weights: ScoringWeights` parameter (defaulting to `SCORING_MODES["default"]`) and use it in place of hardcoded numbers for both the score math and the reason strings. Callers select a mode simply by passing a different `SCORING_MODES[...]` entry in, with no duplicated scoring logic anywhere.
