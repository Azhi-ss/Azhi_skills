# OpenAI Skills Export

This manifest records the available skill folders found at `/home/oai/skills` in the current environment.

## Skill folders

- `docx/` — DOCX creation/editing/redline/comment workflows and helper scripts.
- `pdfs/` — PDF creation/editing/extraction/redaction/conversion workflows and helper scripts.
- `slides/` — PowerPoint/slide generation and editing workflows, pptxgenjs helpers, artifact tool docs, and templates.
- `spreadsheets/` — spreadsheet creation/editing/analysis workflows with artifact_tool/openpyxl guidance.

## Local inventory summary

The local directory contained approximately 124MB of files:

- Text/code/docs: skill definitions, task guides, Python scripts, JavaScript helpers, Markdown specs, package manifests, and licenses.
- Large binary assets: slide templates and example images under `slides/slide_templates/` and `slides/artifact_tool/examples/`.

## Top-level files present locally

```text
/home/oai/skills/spreadsheets/SKILL.md
/home/oai/skills/spreadsheets/API_QUICK_START.md
/home/oai/skills/spreadsheets/templates/financial_models.md
/home/oai/skills/spreadsheets/LICENSE.txt
/home/oai/skills/slides/SKILL.md
/home/oai/skills/slides/LICENSE.txt
/home/oai/skills/docx/SKILL.md
/home/oai/skills/docx/render_docx.py
/home/oai/skills/docx/LICENSE.txt
/home/oai/skills/pdfs/SKILL.md
/home/oai/skills/pdfs/LICENSE.txt
```

## Binary assets noted but not expanded in this manifest

The local `slides/slide_templates/` folder included large `.pptx` template files and an `Overview.png`; `slides/artifact_tool/examples/` included example images and a starter deck.

## Suggested repository layout

```text
openai-skills/
├── docx/
├── pdfs/
├── slides/
└── spreadsheets/
```

## Export note

I verified the connected GitHub repository `Azhi-ss/Azhi_skills` is writable from this session. This manifest is a lightweight first commit documenting the skills inventory. The full text/code export should be committed as normal files or as a compressed archive from an environment with direct Git access, because the current GitHub connector accepts text content directly but cannot stream large local binary files from `/home/oai/skills`.
