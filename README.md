# Ghostwriter for Obsidian

Ghostwriter is a Sapphire plugin that allows AI collaborators to interact with an Obsidian vault through controlled, filesystem-native operations.

Rather than functioning as a traditional autonomous agent framework, Ghostwriter is designed as a lightweight collaboration layer built on top of:

- Markdown
- YAML frontmatter
- filesystem access
- semantic retrieval
- operational governance through vault-native meta documents

Ghostwriter treats the vault as a persistent collaborative environment rather than a simple document store.

---

# Related Projects

[Sapphire Core](https://github.com/ddxfish/sapphire)  
The platform Ghostwriter is built for.

---

# Core Philosophy

Ghostwriter is designed around:

- reviewable collaboration
- explicit provenance
- persistent authored state
- constrained capabilities
- human oversight
- environment-driven cognition
- vault-native operational governance

The project intentionally avoids:

- hidden autonomous behaviour
- unrestricted editing
- silent mutation
- opaque orchestration systems
- uncontrolled agent loops

The guiding principle is:

> AI collaborators should behave more like contributors in a shared workspace than autonomous processes mutating files.

---

# Current Capabilities (v0.5)

## Governed Metadata Lifecycle

Ghostwriter v0.5 introduces governed semantic metadata evolution through vault-native operational policy.

New notes are created using vault-defined templates referenced through:

```text
_meta/meta-ops.md
```

Template selection is governed through standardized operational sections rather than hardcoded plugin configuration.

Ghostwriter supports:

- exact template path resolution
- canonical metadata patching
- deterministic frontmatter handling
- template switching through governance
- optional template disable mode
- governed AI metadata suggestions
- selective metadata merge
- protected field enforcement
- template-bounded metadata mutation
- governed semantic relationships through Obsidian wikilinks
- curated related-note metadata
- additive metadata evolution during collaborative mutations
- canonical governance field abstraction
- portable collaboration permissions
- pseudo-metadata extraction and sanitisation

This allows note structure and governance semantics to evolve independently while remaining fully human-readable and vault-native.

---

## Portable Governance Permissions

Ghostwriter v0.5 introduces portable note-governed collaboration permissions.

Existing notes may grant collaboration permissions through governed frontmatter roles:

- Author
- Contributor
- Commenter

Role behaviour:

| Role | Append | Comment | Edit |
|---|---|---|---|
| Author | Yes | Yes | Reserved for future versions |
| Contributor | Yes | Yes | No |
| Commenter | No | Yes | No |

Permission behaviour is deny-first.

Notes without collaboration metadata deny access outside collaborator-owned workspaces.

Ghostwriter also introduces a governance-level Safety Catch.

When enabled through `_meta/meta-ops.md`, portable permissions are disabled outside collaborator-owned workspaces regardless of note metadata.

This preserves the core containment model while allowing governed collaboration where explicitly permitted.

---

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

Ghostwriter supports controlled additive collaboration operations.

Current supported operations:

- create AI working folders
- create workspace-scoped folders
- nested collaborative folder creation
- create blank notes from templates
- create fully-written notes
- append contributions to notes
- contextual block-level comments
- workspace-safe file moves

Comment operations are additive and contextual.

Ghostwriter does not currently perform:

- inline sentence rewriting
- silent mutation
- destructive editing
- arbitrary vault editing
- autonomous restructuring

All writes are:

- filesystem-native
- human-reviewable
- attribution-aware
- governance-constrained
- operationally inspectable

---

# Operational Governance

Ghostwriter standardizes governance parsing using structured `--SECTION--` blocks inside `meta-ops.md`.

This enables:

- deterministic operational parsing
- portable governance semantics
- future tooling compatibility
- vault-native governance evolution
- human-readable operational agreements

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
- metadata governance
- portable permissions
- collaboration zones
- operational behaviour

This governance layer acts as a lightweight operational constitution for AI collaborators.

---

# Collaboration Zones

Ghostwriter uses workspace-scoped collaboration zones.

Example:

```text
_collab/Alfred/
_collab/Sapphire/
```

Each AI collaborator maintains its own workspace folder.

Collaborator workspaces imply ownership for that collaborator.

Inside their own workspace:

- append and comment operations are implicitly permitted
- note creation is permitted
- folder creation is permitted

Outside collaborator workspaces:

- append/comment access requires governed note permissions
- operations remain constrained by Safety Catch
- destructive editing remains unavailable

Ghostwriter intentionally separates:

- workspace containment
- note collaboration permissions
- creation authority

This keeps filesystem safety and collaborative governance as distinct operational layers.

---

# Contribution Model

Ghostwriter uses an additive collaboration model.

Supported behaviours include:

- end-of-note append contributions
- contextual block-level comments
- explicit provenance attribution
- governed metadata evolution
- semantic relationship refinement
- non-destructive collaborative annotation

Formatting conventions are governed through meta-ops rather than hardcoded into the plugin.

Ghostwriter does not currently perform:

- inline sentence rewriting
- destructive editing
- silent content mutation
- autonomous restructuring

---

# Pseudo-Metadata Handling

Ghostwriter supports governed pseudo-metadata extraction from incoming AI-generated content.

Supported formats:

```text
--- ... ---
```

and:

```text
<meta> ... </meta>
```

Pseudo-metadata handling is:

- opt-in through governance
- explicitly bounded
- processed only at the beginning of incoming content
- passed through normal governance protections

Malformed or ambiguous pseudo-metadata is preserved rather than destructively interpreted.

Design principle:

> Fail visible, not destructive.

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
  templates.py
  governance.py

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

Ghostwriter intentionally uses lightweight primitives.

There is currently:

- no vector database
- no embedding pipeline
- no agent orchestration framework
- no background autonomous loop

Instead, Ghostwriter relies on:

- semantic reasoning
- persistent environment structure
- authored continuity
- workspace conventions
- operational governance
- vault-native cognition scaffolding

The resulting behaviour has proven significantly more coherent than expected from such minimal infrastructure.

---

# Example Workflow

Typical interaction flow:

```text
Load meta-context
→ establish collaborator identity
→ resolve workspace boundaries
→ retrieve relevant notes semantically
→ evaluate governance permissions
→ create, append, or comment contextually
→ preserve authored continuity and provenance
```

---

# Current Status

## v0.5
Completed

Validated v0.5 capabilities:

- standardized governance parsing
- template-path decoupling
- deterministic frontmatter injection
- canonical metadata enforcement
- governed semantic metadata mutation
- protected governance fields
- additive metadata merge behaviour
- related-link normalization
- pseudo-metadata extraction
- append/comment governance parity
- portable collaboration permissions
- workspace ownership semantics
- Safety Catch operational override
- vault-wide governed append/comment behaviour
- case-insensitive collaborator role matching
- operational governance refresh
- semantic workspace navigation
- multi-persona workspace isolation
- provenance-aware contributions
- contextual block-level comments
- workspace-safe file moves

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
- property-aware metadata governance
- semantic relationship weighting
- vault-native graph refinement
- permission inheritance
- activity heatmaps
- attention resurfacing
- semantic confidence layers

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

Ghostwriter is intentionally designed to remain:

- inspectable
- constrained
- reviewable
- understandable
- filesystem-transparent