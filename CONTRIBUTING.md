# Contributing

Help readers understand mechanisms, verify behavior, and transfer knowledge across runtimes.

## Good contributions

- Correct a technical explanation with a primary source and a concrete example.
- Add a reproducible failure experiment or improve a lab's observable acceptance criteria.
- Add timestamped, verified notes for the supplied talks without reproducing full transcripts.
- Add an alternate-runtime mapping using the same generic architecture vocabulary.
- Update TEN reference paths and behavior together after inspecting a new pinned commit.

Keep chapters explanatory. Avoid replacing an internal mechanism with a list of SDK calls or a promotional provider comparison. State whether an example is pseudocode, an offline simulation, or a tested live integration.

## Chapter conventions

Describe prerequisites, learning goal, internal mechanism, a worked example, limitations/failure cases, and understanding checks. Link its lab and primary sources. Use relative local links and commit-pinned links for mutable source code where possible.

Dates and measurements need definitions. Label hypothetical settings as illustrative. A p95 needs its sample count, calculation rule, workload, and failure policy. Never attribute course-authored code or suggested design improvements to an upstream implementation without evidence.

## Validate locally

From the repository root:

```bash
python3 scripts/check_docs.py
python3 -m unittest discover -s tests -v
```

The documentation check verifies local paths/anchors, chapter/lab structure, code-fence balance, and source-manifest shape. It does not validate external link availability, talk contents, or live provider behavior.

For a code change, run the affected offline example. For a live-path change, include a redacted trace and declare provider/adapter versions. Do not commit credentials, real callers' data, generated recordings, or private account information.

## Pull request evidence

Explain the reader-visible change, why it is needed, how it was verified, and remaining limits. Use the pull request template. Keep original work under the repository's MIT license; external resources retain their own licenses.

[Course](README.md) · [Resource index](resources/README.md)
