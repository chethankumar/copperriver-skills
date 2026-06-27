---
name: hyperframes
description: "Build animated video compositions using plain HTML + CSS + GSAP. The CLI (npx hyperframes render index.html) renders to MP4. Replaces the default video-artifact workflow."
version: 1.0.0
category: media
source: copperriver
---

# Hyperframes

Build animated video compositions using **plain HTML + CSS + GSAP**. The CLI (`npx hyperframes render index.html`) renders to MP4.

**HyperFrames replaces the default video-artifact workflow.** No React, no Babel, no starter components.

---

## Workflow

1. **You** → brand identity, scene content, layout, first-pass animations, shader choices
2. **User** → downloads ZIP, runs `npx hyperframes render`
3. **Claude Code** (or you again) → polish: ease curves, stagger timing, scene durations, mid-scene activity, shader swaps

You produce a **valid first draft** — structurally sound, full motion, ready to render. Not a slide deck.

---

## Step 1: Understand the Brief

**Gate:** You can name the subject, duration, aspect ratio, and at least one source of visual direction.

**Inputs, in order of reliability:**
1. **Attachments** — screenshots, PDFs, brand guides. Mine for palette, type, tone.
2. **Pasted content** — hex codes, typefaces, copy, scripts.
3. **Research** — web search the brand. Static pages (blogs, press, Wikipedia) work. SPAs return empty — pivot to blog/press.
4. **URLs** — start there, expand outward.

**If the brief is sparse** (no attachment, hex/typeface, named aesthetic, known brand, or "surprise me"): ask **one** short clarifying question with concrete options. Wait for reply.

---

## Step 2: Pick a Skeleton

**Gate:** A working `index.html` exists with palette + typography on `:root`. Preview renders.

### Video Type → Skeleton

| Type | Duration | Scenes | Skeleton |
|------|----------|--------|----------|
| Social reel (9:16) | 10-15s | 5-7 | Skeleton A |
| Launch teaser (16:9) | 15-25s | 7-10 | Skeleton B |
| Product explainer (16:9) | 30-60s | 10-18 | Skeleton C |
| Cinematic title (16:9) | 45-90s | 7-12 | Skeleton D |

### Fill `:root` Immediately

```css
:root {
  /* === FILL: Your brand identity === */
  --bg: #0a0a0d;
  --ink: #f5f5f7;
  --accent: #7c6cff;
  --muted: #5a6270;
  --accent-dim: #3d3680;
  --font-display: "Space Grotesk", sans-serif;
  --font-data: "JetBrains Mono", monospace;
}
```

### Anti-Monoculture

**Banned fonts:** Inter, Inter Tight, Roboto, Open Sans, Noto Sans, Lato, Poppins, Outfit, Sora, Fraunces, Playfair Display, Cormorant Garamond, EB Garamond, Syne, Cinzel, Prata, Bodoni Moda, Nunito, Source Sans, PT Sans, Arimo.

**Banned pairings:** Fraunces + JetBrains Mono, Inter + anything, Playfair + Lato.

**Question defaults:** gradient text, cyan-on-dark, pure `#000`/`#fff`, identical card grids, left-edge accent stripes, everything centered with equal weight.

Pick a real typeface pair. **Weight contrast must be dramatic** (300 vs 900, not 400 vs 700). Video sizes: 60px+ headlines, 20px+ body, 16px+ labels.

---

## Step 3: Fill Scenes

**Gate:** Every scene has visible content, at least 2 animation patterns, and mid-scene activity. No static slides.

### 3a. Scene Content

Put text, images, layout **inside `.scene-content`**:

```html
<div class="scene-content">
  <h1 id="s3-title" class="display">$1.9 Trillion</h1>
  <p id="s3-sub" class="body-text">processed annually</p>
  <div id="s3-bar-chart">...</div>
</div>
```

Keep decoratives (glows, grain, vignette) **outside** `.scene-content`, inside the scene div directly.

### 3b. Entrance Animations

Add `tl.from()` tweens in the timeline block for that scene. Animate FROM offscreen/invisible TO final position:

```js
// === SCENE 3 ===
tl.from("#s3-title", { y: 40, autoAlpha: 0, duration: 0.6, ease: "power3.out" }, 10.3);
tl.from("#s3-sub", { y: 20, autoAlpha: 0, duration: 0.5, ease: "power2.out" }, 10.7);
tl.from("#s3-bar-chart", { scaleY: 0, transformOrigin: "bottom", duration: 0.8, ease: "expo.out" }, 11.0);
```

