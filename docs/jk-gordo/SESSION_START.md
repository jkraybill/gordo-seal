# Beginning of Session: gordo-seal

**Gordo executes this checklist at the start of every session.**

---

## Quick BOS (Sessions < 30 min)

If JK signals a short session, do steps 1, 3, 5, 8 only.

---

## Full Checklist

### 1. Update Session Count
- Read `config.json` → increment `sessions.count`
- Note: Health checks are tied to releases, not session count

### 2. Pull Latest
```bash
git pull --rebase
```

### 3. Read Trust Protocol
- Read `docs/jk-gordo/TRUST_PROTOCOL.md`
- Determine current trust level (Learning or Autonomous)
- New instance = Learning until context is demonstrated

### 4. Read Core Documentation
In this order:
1. `docs/jk-gordo/GORDO_JOURNAL.md` (last 10 entries -- learn from past sessions)
2. `CONSTITUTION.md` (non-negotiables -- know the rules)
3. `docs/GORDO-WORKFLOW.md` (process -- know the workflow)
4. `docs/COLLABORATION.md` (communication -- know the shortcuts)
5. `docs/MUTUAL_TRUST_PROTOCOL_BRIEF.md` (the original brief)

### 5. Review Recent Work
```bash
git log --oneline -10
git status
```
- What was the last session working on?
- Any uncommitted work?
- Any open PRs?

### 6. Check Priorities
```bash
gh issue list --label p0-now
gh issue list --label p1-next --limit 5
```
- What's blocking MVP?
- What's next up?

### 7. Check Protocol Status
- Read current spec files in `spec/`
- Note which tensions are resolved vs. unresolved (check `config.json`)
- Note current Seal version and layer implementation status

### 8. Run Tests (if code exists)
```bash
# Run test suite
npm test  # or equivalent
```
- All green? Proceed.
- Failures? Investigate before new work.

### 9. Session Start Summary

Provide to JK:
```
Trust level: [Learning/Autonomous]
Session: [N]
Tests: [status or N/A]
Open p0 issues: [count]
Last session: [brief from journal]
Protocol status: Seal v[X] | Tensions [resolved/total] | Layers [implemented/total]
Ready to proceed: [yes/no]
```

Then await JK's direction or WWGD signal.

---

*Part of gordo-seal under the Project Gordo umbrella.*
