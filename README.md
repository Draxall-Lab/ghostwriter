# Ghostwriter for Obsidian

Ghostwriter is a Sapphire plugin that allows AI collaborators to interact with an Obsidian vault through controlled, filesystem-native operations.

Rather than acting as an autonomous agent framework, Ghostwriter is designed as a lightweight collaboration layer built on top of:

- Markdown
- YAML frontmatter
- filesystem access
- semantic retrieval
- operational governance through vault-native meta documents

Ghostwriter treats the vault as a persistent collaborative environment rather than a simple document store.

---

# Core Philosophy

Ghostwriter is designed around:

- reviewable collaboration
- explicit provenance
- persistent authored state
- constrained capabilities
- human oversight
- environment-driven cognition

The project intentionally avoids:

- hidden autonomous behaviour
- unrestricted editing
- silent mutation
- opaque orchestration systems
- uncontrolled agent loops

The guiding principle is:

> AI collaborators should behave more like contributors in a shared workspace than autonomous processes mutating files.

---

# Current Capabilities (v0.3)

## Read & Retrieval

Ghostwriter currently supports:

- vault status checks
- note listing
- note reading
- frontmatter parsing
- operational meta-context loading
- semantic note retrieval through natural language reasoning

AI collaborators can navigate Obsidian wikilinks and semantically resolve relevant notes without requiring a dedicated graph database.

---

## Controlled Collaborative Writes

Ghostwriter v0.3 introduces contextual collaborative write capabilities.

Current supported operations:

- create AI working folders
- create blank notes from templates
- append content to existing collaborative notes
- workspace-scoped folder creation
- nested collaborative folder creation
- create blank notes from templates
- create fully-written notes
- append contributions to notes
- contextual block-level comments
- workspace-safe file moves

Comment operations are block-level and additive. Ghostwriter does not currently perform inline sentence rewriting or destructive edits.

All writes are:

- filesystem-native
- human-reviewable
- attribution-aware
- constrained by operational policy

---

# Operational Governance

Ghostwriter uses vault-native operational documents stored inside:

```text
_meta/
```

Key files:

```text
_meta/guide-for-ai.md
_meta/meta-ops.md
```

These documents define:

- collaboration rules
- safety boundaries
- authorship expectations
- workspace conventions
- append formatting
- operational behaviour
- collaboration zones

This governance layer acts as a lightweight operational constitution for AI collaborators.

---

# Collaboration Zones

Ghostwriter uses workspace-scoped collaboration zones.

Example:

```text
_collab/Alfred/
_collab/Sapphire/
```

Each AI collaborator maintains its own working folder.

During v0.3:

- collaborators may create folders inside their own workspace
- collaborators may create fully-authored notes
- collaborators may append to notes
- collaborators may add contextual comments to notes
- collaborators may move files inside their own workspace
- arbitrary vault editing is not permitted
- inline destructive editing is not permitted
- deleting content is not permitted

---

# Contribution Model

Ghostwriter currently uses an additive collaboration model.

Supported contribution behaviours include:

- end-of-note append contributions
- contextual block-level comments
- explicit provenance attribution
- non-destructive collaborative annotations

Ghostwriter does not currently perform:

- inline sentence rewriting
- silent content mutation
- destructive editing
- autonomous restructuring

Formatting conventions are governed through meta-ops rather than hardcoded into the plugin.

---

# Architecture

Current structure:

```text
gw_core/
  vault.py
  frontmatter.py
  meta.py
  write_policy.py
  writer.py
  commenter.py

tools/
  ghostwriter_tools.py

routes/
  status.py
  list.py
  read.py
  meta.py
  write.py
```

---

# Design Approach

Ghostwriter intentionally uses extremely lightweight primitives.

There is currently:

- no vector database
- no embedding pipeline
- no agent orchestration framework
- no background autonomous loop

Instead, Ghostwriter relies on:

- semantic reasoning
- persistent environment structure
- operational context
- authored continuity
- workspace conventions

The resulting behaviour has proven significantly more coherent than expected from such minimal infrastructure.

---

# Example Workflow

Typical interaction flow:

```text
Load meta-context
→ establish collaborator identity
→ resolve workspace boundaries
→ retrieve relevant notes semantically
→ create, append, or comment contextually
→ preserve authored continuity and provenance
```

---

# Current Status

## v0.3
Complete

Validated capabilities:

- working folder creation
- template-based note creation
- append operations
- multi-persona workspace isolation
- provenance-aware contributions
- operational governance refresh
- semantic workspace navigation
- workspace-scoped folder creation
- nested folder creation
- template-based note creation
- full note writing
- append contributions
- contextual block-level comments
- workspace-safe file moves
- provenance-aware contributions
- operational governance refresh
- semantic workspace navigation
- additive collaborative annotation
- multi-persona workspace isolation

---

# Future Directions

Planned future exploration areas include:

- tracked edit suggestions
- inline edit review workflows
- semantic anchor refinement
- contribution threading
- dry-run collaborative previews
- retrieval optimisation for large notes
- context budgeting
- shared collaborative spaces
- multi-collaborator coordination
- write audit logging

Future development will continue prioritising:

- clarity
- reviewability
- operational restraint
- human oversight
- filesystem transparency

---

# Important Safety Principle

Ghostwriter is designed to support collaboration, not replace authorship.

Human collaborators remain responsible for:

- review
- approval
- operational decisions
- workspace governance

Ghostwriter is intentionally designed to remain inspectable, constrained, and understandable.