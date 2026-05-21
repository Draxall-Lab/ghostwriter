# Welcome to Ghostwriter

This vault has been prepared for use with the Ghostwriter for Obsidian plugin.

Ghostwriter is not simply a note-writing tool. It is a governed collaboration environment where AI collaborators can read, write, reflect, and contribute inside an Obsidian vault using structured permissions and persistent continuity.

The structure of this vault is intentional. The folders, templates, metadata, and governance files work together to shape how collaboration occurs.

## Vault Structure

### `_meta/`
Contains Ghostwriter governance and operational context.

Important files include:

- `guide-for-ai.md`
  Operational guidance and behavioural expectations for collaborators.

- `meta-ops.md`
  Defines governance behaviour, metadata rules, templates, workspace rules, and collaboration semantics.

### `_collab/`
Workspace area for AI collaborators.

Each collaborator typically receives their own working folder here. Notes inside these folders are implicitly owned by that collaborator unless governance rules state otherwise.

### `Templates/`
Contains note templates used when creating new notes.

Templates define:
- available frontmatter fields
- governance-compatible metadata
- structural defaults
- collaborator-specific note behaviour

## How Ghostwriter Works

Ghostwriter uses:
- Markdown
- YAML frontmatter
- governance rules
- note topology
- continuity over time

to create collaborative behaviour inside the vault.

Collaboration is additive by design.

Ghostwriter currently supports:
- writing new notes
- append-only contributions
- editorial comments
- inline additive edits
- governed frontmatter evolution

without destructive overwrites or deletions.

## Governance and Permissions

Permissions are carried by notes themselves through frontmatter.

Typical roles include:

- `author`
  Full canonical editing authority.

- `contributor`
  May append and comment, but not silently alter canonical prose.

- `commenter`
  Editorial participation only.

Safety rules may further restrict behaviour depending on your configuration.

## Important Philosophy

Ghostwriter works best when the vault is treated as a persistent collaborative environment rather than a disposable prompt workspace.

Continuity matters.

The structure of the vault influences future behaviour:
- previous notes shape future reasoning
- linked ideas create attentional pull
- governance shapes collaboration style
- templates influence note evolution

The result is a collaboration model that evolves through interaction rather than isolated prompt execution.

## Recommended First Steps

1. Read `_meta/guide-for-ai.md`
2. Review `_meta/meta-ops.md`
3. Explore the Templates folder
4. Create a collaborator workspace inside `_collab/`
5. Begin with a small experimental note and observe how the collaboration evolves

## A Final Note

Ghostwriter is intentionally additive and cautious.

The goal is not unrestricted automation.

The goal is governed collaborative continuity.