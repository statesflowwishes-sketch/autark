# Leap Integration

## Übersicht
Leap erweitert das Autark-System um:
- Embeddings
- Utility LLM (Kurz-Summaries, Pre-Drafts)
- Bild-/Asset-Generierung
- Fine-Tuning Pipelines

## Entscheidungsmatrix
| Task Typ | Primär | Fallback |
|----------|--------|----------|
| Code Gen | CodeLLM | Local/Qwen |
| Kurze Summary (<=1k Tokens) | Leap Utility LLM | CodeLLM |
| Embeddings | Leap Embeddings | Local Embedding Model |
| README Draft | Leap -> Refine CodeLLM | Direkt CodeLLM |
| Image Asset | Leap Image Model | (platzhalter: stable-diffusion local) |
| Commit Message Style (Fine-tuned) | Leap Fine-Tuned Model | Generic Prompt |

## Sicherheitsfilter
- `prompt_sanitizer.py` entfernt Codefragmente wenn asset=true.
- Klassifikator markiert potenziell sensitive Strings -> Blocklist.

## Fine-Tuning Flow
1. Datenernte: commit messages, PR Beschreibungen (Policy-gated)
2. Normalisierung -> JSONL
3. Upload -> Leap Fine-Tune Job
4. Status Poll -> bei 'completed' Modell-ID speichern in routing registry
5. Versionsverwaltung: `model_registry.json` (hash + created_at)

## Kostenkontrolle
- Konfig `cost_budgets.yaml` enthält pro Service Budget.
- Preflight: Summierung geplanter Embedding Tokens.

## Observability
- Metrik: leap_requests_total{type="embedding|image|llm"}
- Metrik: leap_latency_seconds_bucket
- Audit Einträge: service='leap', model=..., task_id=...

## Beispiel Use Cases
- "Erzeuge Icon für neues Feature" -> orchestrator ruft leap_image.generate()
- "Kurzer Diff-Summary" -> leap_llm.summarize(diff)
- "Feinjustiere Commit Message Style" -> fine-tuned model in commits phase.
