# Changelog

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