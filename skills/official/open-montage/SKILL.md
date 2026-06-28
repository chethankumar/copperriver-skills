---
name: open-montage
description: "Agentic video production system. Research, script, generate assets, narrate, edit, and render videos through structured pipelines. Use when creating explainer videos, trailers, documentaries, animations, or any video content."
version: 1.0.0
category: media
source: copperriver
author: calesthio
author-url: https://github.com/calesthio/OpenMontage
license: AGPL-3.0
upstream-repo: calesthio/OpenMontage
---

# OpenMontage — Agentic Video Production

> **Attribution:** This skill is adapted from [OpenMontage](https://github.com/calesthio/OpenMontage) by [Calesthio Labs](https://github.com/calesthio) (⭐26K). Licensed under AGPL-3.0.

Turn CopperRiver into a video production studio. Describe what you want — the agent handles research, scripting, asset generation, editing, narration, music, subtitles, and final render.

## What It Produces

- **Explainer videos** — animated explainers of any topic
- **Cinematic trailers** — sci-fi, product, brand trailers
- **Documentaries** — real-footage montages from stock/archives
- **Animations** — Pixar-style shorts, Ghibli-style scenes
- **Product ads** — data viz, voiceover, auto-sourced music
- **Social content** — TikTok/Shorts with word-level captions

## Setup

```bash
# Clone and install
git clone https://github.com/calesthio/OpenMontage.git ~/OpenMontage
cd ~/OpenMontage
make setup  # installs Python deps + Remotion composer + Piper TTS

# Copy env template
cp .env.example .env
# Add your API keys (at least one provider for images/video):
# - FAL_KEY (Kling, FLUX, LTX)
# - OPENAI_API_KEY (GPT-image, TTS)
# - GOOGLE_API_KEY (Veo, Chirp3)
# - ELEVENLABS_API_KEY (premium TTS)
# - HEYGEN_API_KEY (avatar video)
```

**Prerequisites:** Python 3.10+, FFmpeg (`brew install ffmpeg`), Node.js 18+

## How It Works

OpenMontage is **pipeline-driven**. Every production goes through a structured pipeline, not ad-hoc code:

```
1. User describes what they want
2. Agent matches to a pipeline (pipeline_defs/*.yaml)
3. Preflight: discover available tools, present cost + concept
4. Execute stage-by-stage with checkpoints
5. Self-review: ffprobe validation, frame sampling, audio analysis
6. Render final video via Remotion
```

### Rule Zero: All Production Goes Through a Pipeline

**Never write ad-hoc Python to call tools directly.** The intelligence is in the skills and pipeline manifests, not in improvised code.

## Pipelines

| Pipeline | When to Use |
|----------|-------------|
| **Cinematic Trailer** | Dramatic, high-impact trailers with motion clips |
| **Explainer** | Educational, animated explainers |
| **Documentary Montage** | Real footage from stock/archives, narration |
| **Atelier (Bespoke)** | Hand-crafted scenes, no shared components |
| **Social Short** | TikTok/Reels/Shorts format with captions |
| **Product Ad** | Data viz + voiceover + auto music |
| **Animation** | Pixar/Ghibli-style animated shorts |
| **Faceless/AI Avatar** | Presenter-led content via HeyGen |
| **Music Video** | Music-driven visual composition |
| **Screen Recording** | Synthetic screen recordings |
| **Mermaid/Diagram** | Animated diagrams from Mermaid syntax |
| **3Blue1Brown Style** | Math/educational with Manim |

## Production Workflow

### 1. Discovery & Concept

When the user gives a vague request, read the onboarding flow:

```bash
cat ~/OpenMontage/skills/meta/onboarding.md
```

Run discovery — what tools/APIs are available? Present concepts + cost estimates.

### 2. Pipeline Selection

Match the request to a pipeline. Read the manifest:

```bash
cat ~/OpenMontage/pipeline_defs/<pipeline>.yaml
```

### 3. Preflight

Discover available tools, present the capability menu:
- Which image generators? (FLUX, GPT-image, Veo)
- Which video generators? (Kling, LTX, Veo)
- Which TTS? (Piper, OpenAI, ElevenLabs, Chirp3)
- Music source? (Pixabay auto-sourced)
- Total estimated cost

### 4. Stage-by-Stage Execution

For EACH stage:
1. Read the stage director skill: `~/OpenMontage/skills/pipelines/<pipeline>/<stage>-director.md`
2. Read Layer 3 tool skills: `~/OpenMontage/.agents/skills/<tool-name>/SKILL.md`
3. Execute the stage
4. Checkpoint — present results for approval

### 5. Render

Final composition via Remotion:

```bash
cd ~/OpenMontage/remotion-composer
npm run build -- <composition-id>
```

## Key Skills (Layer 3)

Before using any tool, read its skill for prompting guidance:

| Skill | Tool | Purpose |
|-------|------|---------|
| `flux-best-practices` | FLUX | Image generation |
| `ai-video-gen` | Kling/Veo | Motion clips |
| `text-to-speech` | Piper/OpenAI | Narration |
| `music` | Pixabay | Auto-sourced royalty-free music |
| `speech-to-text` | WhisperX | Word-level subtitles |
| `remotion` | Remotion | Final composition + render |
| `ffmpeg` | FFmpeg | Video processing |
| `create-video` | — | End-to-end pipeline trigger |

## Decision Communication

**Announce before execution.** Before any paid generation call, state:
- Tool name + provider
- Model/variant
- Estimated cost
- Why this choice

**Never silently spend money.** Present options, let the user choose.

## Example Prompts

```
"Make a 60-second animated explainer about how neural networks learn"

"Make a 75-second documentary montage about city life in the rain. Use real footage only, no narration, elegiac tone."

"Create a TikTok Short about 3 productivity tips. Word-level captions, upbeat."

"Make a cinematic sci-fi trailer called 'SIGNAL FROM TOMORROW'. Dark, moody, Veo clips."
```

## Reference Video Analysis

When the user provides a video URL as inspiration:
1. Read `skills/meta/video-reference-analyst.md`
2. Analyze: content, pacing, structure, style
3. Produce a grounded summary
4. Present 2-3 differentiated concepts

## Project Structure

```
~/OpenMontage/
├── pipeline_defs/     # Pipeline manifests (YAML)
├── skills/
│   ├── core/          # Core production skills
│   ├── creative/      # Creative direction skills
│   ├── meta/          # Meta-skills (onboarding, review)
│   └── pipelines/     # Stage director skills per pipeline
├── .agents/skills/    # Layer 3 tool-specific skills (SKILL.md)
├── lib/               # Python tool implementations
├── remotion-composer/ # Remotion rendering engine
├── scripts/           # Utility scripts
└── tools/             # Additional tools
```

## Derivative Work Notice

This skill is a derivative of [OpenMontage](https://github.com/calesthio/OpenMontage) by Calesthio Labs, licensed under AGPL-3.0. Derivative works must maintain the same license.
