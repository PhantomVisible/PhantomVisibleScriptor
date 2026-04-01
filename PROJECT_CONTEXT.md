# 🧠 Phantom Visible Scripter - Project Context

## 🎯 Objective
Build a local-first AI system that generates high-retention YouTube scripts (2000–2500 words) using a multi-agent pipeline.

The system must:
- Run fully locally (Ollama)
- Require no paid APIs
- Produce structured, engaging scripts
- Allow iterative improvement via agents

---

## 🧩 Architecture

Pipeline:

1. Research Agent
   - Uses DuckDuckGo search
   - Summarizes and extracts insights

2. Planning Agent
   - Creates structured content plan
   - Defines sections and flow

3. Scripting Agent
   - Writes full script (target: 2000–2500 words)
   - Follows strict storytelling structure

4. Critic Agent
   - Reviews script quality
   - Scores:
     - Hook strength
     - Clarity
     - Engagement
   - Suggests improvements

5. (Planned) Expansion Agent
   - Expands weak/short sections
   - Ensures word count targets are met

---

## 🤖 Models Used

- LLaMA 3 8B → Planning
- Mistral 7B → Script writing
- (Optional future) Qwen → Research

All models run via Ollama.

---

## ⚙️ Key Constraints

- No external APIs
- Must work via CLI
- Modular agent-based design
- Prompts stored in `/prompts`
- Each agent must be independently replaceable

---

## 🚀 Current Priorities

1. Improve script length consistency
2. Enhance critic agent scoring system
3. Add expansion agent
4. Improve prompt engineering

---

## 🧠 Design Philosophy

- Small models → specialized roles
- Never rely on one model for everything
- Prefer iterative refinement over single-pass generation

---

## ⚠️ Known Issues

- Scripts too short (700–1200 words)
- Some sections lack depth
- Model ignores length constraints

---

## ✅ Definition of Done

A successful output:
- 2000–2500 words
- Strong hook
- Engaging storytelling
- Clear structure
- Minimal repetition    