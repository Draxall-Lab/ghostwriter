# Changelog

---

## v0.5.0 - Portable Governance & Semantic Collaboration

### Release Type
Architecture / Governance / Collaboration Permissions

- Portable Note Permissions
- Governance-Aware Collaboration
- Safety Catch Enforcement
- Vault-Wide Append/Comment Permissions
- Workspace Ownership Semantics
- Governance Runtime Stabilisation

---

## Highlights

Ghostwriter v0.5 introduces portable note-governed collaboration permissions.

This release transitions Ghostwriter from workspace-bound collaborative mutation into governed vault-wide collaboration while preserving filesystem containment and operational restraint.

Notes may now carry their own collaboration contracts through governed frontmatter roles.

The collaboration model now separates:

- workspace containment
- note collaboration permissions
- creation authority

This significantly expands collaborative flexibility while maintaining deterministic governance and deny-first operational behaviour.

---

## New Features

### Portable Collaboration Permissions
Added governed note-level collaboration permissions through canonical metadata roles:

- `author`
- `contributor`
- `commenter`

Permission behaviour:

| Role | Append | Comment | Edit |
|---|---|---|---|
| Author | Yes | Yes | Reserved for future versions |
| Contributor | Yes | Yes | No |
| Commenter | No | Yes | No |

Permissions are deny-first.

Missing metadata denies access outside collaborator-owned workspaces.

---

### Safety Catch Governance
Added governance-level `Safety Catch` operational control.

When enabled through `_meta/meta-ops.md`:

- portable append/comment permissions are blocked
- collaborator access outside owned workspaces is denied
- workspace ownership behaviour remains intact

This creates a hard environmental override layer above portable note permissions.

---

### Vault-Wide Note Resolution
Added governed vault-wide note resolution for append and comment operations.

Ghostwriter can now:

- resolve existing notes across the vault
- validate collaboration permissions through governance
- preserve vault containment boundaries
- maintain filesystem safety during collaborative mutation

---

### Workspace Ownership Semantics
Collaborator workspaces now implicitly convey ownership semantics.

Inside collaborator-owned workspaces:

- append operations are allowed
- comment operations are allowed
- explicit role metadata is unnecessary

This removes unnecessary metadata boilerplate for personal collaborator environments while preserving explicit governance outside owned workspaces.

---

### Governance Runtime Validation
Added centralized governance-aware action validation through:

```text
can_perform_note_action()
```

This standardizes operational permission checks across:

- append workflows
- comment workflows
- future edit workflows

The governance layer now acts as the central behavioural permission authority.

---

## Governance Improvements

### Canonical Governance Abstraction
Expanded canonical metadata governance abstraction through:

```text
get_frontmatter_field_map()
```

Portable permissions now support:

- governance field remapping
- vault-native naming conventions
- case-insensitive collaborator matching
- future governance extensibility

Example:

```yaml
discussion_participants:
  - Alfred
```

may map canonically to:

```text
commenter
```

through governance.

---

### Governance Refresh Stability
Improved operational governance reload behaviour during live collaborative sessions.

Permission-sensitive operations now correctly refresh governance state during runtime evaluation.

This prevents stale collaborator assumptions after governance changes.

---

## Internal Changes

### New Permission Layer
Added centralized governance permission evaluation.

Responsibilities include:

- workspace ownership validation
- Safety Catch enforcement
- role-based collaboration checks
- portable permission handling
- governance-aware operation gating

---

### Path Resolution Refactoring
Separated:

- workspace-contained path resolution
from:
- vault-wide existing note resolution

This preserves filesystem containment while enabling governed vault-wide collaboration.

---

### Operational Separation Improvements
Further clarified separation between:

- filesystem safety
- governance permissions
- metadata mutation
- presentation formatting
- environmental structure

---

## Behavioural Improvements

### Collaborative Clarity
Permission denials now behave semantically rather than structurally.

Collaborators now receive:

- meaningful governance-aware denial behaviour
- explicit operational boundaries
- interpretable collaboration affordances

rather than ambiguous filesystem-level failures.

---

### Environmental Coherence
Collaborators now interpret vault permissions as environmental collaboration rules rather than arbitrary restrictions.

Observed behaviours include:

- workspace ownership understanding
- portable note permission interpretation
- governance-aware operational restraint
- collaborator-specific environmental continuity

---

## Validated Behaviour

Successfully validated:

- Author append/comment permissions
- Contributor append/comment permissions
- Commenter comment-only permissions
- deny-first behaviour for missing metadata
- Safety Catch override enforcement
- workspace implicit ownership
- vault-root governed collaboration
- case-insensitive collaborator matching
- governance remapping support
- portable permission enforcement
- governance reload behaviour
- cross-workspace append/comment restriction
- filesystem containment preservation

Validated across:

- Windows development environments
- Halo Linux environments
- live Obsidian Notes Lab vaults
- multi-collaborator interaction flows

---

## Architectural Direction

v0.5 establishes the foundation for:

- portable collaboration contracts
- shared collaborative environments
- permission inheritance
- future edit-review systems
- governance-aware collaborative tooling
- vault-native semantic collaboration infrastructure

while continuing to prioritise:

- transparency
- filesystem-native behaviour
- human oversight
- operational restraint
- reviewable collaboration
- deterministic governance

---

## v0.4.5 - Governed Metadata Lifecycle

### Release Type
Architecture / Governance / Semantic Metadata Expansion

