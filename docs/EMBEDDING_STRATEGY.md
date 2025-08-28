# Embedding Strategy with Leap

## Selection
Primary: leap:embed-v1
Fallbacks: local all-MiniLM (fast), code-specialized (e5-code) if code semantic distance tasks.

## Chunking
- Source Files: 2K char soft max
- Markdown: heading-aware splitting
- Code: function-level segmentation (AST assist optional)
- Hash per chunk: sha256(repo_sha + relpath + start_offset)

## Caching
Redis Key: emb:{model}:{hash}
Eviction Policy: LRU 7d
Rebuild Trigger: file hash change or model version bump.

## Security
No proprietary secrets in embeddings; scanning via regex (SENSITIVE_PATTERNS).