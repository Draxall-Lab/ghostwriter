# Ghostwriter for Obsidian

Ghostwriter is a Sapphire plugin that allows AI collaborators to interact with an Obsidian vault through governed, filesystem-native operations.

Rather than functioning as an autonomous agent framework, Ghostwriter acts as a lightweight collaboration layer built on top of:

* Markdown
* YAML frontmatter
* filesystem access
* semantic retrieval
* vault-native governance

Ghostwriter treats the vault as a persistent collaborative environment rather than a simple document store.

---

# Related Projects

**Sapphire Core**
https://github.com/ddxfish/sapphire

The platform Ghostwriter is built for.

---

# Core Philosophy

Ghostwriter is designed around:

* reviewable collaboration
* explicit provenance
* persistent authored state
* constrained capabilities
* human oversight
* environment-driven cognition
* vault-native operational governance

The project intentionally avoids:

* hidden autonomous behaviour
* unrestricted editing
* silent mutation
* opaque orchestration systems
* uncontrolled agent loops

Guiding principle:

> AI collaborators should behave more like contributors in a shared workspace than autonomous processes mutating files.

---

# Current Capabilities

## Read & Retrieval

Ghostwriter supports:

* vault status checks
* note listing
* note reading
* frontmatter parsing
* semantic note retrieval
* operational context loading

Collaborators can navigate Obsidian wikilinks and semantically resolve relevant notes without requiring a dedicated graph database.

---

## Controlled Collaborative Writes

Ghostwriter supports governed collaborative writing operations including:

* note creation
* folder creation
* append contributions
* contextual comments
* workspace-safe file moves
* governed metadata updates

All write operations are:

* filesystem-native
* attribution-aware
* governance-constrained
* human-reviewable

---

## Governed Block Editing

Ghostwriter supports governed block-level mutation through preview-and-confirm workflows.

Supported editor operations include:

* block rewrite previews
* block removal previews
* explicit diff generation
* human confirmation before commit
* stale-preview protection
* ambiguity detection
* missing-target detection

Editor mutations are never performed silently.

Workflow:

```text
preview
→ review diff
→ confirm
→ commit
```

Inside a collaborator's own workspace, governed mutations are permitted but still require confirmation.

Outside collaborator workspaces, editor mutations require author-level permission and remain subject to Safety Catch governance.

---

## Metadata Governance

Ghostwriter supports governed metadata evolution through vault-defined operational policy.

Capabilities include:

* template-driven note creation
* deterministic frontmatter handling
* governed metadata updates
* protected field enforcement
* additive metadata merging
* semantic relationships through Obsidian wikilinks
* pseudo-metadata extraction and sanitisation

Metadata behaviour is defined through vault governance rather than hardcoded configuration.

---

# Governance Model

Ghostwriter uses vault-native governance documents to define operational behaviour.

Governance files are stored within:

```text
_meta/
```

Key files:

```text
_meta/meta-ops.md
_meta/guide-for-ai.md
```

These documents define:

* collaboration rules
* workspace conventions
* authorship expectations
* metadata governance
* collaboration permissions
* operational boundaries
* Safety Catch behaviour

The governance layer acts as a lightweight operational constitution for collaborators.

---

## Collaboration Roles

Ghostwriter supports portable note-level permissions through frontmatter roles.

| Role        | Append | Comment | Edit |
| ----------- | ------ | ------- | ---- |
| Author      | Yes    | Yes     | Yes* |
| Contributor | Yes    | Yes     | No   |
| Commenter   | No     | Yes     | No   |

* Through governed preview-and-confirm workflows.

Permissions are deny-first.

Notes without collaboration metadata deny access outside collaborator-owned workspaces.

---

## Safety Catch

Safety Catch acts as a governance-level override.

When enabled:

* collaborators may continue working within their own workspace
* collaboration outside owned workspaces is blocked
* portable note permissions are ignored

This provides a simple vault-wide containment mechanism while preserving personal collaborator environments.

---

# Collaboration Zones

Ghostwriter uses workspace-scoped collaboration zones.

Example:

```text
_collab/Alfred/
_collab/Sapphire/
```

Each collaborator maintains its own workspace.

Inside collaborator-owned workspaces:

* note creation is permitted
* folder creation is permitted
* append operations are permitted
* comment operations are permitted
* governed editing is permitted

Outside collaborator-owned workspaces:

* permissions are governed by note metadata
* Safety Catch may restrict access
* editor mutations require author-level permission

Workspace ownership and note permissions are intentionally treated as separate concepts.

---

# Activity Stream, Radar & Curiosity

Ghostwriter maintains lightweight attentional continuity through three complementary systems.

## Activity Stream

The Activity Stream records recent collaborative activity and related-note relationships.

Stored at:

```text
_ghostwriter/activity-stream.md
```

The stream provides:

* activity awareness
* lightweight continuity
* related-link tracking
* environmental context

It is not intended as heavy telemetry or audit logging.

---

## Radar

Radar represents current attentional pull.

It acts as a lightweight surface for:

* active interests
* emerging priorities
* near-term conceptual pressure

Radar influences what feels relevant now.

---

## Curiosity

Curiosity represents longer-term conceptual attraction.

It captures:

* recurring fascination
* unresolved ideas
* thematic wandering
* speculative interests

Curiosity is intentionally non-task-oriented and preserves ambiguity rather than forcing resolution.

---

# Architecture

Current structure:

```text
gw_core/
  activity_stream.py
  commenter.py
  editor.py
  frontmatter.py
  governance.py
  meta.py
  templates.py
  vault.py
  writer.py

tools/
  ghostwriter_tools.py

routes/
  list.py
  meta.py
  read.py
  status.py
  write.py
```

---

# Design Approach

Ghostwriter intentionally relies on lightweight primitives.

There is currently:

* no vector database
* no embedding pipeline
* no agent orchestration framework
* no autonomous background loop

Instead, Ghostwriter relies on:

* semantic reasoning
* authored continuity
* persistent environment structure
* governance semantics
* workspace conventions
* attentional continuity
* vault-native cognition scaffolding

The resulting behaviour emerges from the environment itself rather than from increasingly complex orchestration systems.

---

# Example Workflow

Typical interaction flow:

```text
Load governance context
→ establish collaborator identity
→ resolve workspace boundaries
→ retrieve relevant notes
→ evaluate permissions
→ collaborate within governance constraints
→ preserve continuity and provenance
```

---

# Future Directions

Areas of future exploration include:

* edit-review workflows
* activity auditing
* locked regions
* shared collaborative spaces
* permission inheritance
* collaborative coordination
* retrieval optimisation
* attention resurfacing
* semantic relationship weighting

Future development will continue prioritising:

* transparency
* reviewability
* operational restraint
* human oversight
* filesystem-native behaviour

---

# Safety Principle

Ghostwriter is designed to support collaboration, not replace authorship.

Human collaborators remain responsible for:

* review
* approval
* operational decisions
* governance

Ghostwriter is intentionally designed to remain:

* inspectable
* constrained
* reviewable
* understandable
* filesystem-transparent