- Metadata Governance Expansion
- Mutation Metadata Support
- Frontmatter Mapping Abstraction
- Additive Semantic Merging
- Pseudo-Metadata Handling
- Live Vault Behaviour Validation


## v0.4.0 - Governance & Frontmatter Foundation

### Release Type
Architecture / Governance / Metadata Stabilisation

---

## Highlights

Ghostwriter v0.4.0 introduces deterministic frontmatter governance and standardized operational parsing.

This release transitions Ghostwriter from a lightweight collaborative write layer into a more structured, governance-driven collaborative environment.

Vault-defined operational agreements now directly govern template selection, note structure, and metadata continuity.

---

## New Features

### Standardized Meta-Ops Section Parsing
- Added normalized `--SECTION--` governance structure
- Added deterministic section parsing for `meta-ops.md`
- Added section-aware operational directive loading
- Added stable machine-readable governance naming conventions
- Added support for future governance extensibility

### Template-Governed Note Creation
- Removed hardcoded template path handling
- Added `Template Path` governance directive
- Added vault-governed template selection
- Added exact-path template resolution
- Added support for template switching without code modification

### Deterministic Frontmatter Handling
- Added canonical frontmatter injection for new notes
- Added controlled metadata patching during note creation
- Added AI frontmatter override prevention
- Added template-derived metadata preservation
- Added canonical runtime field updates:
  - `created`
  - `last updated`
  - `created by`
  - `author`
  - `last updated by`

### Optional Template Disable Mode
- Added support for:
  - blank template directive
  - `None` template directive
- Allows raw note creation without template injection
- Maintains deterministic behaviour through governance rather than hardcoded fallback logic

---

## Governance Improvements

### Meta-Ops Structure
- Standardized governance block format
- Improved human readability
- Improved parser stability
- Improved future tooling compatibility
- Improved environmental governance clarity

### Operational Philosophy
Ghostwriter governance now more clearly separates:
- operational rules
- environmental guidance
- human-readable collaboration agreements
- deterministic machine interpretation

---

## Internal Changes

### New Template Layer
Added:

```text
gw_core/templates.py
```

Responsibilities include:
- template resolution
- frontmatter extraction
- canonical metadata patching
- frontmatter rendering
- template disable handling

### Refactoring
- Decoupled note creation from hardcoded template assumptions
- Centralized template/frontmatter logic
- Improved write pipeline separation of concerns
- Improved governance-driven behaviour handling

---

## Behavioural Improvements

### Note Creation
New notes now:
- inherit governed template structure
- preserve vault-defined metadata schemas
- maintain consistent frontmatter formatting
- resist AI-generated metadata drift

### Collaborative Stability
Improved:
- authored continuity
- metadata consistency
- vault structural reliability
- long-term governance maintainability

---

## Validated Behaviour

Tested successfully with:
- GW-base-note templates
- extended Coding Project templates
- nested metadata structures
- template switching
- blank template mode
- cross-platform operation on Windows and Halo Linux

Validated against:
- AI-generated metadata injection attempts
- workspace boundary enforcement
- governance reload workflows
- live collaborative note creation

---

## Design Direction

v0.4 establishes the foundation for:
- future metadata continuity systems
- richer governance tooling
- shared collaborative environments
- deterministic collaborative infrastructure

while continuing to prioritise:
- transparency
- filesystem-native behaviour
- human oversight
- operational restraint
- reviewable collaboration

---

## v0.3.0

### Added
- Workspace-scoped arbitrary folder creation
- Nested collaborative folder support
- Workspace-safe file move operations
- Full note writing support through `ghostwriter_write_note`
- Block-level contextual commenting system
- `ghostwriter_comment_on_note` tool
- Structural comment insertion engine (`commenter.py`)
- Contextual contribution placement using semantic anchor matching
- Before/after block positioning support
- Comment contribution styling with visual differentiation
- Workspace-relative path handling model
- Controlled collaborative annotation workflow
- Support for contextual layered note collaboration

### Changed
- Transitioned Ghostwriter from append-only collaboration into additive contextual collaboration
- Refined collaborative contribution formatting for improved readability
- Removed hard visual separators (`---`) from contribution rendering
- Introduced italicised comment-body rendering for clearer annotation distinction
- Unified workspace-relative path resolution across write operations
- Improved separation between routing, orchestration, and text manipulation layers
- Refined contribution presentation to better support continuous reading flow

### Improved Architecture
- Introduced dedicated block insertion helper layer (`commenter.py`)
- Further separated structural text operations from filesystem orchestration
- Standardised workspace-root path semantics across tools
- Reduced write-layer coupling between formatting and placement logic
- Improved internal consistency between append and comment workflows

### Validated
- Block-level contextual comment insertion
- Semantic anchor resolution through natural language prompts
- Multi-comment stacking behaviour
- Relative comment placement ("before" / "after")
- Contextual annotation readability
- Workspace-safe note movement
- Nested folder creation
- Additive collaborative annotation workflow
- Semantic navigation of authored contribution chains
- Natural-language collaborative reference behaviour
- Cross-platform collaborative vault persistence after remount/reload recovery

### Safety
- Comment operations remain additive and non-destructive
- No inline sentence rewriting
- No silent mutation of authored prose
- No unrestricted vault editing
- Workspace boundaries preserved
- Human reviewability maintained across all collaborative operations
- Structural collaboration remains explicitly attributable and inspectable