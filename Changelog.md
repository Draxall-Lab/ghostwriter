# Changelog

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

---

## v0.2.0

### Added
- Controlled collaborative write capabilities
- AI working folder creation inside approved collaboration zones
- Template-based blank note creation using `Templates/General Note.md`
- Append-only collaborative note contributions
- Persona-scoped workspace isolation
- Write policy resolution layer (`write_policy.py`)
- Filesystem-safe writer layer (`writer.py`)
- Append target validation for owned collaborative notes
- Raw append model with meta-ops-governed contribution formatting
- New Ghostwriter tools:
  - `ghostwriter_create_working_folder`
  - `ghostwriter_create_blank_note`
  - `ghostwriter_append_to_note`
- Multi-persona collaboration testing and validation
- Operational governance updates for v0.2 Stage 1
- README documentation

### Changed
- Transitioned Ghostwriter from read-only retrieval into controlled collaborative authorship
- Moved contribution formatting responsibility from hardcoded tool behaviour into `_meta/meta-ops.md`
- Updated operational governance documents to support limited write permissions
- Improved collaborator identity handling and working-folder enforcement
- Standardised frontmatter population using vault-native template fields

### Validated
- Semantic workspace navigation
- Working folder inference from collaborator identity
- Template-native note creation
- Append-only collaboration workflow
- Multi-collaborator workspace separation
- Meta-context refresh and governance reloading
- Provenance-aware collaborative contributions
- Persistent authored collaborative state

### Safety
- Append operations restricted to owned collaborative notes
- No arbitrary vault editing
- No delete or move capabilities
- No silent content mutation
- No unrestricted filesystem access
- Human review and oversight preserved as core operational principle

---

## v0.1.0

### Added
- Initial Ghostwriter filesystem-native Obsidian integration
- Vault status checks
- Markdown note listing
- Markdown note reading
- Frontmatter parsing
- Meta-context loading from `_meta/guide-for-ai.md`
- Meta-context loading from `_meta/meta-ops.md`
- Semantic note retrieval through natural language reasoning
- Wikilink navigation and semantic graph traversal
- SMB/CIFS-mounted vault support
- Windows and Linux validation environments

### Added Operational Layer
- `_meta/guide-for-ai.md`
- `_meta/meta-ops.md`

### Introduced Concepts
- Environment-centric AI collaboration
- Persistent collaborative workspace cognition
- Operational governance through Markdown documents
- Filesystem-native authored continuity
- Identity-scoped collaboration
- Human-reviewable collaboration architecture

### Validated
- Semantic retrieval without vector databases
- Workspace structure interpretation
- Natural wikilink traversal
- Operational governance influence on collaborator behaviour
- Vault-as-environment interaction model
- Lightweight collaboration architecture using Markdown and filesystem primitives only

### Design Principles
- No vector database
- No embeddings pipeline
- No orchestration framework
- No background agents
- No autonomous mutation
- Reviewable, constrained collaboration-first architecture