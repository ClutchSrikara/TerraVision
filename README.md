# 🏗️ TerraVision
### AI Construction Progress Analyzer
**Ironsite × UMD Startup Shell Hackathon · February 2026**

---

## What It Does

Upload a **blueprint**, a **site photo**, and a **materials manifest** — TerraVision tells you:

- 📊 **How complete** the construction is (%)
- ❌ **What's missing** vs the blueprint
- ⚠️ **What's wrong** (misaligned, wrong size, wrong count)
- 📦 **What materials** are still needed
- 🔨 **What to do next** (prioritized)

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
    │   ├── blueprint.jpg          ← your blueprint image (add this)
    │   ├── site_partial.jpg       ← partial site photo (add this)
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
Open http://localhost:8501

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

