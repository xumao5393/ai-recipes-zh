L104: Before you rely on it:
L105: 
L106: - **The trademark catalog is yours to load.** No trademark data is shipped or downloaded. You prepare the data, check
L107:   that the terms of its source allow this storage and use, and import it (see [Trademark catalog](#trademark-catalog)).
L108:   Without a catalog the trademark check answers `503` and the rule checks are not affected. The `uspto-convert` job
L109:   converts a USPTO Trademark Daily XML applications file you downloaded yourself to the `jsonl-1` format, but it is
L110:   **unverified against real data**: it was written from the public DTD V2.0 and tested with synthetic XML only, and a daily
L111:   file holds changes, not the whole register. For any other source you convert your data to `jsonl-1` yourself.
L112: - **No accuracy has been measured on real data.** The evaluation of the trademark check (ADR-009, PR A4) has not been
L113:   run, and every threshold and word list of the trademark ruleset is marked `unverified`. `batch-check` can count how
L114:   often listings you labelled were flagged (`--label-column`); that is a measurement on a small set, not an accuracy.
L115: - **Marketplace limits are only as verified as their source.** Each rule records a source status (`verified`,
L116:   `secondary` or `unverified`) in its ruleset; see [Rulesets](#rulesets).
L117: - **Policy retrieval has not been evaluated.** There is no recall figure yet, because the evaluation needs a real run
L118:   with an embedding provider.