**Offset first tween 0.1-0.3s into the scene.** Zero-delay entrances feel like jump cuts.

### 3c. Mid-Scene Activity (the differentiator)

Every visible element must keep moving AFTER its entrance. A still element on a still background is a JPEG with a progress bar. Use at least 2 patterns per scene.

| Element | Mid-scene motion | Pattern |
|---------|-----------------|---------|
| Stat / number | Counter animates 0 → target | Counter animation |
| SVG line / path | Draws itself in real-time | SVG stroke draw |
| Title / wordmark | Characters enter one by one | Character stagger |
| Logo / lockup | Subtle vertical drift | Breathing float |
| Chart / bars | Bars fill sequentially | Bar chart fill |
| Image / screenshot | Slow zoom `scale: 1 → 1.03` | Ken Burns |
| Accent / highlight | Sweep across text | Highlight sweep |
| Background glow | Opacity pulse | Glow pulse |

### 3d. Scene Duration

| Display text | Min duration |
|-------------|--------------|
| No text (hero, icon) | 1.5-2s |
| 1-3 words (kicker, number) | 2-3s |
| 4-10 words (headline + subhead) | 3-4s |
| 11-20 words (sentence or two lines) | 4-6s |
| 21-35 words (paragraph) | 6-8s |
| 35+ words | Split into two scenes |

**Hard ceiling: 5s per scene** unless you name a specific reason.

When changing a scene's duration, update `data-start` on subsequent scenes to keep them tiled end-to-end. Also update the root's `data-duration`.

### 3e. Vary Eases

Use at least 3 different eases per scene.

| Feeling | Ease | Duration |
|---------|------|----------|
| Smooth | `power2.out` | 0.4-0.6s |
| Snappy | `power4.out` | 0.2-0.3s |
| Bouncy | `back.out(1.6)` | 0.3-0.5s |
| Dramatic | `expo.out` | 0.3-0.5s |
| Dreamy | `sine.inOut` | 0.5-0.8s |
| Mechanical | `steps(5)` | 0.3-0.5s |

---

## Step 4: Transitions

### The Professional Rule: Most Cuts Are Hard Cuts

~95% of scene changes are hard cuts. Shader transitions are for 2-3 key moments only — hero reveal, energy shift, CTA landing. Using a shader on every cut is the video equivalent of bolding every word.

### Three Transition Types

**Hard cut (default):** No transition code needed. Scene N disappears, scene N+1 appears. Entrance animations do all the visual work.

**Shader transition (2-3 per video):** Pre-wired in skeleton at key positions. HyperShader captures both scenes as textures and composites them pixel-by-pixel via WebGL.

**When to use shaders vs hard cuts:**

| Use shader for | Use hard cut for |
|---------------|-----------------|
| Hero reveal / product unveil | Connective scenes between features |
| Major energy shift or act break | Rapid-fire lists or stats |
| CTA / final brand moment | 3+ consecutive quick scene changes |
| Any moment the music punctuates | Scenes where pacing should feel fast |

**Rule of thumb:** A 6-8 scene video wants **2 shader transitions**, rest hard cuts.

### Shader Catalog

| Shader | Energy |
|--------|--------|
| `domain-warp` | Calm, editorial |
| `cross-warp-morph` | Calm, editorial |
| `light-leak` | Calm, editorial |
| `cinematic-zoom` | Medium, professional |
| `whip-pan` | Medium, professional |
| `sdf-iris` | Medium, professional |
| `glitch` | High, aggressive |
| `chromatic-split` | High, aggressive |
| `ridged-burn` | High, aggressive |
| `gravitational-lens` | Ethereal, mysterious |
| `ripple-waves` | Ethereal, mysterious |
| `swirl-vortex` | Ethereal, mysterious |
| `thermal-distortion` | Ethereal, mysterious |
| `flash-through-white` | Any (punctuation) |

### Adjusting Transition Timing

When changing scene durations, recalculate:
```
transition.time = scene_boundary - (transition.duration / 2)
```

Example: scene-3 ends at 8s, transition duration 0.5s → `time: 7.75`

