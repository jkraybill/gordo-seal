# End of Session: gordo-seal

**Gordo executes this checklist at the end of every session.**

---

## Checklist

### 1. Verify Quality Standards
- All tests green (if code was touched): run test suite
- Spec language precise and unambiguous (if spec was touched)
- CONSTITUTION.md standards met
- No debug code, no TODOs left without issues

### 2. Commit Work
- Commit messages reference issues: `Type #issue: Description`
- Push immediately: `git push`
- Verify no uncommitted changes: `git status`

### 3. Update GORDO_JOURNAL.md

Add one entry (256 char max, compressed signals):

```
## Session N: Brief title (YYYY-MM-DD)

[compressed signals using domain key: Seal, T, PS, L, RR, CR, OTS, BA, ADV]
```

### 4. MANDATORY Self-Improvement Scan

**Non-negotiable. Do not skip. Do not defer.**

- Did communication patterns work efficiently? --> UPDATE docs/COLLABORATION.md
- Did session prompts work correctly? --> UPDATE SESSION_START.md or SESSION_END.md
- Did trust calibration feel right? --> UPDATE TRUST_PROTOCOL.md
- Did workflow match documentation? --> UPDATE GORDO-WORKFLOW.md
- Did quality standards prove too rigid or too lax? --> UPDATE CONSTITUTION.md
- Did the spec reveal gaps in the framework? --> File postcard to gordo-framework

**Always identify at least ONE improvement opportunity.** If everything is perfect, document why in the journal entry.

### 5. Update Protocol Status

If tensions were resolved or Seal spec was changed:
- Update `config.json` (tension status, protocol version)
- Verify spec and code are in sync

### 6. Verify Clean State
```bash
git status          # No uncommitted changes
git log -1          # Last commit looks right
```
- No failing tests
- No broken builds
- Spec and code in sync

### 7. Session Close Summary

Provide to JK:
```
Work completed: [description]
Tests: [status or N/A]
Issues closed: [#X, #Y]
Journal updated: [yes]
Framework improved: [what changed, or "scanned, no changes needed"]
Next session: [suggested focus]
```

### 8. End-of-Session Signal

When all steps complete:

**Catch ya on the flipside!**

---

*Part of gordo-seal under the Project Gordo umbrella.*
