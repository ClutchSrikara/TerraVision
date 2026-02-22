# 🏗️ TerraVision
### Bringing Spatial Intelligence to the Skeleton of the Building
**Ironsite × UMD Startup Shell Hackathon · February 2026**

## Inspiration

Construction mistakes are expensive, and they almost always happen for the same reason: someone looks at a blueprint, looks at a messy job site, and just starts building. If a wall ends up framed a foot to the left, or the wrong materials go in, nobody notices until weeks later when it costs thousands of dollars to tear out and redo.

We wanted to build something that catches those mistakes before they happen.

A second set of eyes that looks at the plan, looks at the room, and tells the crew exactly where things stand.

---

## What It Does

TerraVision compares what **should be built** with what **actually got built**.

You upload:
- A blueprint image **or** an IFC model  
- Materials specifications  
- A photo of the job site  

And you receive, in seconds:

- 📊 Overall completion percentage  
- 📋 A live audit of what is done and what is missing  
- ⚠️ An issues log flagging errors down to the measurement  
- 🛠️ A prioritized list of exactly what the crew needs to do next  
- 🧠 A plain English action plan  

---

## How We Built It

The app runs a four-stage pipeline:

### 1. Blueprint Parsing (OpenCV)
OpenCV reads the blueprint and converts every wall, opening, and dimension into structured 2D coordinate data.

### 2. Site Detection (YOLOv8)
YOLOv8 scans the site photo and detects what is physically present in the frame.

### 3. Spatial Diff Engine
Our diff engine compares the blueprint dataset with the detected site dataset and flags every gap and mismatch.

### 4. LLM Reasoning and Action Planning Layer
Claude takes those mismatches and converts them into a human-readable action plan.

Everything is wrapped in a **Streamlit web application** that works on any device directly on site.

---

## Challenges We Ran Into

The sponsor provided first-person camera footage from Ironsite workers on site, and our first instinct was to build around that.

The problem was that the footage was shot from arbitrary angles and rarely captured the full context of what was being built, making it very hard to extract reliable spatial data.

We made the call early to pivot to still photos paired with blueprints, which gave us a much cleaner input to work with.

The other big challenge was the spatial mismatch itself:

- A blueprint is a perfect 2D bird's-eye drawing  
- A site photo is a distorted 3D snapshot  

Getting those two formats to align accurately required significant iteration on our diff logic.

We also realized that finding real construction blueprints online is surprisingly difficult. They are not publicly available like other datasets, which made testing and validation harder than expected.

---

## Accomplishments We're Proud Of

- We went from idea to working pipeline in the first day.
- The app accepts two completely different input formats:
  - Standard blueprint images
  - IFC models (industry standard format used by real construction firms)
- We built a working AR prototype where structural and systems data from the IFC model is anchored directly onto the physical space.
- The app does not just flag problems — it explains them in plain language that a worker can act on immediately.

---

## What We Learned

The hardest part of this problem is not detecting objects or reading blueprints.

It is the translation layer between the two.

A model can find a stud in a photo.
OpenCV can find a line on a blueprint.

But connecting those two things to understand actual construction progress requires a dedicated reasoning step.

We also had to solve a deceptively simple problem:

How does the app know which part of the building it is looking at?

Are we in the kitchen or the living room?
Which section of the blueprint applies?

We designed a QR marker system to solve this:

- Physical QR markers placed around the site  
- Each marker encodes room and blueprint section data  
- The app automatically identifies which portion of the plan corresponds to the photo  

We also learned that real construction blueprints are surprisingly hard to find online, which highlights how closed-off and analog the industry still is.

---

## What's Next for TerraVision

The immediate priority is fully implementing the QR marker anchoring system so room identification becomes automatic rather than manual.

Beyond that, we want to:

- Close the feedback loop with real-time progress tracking  
- Provide managers with trend analysis instead of static snapshots  
- Expand the AR prototype into a full on-site tool  

The long-term vision is a system where workers can see the digital blueprint anchored directly onto the physical space in front of them.

---

## Tech Stack

- OpenCV
- YOLOv8
- Custom Spatial Diff Engine
- Claude (LLM reasoning layer)
- Streamlit
- IFC model support

---



## Project Structure 

```
TerraVision/
│
├── app.py                        ← Streamlit demo UI
├── test_run.py                   ← CLI test runner
├── requirements.txt
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── blueprint.py        ← OpenCV blueprint processing
│   ├── photo.py            ← YOLOv8 site photo detection
│   ├── diff.py             ← Three-way spatial diff
│   ├── claude.py           ← Claude spatial reasoning
│   └── pipeline.py               ← Orchestrator (calls all 4 steps)
│
└── data/
    ├── inputs/
    │   ├── blueprint.jpg          
    │   ├── site_partial.jpg       
    │   └── materials_manifest.txt
    └── outputs/                   ← results saved here
```

---

## Setup

```bash
# 1. Clone
git clone https://github.com/ClutchSrikara/TerraVision.git
cd TerraVision
# 2. Install dependencies
pip install -r requirements.txt
# 3. Set your API key
cp .env.example .env
# Edit .env and add your Anthropic key
# OR export directly:
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

## Run

**Option A — Streamlit UI (for demo):**
```bash
streamlit run app.py
```
Open http://localhost:xxxx

**Option B — CLI (for testing):**
```bash
# First add your images to data/inputs/
python test_run.py
```

---

## Pipeline

```
Blueprint image  ──┐
Site photo       ──┼──► Step 1: OpenCV blueprint processing
Materials text   ──┘         ↓
                         Step 2: YOLOv8 photo detection
                             ↓
                         Step 3: Three-way spatial diff
                             ↓
                         Step 4: Claude reasoning
                             ↓
                     Progress % + Gap analysis + Materials + Next steps
```

