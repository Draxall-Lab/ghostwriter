# Changelog

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