**Minimum transition duration: 0.3s.** Sweet spot is 0.5s.

---

## Step 5: Deliver

1. Create a project folder with `index.html` and `preview.html`
2. Run `npx hyperframes lint` to verify structural validity
3. Package as ZIP for the user to download
4. User runs `npx hyperframes render index.html` locally to generate MP4

---

## Common Animation Patterns

### Counter Animation
```js
var counterObj = { v: 0 };
tl.to(counterObj, {
  v: 1900000000000,
  duration: 2.0,
  ease: "power2.out",
  onUpdate: function () {
    document.getElementById("s3-stat").textContent = "$" + (counterObj.v / 1e12).toFixed(1) + "T";
  },
}, 10.5);
```

### SVG Stroke Draw
```html
<svg viewBox="0 0 400 200" style="position:absolute; bottom:100px; left:160px;">
  <path id="s2-line" d="M 0 100 Q 200 20 400 100"
    stroke="var(--accent)" stroke-width="3" fill="none"
    stroke-linecap="round" stroke-dasharray="440" stroke-dashoffset="440" />
</svg>
```
```js
tl.to("#s2-line", { strokeDashoffset: 0, duration: 1.0, ease: "power2.out" }, 3.5);
```

### Character Stagger
```html
<h1 class="display" style="font-size:120px;">
  <span class="char">N</span><span class="char">O</span><span class="char">R</span>
  <span class="char">T</span><span class="char">H</span>
</h1>
```
```js
tl.from(".char", {
  y: 60, autoAlpha: 0, duration: 0.5, ease: "power3.out",
  stagger: { each: 0.12, from: "start" }
}, 29.5);
```

### Breathing Float
```js
tl.to("#s4-logo", {
  y: -5, duration: 1.5, ease: "sine.inOut", yoyo: true, repeat: 1
}, 15.0);
```

### Bar Chart Fill
```js
["#bar1", "#bar2", "#bar3", "#bar4"].forEach(function (sel, i) {
  tl.from(sel, {
    scaleY: 0, transformOrigin: "bottom", duration: 0.6, ease: "expo.out"
  }, 11.0 + i * 0.15);
});
```

### Ken Burns (Image Zoom)
```js
tl.to("#s6-image", { scale: 1.03, duration: sceneLength, ease: "none" }, sceneStart);
```

### Highlight Sweep
```css
#s5-headline {
  background: linear-gradient(var(--accent), var(--accent)) no-repeat 0 85% / 0% 30%;
}
```
```js
tl.to("#s5-headline", { backgroundSize: "100% 30%", duration: 0.6, ease: "power2.out" }, 22.0);
```

### Orbit / Rotation
```js
tl.to("#orbit-dot", {
  rotation: 360, duration: 3.0, ease: "none", transformOrigin: "50% 200px"
}, 8.5);
```

### CSS Radial-Gradient Grain (Safari-safe)
```css
.grain {
  position: absolute; inset: 0; pointer-events: none; z-index: 50; opacity: 0.18;
  background-image:
    radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1.2px),
    radial-gradient(rgba(0, 0, 0, 0.18) 1px, transparent 1.2px);
  background-size: 3px 3px, 5px 5px;
  background-position: 0 0, 1px 2px;
  mix-blend-mode: overlay;
}
```

**NEVER use SVG filter `data:image/svg+xml` grain** — it taints html2canvas in Safari, breaking every shader transition.

---

## Skeletons

See `skeletons/` subdirectory for complete HTML skeletons:
- `skeleton-a.html` — Social reel (9:16, 10-15s, 5-7 scenes)
- `skeleton-b.html` — Launch teaser (16:9, 15-25s, 7-10 scenes)
- `skeleton-c.html` — Product explainer (16:9, 30-60s, 10-18 scenes)
- `skeleton-d.html` — Cinematic title (16:9, 45-90s, 7-12 scenes)

---

## What NOT to Touch

- The `<script>` loading order
- `window.__timelines` initialization
- The `.scene.clip` class on scene containers
- The `.scene-content` wrapper inside each scene
- The `preview.html` structure

---

## References

- Full docs: https://hyperframes.heygen.com/
- Core composition contract: https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/SKILL.md
- Motion principles: https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/references/motion-principles.md
- Typography: https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/references/typography.md
- Transitions: https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/references/transitions.md
- Captions: https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/references/captions.md
