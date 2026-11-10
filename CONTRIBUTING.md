# How changes land in this repo

Every change goes through a pull request, even solo work:

1. Branch from `main` (`feat/...`, `fix/...`).
2. Open a PR using the template; CI must be green.
3. Review the diff against the checklist before merging, and leave review comments on anything that needs a follow-up.
4. Squash-merge, then delete the branch.

CI (`.github/workflows/`) runs unit tests, the FabLens retrieval gate, the AI App Scorecard regression check, and the lakehouse pipeline test.
