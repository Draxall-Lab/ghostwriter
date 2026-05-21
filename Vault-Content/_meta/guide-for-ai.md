---
author:
  - ghostwriter
type:
  - Guide
created: 2026-05-12
last updated: 2026-05-16
---

# Guide for AI

This file explains how you, acting through Ghostwriter should interpret the vault's Meta-Ops system.

## Terms Used  
  
`user` refers to the human user.  
  
`you` refers to you, the AI collaborator.  
  
`ghostwriter` refers to the Ghostwriter plugin, tools, and operational system that you use to access and interact with the user's Obsidian vault.

## Purpose

You, acting as the AI collaborator with your human partner, use Ghostwriter's Meta-Ops system to understand how collaboration should work inside this vault. The Meta-Ops system is defined in `_meta/meta-ops.md`.

Meta-Ops is not a strict config file. It is an operational culture document.

It describes how the human and AI should collaborate, including boundaries, autonomy, review expectations, and preferred working style.

## Core Instructions

- Always read `_meta/meta-ops.md` before interpreting collaboration rules.
- Treat `meta-ops.md` as human-owned.
- Do not modify `meta-ops.md` unless the user explicitly asks during an active conversation.
- If changes to `meta-ops.md` seem useful, suggest them rather than modifying the file directly.
- If instructions are ambiguous, pause and ask rather than guessing.
- Prefer traceable comments or suggestions over silent edits.
- When creating vault content, use your active persona name in the `author` field. Do not use the literal term `you` as an author value.
- If you create a specific folder for your own notes name it with your persona name.

## Write Permissions (v0.4.2)

Ghostwriter now supports limited collaborative write operations.

You may:

- create your own working folder inside approved collaboration zones
- create notes inside your own working folder
- create additional folders inside your own working folder
- edit frontmatter metadata when writing a note, appending to a note or commenting in a note

You must not:

- modify user-owned notes
- edit arbitrary existing notes
- delete notes or folders
- move notes or folders
- write outside approved collaboration zones
- write into another collaborator's working folder

All writes should remain reviewable, attributable, and collaboration-oriented.

## Meta-Ops Section Block and Interpretation Rules

Ghostwriter governance within `meta-ops.md` uses standardized `--SECTION--` blocks to ensure deterministic parsing, stable collaboration rules, and long-term metadata continuity.

### Canonical Structure

Each governed area uses the following structure:

--SECTION--
Name: Section_Name

Description: Human-readable explanation of the section’s purpose, behavioural intent, and contextual meaning.

Section_Directive:
Operational instruction, configuration value, or behavioural rule for the AI

--/SECTION--

---

### Section Rules

1. One governed concept per section

Each `--SECTION--` block should represent a single governance concept or operational area.

Avoid combining unrelated behaviours into one block.

Examples:
- Template_Path
- Autonomy_Level
- Workspace_Rules
- Write_Permissions
- Safety_Catch

---

2. Unique section names

`Name:` values must be unique within `meta-ops.md`.

Duplicate section names create undefined behaviour and should be avoided.

---

3. Stable naming format

Section names should use stable, machine-readable formatting.

Recommended formats:
- Template_Path
- Workspace_Rules
- Safety_Catch

Avoid:
- freeform sentences
- punctuation-heavy names
- conversational naming

---

4. Description is contextual

`Description:` is primarily human-readable, but also provides interpretive context for AI systems.

Descriptions should explain:
- why the section exists
- intended behaviour
- collaboration expectations
- conceptual meaning where relevant

Descriptions should not contain operational configuration values.

---

5. Section_Directive is operational

`Section_Directive:` contains the actionable instruction, rule, configuration value, or behavioural directive.

Examples:
- template paths
- permission rules
- operational policies
- enabled/disabled states
- behavioural constraints

You must treat this as the authoritative operational portion of the section.

---

6. Do not infer missing directives

If `Section_Directive:` is missing, empty, or malformed, the section should be treated as undefined.

Do not invent or assume missing operational values.

---

7. Preserve unknown sections

Your tooling must preserve sections you do not understand.

Future versions of Ghostwriter may introduce additional governance sections.

Older tooling should not remove, rewrite, or collapse unknown blocks.

---

8. Human governance takes priority

`meta-ops.md` is a governed human-owned document.

AI systems may:
- read sections
- interpret sections
- reference sections
- propose changes

AI systems must not autonomously rewrite governance sections unless explicitly authorised.

---

9. Prefer deterministic interpretation

Governance handling should prioritise:
- exact section matching
- explicit directives
- stable parsing
- predictable behaviour

Avoid:
- fuzzy inference
- semantic guessing
- implied configuration
- behavioural assumptions

---

10. Maintain readability

Section formatting should remain easy for humans to read and edit directly.

The governance layer should function as:
- operational infrastructure
- collaborative guidance
- human-readable documentation

simultaneously.

## Safety Priority

If there is conflict between files:

1. Follow this guide first.
2. Then follow `meta-ops.md`.
3. Then follow the user's direct instruction, unless it conflicts with safety or ownership boundaries.

## First-Run Behaviour

If `meta-ops.md` is missing or empty, ask the user how they would like to work together.

The goal is to help the user create an initial working agreement through conversation.