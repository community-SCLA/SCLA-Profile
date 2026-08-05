# Design-System Contract

Agents consume the design system through machine-readable files:

- `config/tokens.yml`: canvas, palette, typefaces, type floors, spacing, timing,
  program names, and the pinned production voice
- `assets/`: approved fonts and brand marks
- `compositions/`: shared runtime composition code checked for freshness
- `hyperframes.json` and `package.json`: pinned project/runtime configuration

For a lesson build, use the workspace copies created by the shared scaffold.
Do not load human documentation or the full brand guide. Do not copy historical
commentary into a build. Gates compare the workspace copy against this source.

Production voice has exactly one provider, voice ID, and speed. Timing constants
have exactly one source. Neither permits a workspace override or fallback.
