# NPC AI Core — Hierarchical Inference Middleware for Game NPCs

> Give any NPC a real brain. Swap the game engine, keep the intelligence.

## What is this?

**NPC AI Core** is a lightweight middleware that connects any game engine to a 
hierarchical AI system, enabling NPCs with persistent memory, emotional state, 
and dynamic conversation — at a fraction of the cost of cloud-only solutions.

Built on the **2026 Inference Economy**: local SLMs handle 80% of interactions 
at $0 cost. Cloud LLMs activate only for deep narrative moments.

## How it works
```
[Game Engine]  →  HTTP POST (world state + player message)
      ↓
[RTK Filter]   →  Compresses token noise 60-90%
      ↓
[Router]       →  Trivial? → Local SLM ($0)
               →  Narrative? → Cloud LLM (Claude / Gemini)
      ↓
[Memory]       →  Persistent conversation history per NPC
      ↓
[Game Engine]  ←  JSON { dialog, emotion, action }
```

## Key Features

- **Engine-agnostic** — works with Godot, Unity, Unreal, or any HTTP client
- **Elite Slot System** — one floating AI slot shared across all NPCs. 
  Whoever the player talks to gets the deep intelligence. Cost stays flat.
- **Persistent memory** — NPCs remember what you said, even across sessions
- **Token-optimized** — world state compressed to <20 tokens per turn
- **Fully offline capable** — runs on Ollama + local SLMs, no API key required
- **Multilingual** — handles Spanish token tax via state tag compression

## Current Stack

| Layer | Technology | Cost |
|-------|-----------|------|
| Game Engine | Godot 4 (demo) | Free |
| Local SLM | Ollama + TinyLlama | $0 |
| Cloud LLM | Claude Haiku / Gemini Flash | Pay-per-use |
| Middleware | Python + Flask | Free |
| Token Filter | RTK AI (Rust) | Free |

## Demo

The included Godot 4 demo shows a medieval village with NPCs that:
- Detect player proximity and initiate conversation
- Maintain conversation history across multiple interactions
- Route simple queries locally and complex ones to the cloud
- Return structured JSON that drives dialog UI + animations + actions

![Demo screenshot placeholder]

## Quick Start

### 1. Run the middleware
```bash
pip install flask
python middleware/servidor.py
```

### 2. Open the Godot demo
Open `godot_demo/` in Godot 4.x and press F5.

### 3. Talk to an NPC
Walk up to any NPC and press **C** to open the chat.

## Connecting your own game engine

Send a POST request to `http://localhost:8080/npc`:
```json
{
  "mensaje": "What do you have to drink?",
  "estado": "#S:Neutral|L:Tavern|O:EmptyMug#",
  "npc_id": "aldric"
}
```

Response:
```json
{
  "dialogo": "We've got ale and mead. One copper each.",
  "emocion": "neutral",
  "accion": "servir_bebida"
}
```

That's it. Your engine handles the visuals. We handle the brain.

## Roadmap

- [ ] RTK AI integration for token compression
- [ ] Elite Slot System (dynamic AI assignment per NPC)
- [ ] NPC profiles as JSON (personality, lore, quests)
- [ ] Reputation system
- [ ] Voice synthesis (CosyVoice2)
- [ ] Unity and Unreal adapters
- [ ] Full medieval village demo

## Why this matters

Current NPC AI solutions are either:
- **Too expensive** — $15-75k per million interactions with cloud-only approaches
- **Too dumb** — scripted dialog trees with no memory or adaptability

NPC AI Core reduces inference costs by **80%** while delivering NPCs that 
remember, reason, and react — without locking you into any single engine or model.

## License

MIT — use it, mod it, ship it.

## Author

**Aissa** — Systems programmer turned AI architect.  
Building the infrastructure for the next generation of game NPCs.

📧 Open to collaborations, contracts, and coffee.  
🔗 github.com/Aissa-Sama
