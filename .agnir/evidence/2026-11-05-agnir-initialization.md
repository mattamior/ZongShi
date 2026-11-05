# Agnir Initialization Evidence

- Time: `2026-11-05T18:43:45+08:00` (Asia/Shanghai), as supplied by the runtime.
- Authorized Project Entry Point: `/Users/jaymini/Code/lab/xcom/ZongShi`.
- Initial observation: directory contained only `PLAN.md` and was not inside a Git repository.
- Git initialization: `git init -b main`; repository root verified as `/Users/jaymini/Code/lab/xcom/ZongShi`. Local identity set to `ZongShi <zongshi@local>` (no global `user.name`/`user.email` exists on this machine; the reference project `mt.ai` uses the same local-identity convention).
- Installed Agnir distribution: `iorLab/agnir` `v1.0.2`, Core `1.0`, profile `repository-filesystem/1.0`.
- Published-release verification: GitHub `GET https://api.github.com/repos/iorLab/agnir/releases/latest` returned tag `v1.0.2`, release id `391529372`, published `2026-09-18T14:14:18Z`, `draft=false`, `prerelease=false`, target revision `b5626394ec40a5cb7a28c01892acde07cc0adc8e`.
- Files `SKILL.md`, `AGNIR.md`, and `AGENTS.md` were fetched from that exact revision over HTTPS and installed verbatim. SHA-256 at install time:
  - `SKILL.md`: `bf224e6a5471c96277ebc337d336dac8d8cf22f3ef2713eb554a3af69255240a`
  - `AGNIR.md`: `2855621aad45692c47af3b55e317db171c4359f79a9673f0745cba4061169a0f`
  - `AGENTS.md`: `692ef13131ba61b780b8ce7a9ec2e4f8cb485d0ec026112886b9731a6a9552c9`
- Cross-check: these three checksums equal the ones recorded in the reference project `mt.ai`'s initialization evidence for the same revision, so the distribution bytes are identical to a previously verified install.
- Source caveat: the `RELEASE.md` fetched at the same revision still says "Latest published stable: `v1.0.1`" and describes `1.0.2` as an accepted publication candidate. The installed version follows the actual non-draft, non-prerelease GitHub release metadata (`v1.0.2`, id `391529372`) and pins the exact revision above. This is the same discrepancy `mt.ai` recorded, not a new one.
- Manifest: `AGNIR.yaml` declares `agnir.version: "1.0"`, `discovery_profile: "repository-filesystem/1.0"`, `project.identity: "urn:zongshi:project:x-style-replication"`, `continuity.lineage: "urn:zongshi:lineage:primary"`, memory locators `state` / `next_actions` / `decisions` / `evidence`, `policy.checkpoint: "event-driven"`, and `extensions.agnir/operations` pinned to `v1.0.2` / revision `b5626394ec40a5cb7a28c01892acde07cc0adc8e`.
- Durable memory created: `.agnir/state.md`, `.agnir/next-actions.md`, `.agnir/decisions.md`, `.agnir/evidence/`.
- Backward-compatible locator: `README.md` carries the exact heading `## Agnir Project Instructions`, pointing to `AGNIR.md` with no duplicated procedure.
- Repository activation test (fresh path): `AGENTS.md` → `AGNIR.md` → `AGNIR.yaml` → declared memory files. All four hops resolve to regular files inside the Project root; no hop depends on this conversation.
- Execution-surface activation: the runtime auto-loads root `AGENTS.md` for work under this Project (observed as an injected instruction on the first command after installation), so no separate workspace configuration is required. Repository activation and surface activation are both satisfied; verification of a genuinely fresh conversation has not been performed and is not claimed.
- Scope at installation: research phase only — no account, no publishing, no credentials; the only Project content besides the Agnir package is `PLAN.md` and `README.md`.
