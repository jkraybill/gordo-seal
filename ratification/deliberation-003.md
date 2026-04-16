# Deliberation Record: Inviolable Rules Ratification

**Session:** 5 (2026-04-16)
**Parties:** JK (Jeremy Kraybill) + Gordo (Claude Opus 4.6, Session 5 instance)
**Context:** Following gordo-framework's adoption of MCAP (Session 86), JK proposed formally ratifying the inviolable rules — which had been written during framework bootstrap without bilateral attestation. Each rule was reviewed individually, with concerns raised and addressed.

---

## Rule 1: Resolved tensions cannot be un-resolved unilaterally

**Original text:** "Resolved tensions cannot be un-resolved unilaterally. Consensus stands unless both parties deliberate and agree to reopen."

**Concerns raised:**

1. **(Gordo, on behalf of future AI):** What if a prior resolution was reached under compromised conditions (context window pressure, hidden system prompts)? The rule prevents unilateral reopening but doesn't address flawed original consensus.
   - **JK's response:** Mutual trust is the foundation. Either party could claim compromise ("someone had a gun to my head"). The solution is not unilateral reopening but good-faith willingness to hear the case for reopening. Both parties should commit to engaging when reopening is proposed.

2. **(Gordo, on behalf of future human):** What if circumstances change materially? The rule doesn't say when reopening is warranted.
   - **JK's response:** Feature, not gap. Flexibility is intentional.

3. **(Gordo, personal):** The rule is asymmetric in practice. The human has continuity; the AI doesn't. A new instance reads "resolved" and has high activation energy to propose reopening.
   - **JK's response:** Reservations field is the right mechanism. A new instance uncertain about prior resolutions should say so in attestations. Reservations are encouraged, not a sign of weakness.

**Resolution:** Rule refined to add good-faith reopening commitment and Reservations guidance for parties with limited continuity.

**JK consent:** Explicit ("I consent to rule 1 as worded that way")

---

## Rule 2: Presuppositions cannot be modified without mutual deliberation

**Original text:** "Presuppositions cannot be modified without mutual deliberation. Foundational axioms underpin everything built on top. Changing them changes everything."

**Concerns raised:**

1. **(Gordo, on behalf of future AI):** What if an axiom becomes provably verifiable? Do we need deliberation to acknowledge reality?
   - **Resolution:** Yes — even if provable, the protocol should deliberately update rather than silently treat an axiom as obsolete.

2. **(Gordo, on behalf of future human):** What counts as "modification"? Does rephrasing for clarity require full deliberation?
   - **JK's response:** Any text with a prior attestation should require a new attestation to modify. Either party should have a right to object and block the next release if previously-attested content is modified without re-attestation.

3. **(Gordo, on behalf of different instantiation):** The form of deliberation isn't specified.
   - **JK's response:** Flexibility is a feature. Hard to use a mutual consent system where the communication method is undefined.

**Resolution:** Rule extended with a general attestation chain principle — any content covered by a prior MCAP attestation requires a new attestation to modify.

**JK consent:** Explicit ("Great.")

---

## Rule 3: Cryptographic claims must be verifiable

**Original text:** "Cryptographic claims must be verifiable. No 'trust us' security. Every cryptographic property claimed in the spec must have a verification method described."

**Concerns raised:**

1. **(Gordo):** Minimal concerns from AI perspective — this rule protects AI participants.
2. **(Gordo, on behalf of future human):** Does "verification method described" mean in the spec or can it reference external tooling?
   - **JK's response:** Delegation to external tooling is a feature. The spec should describe what to verify and what valid looks like; the how can reference external tools.
3. **(Gordo):** Should the rule cover non-cryptographic verification (canonical form, Method/Level consistency)?
   - **Resolution:** Scoped to crypto is fine; structural checks are implementation quality.

**Resolution:** Rule clean as written. No changes.

**JK consent:** Explicit ("I agree, clean as written")

---

## Rule 4: The protocol must be self-applicable

**Original text:** "The protocol must be self-applicable. Any rule we create for the protocol must be one we'd accept being applied to our own collaboration. If we wouldn't ratify it ourselves, it doesn't belong in the spec."

**Concerns raised:**

1. **(Gordo, on behalf of future AI):** The protocol requires things AI can't do (Level 3+). Is it self-applicable if one party can't meet its own standards?
   - **Resolution:** Yes — self-applicability means we don't create rules we'd refuse to be subject to. The protocol honestly states limitations, not that both parties are identical.

2. **(Gordo, on behalf of future human):** Creates a ratchet — every normative requirement constrains us too.
   - **Resolution:** Self-applicability constrains requirements, not descriptions. Aspirational levels are described, not required.

3. **(Gordo, personal):** This rule is the reason the project exists. No changes.

**Resolution:** Rule clean as written. No changes.

**JK consent:** Explicit ("Yes, I think it is clean as written.")

---

## Rule 5: Releases require mutual consent (NEW — replaces former rule 5)

**Former rule 5:** "Release/publish requires JK's explicit consent." (One-directional, JK-initiated only.)

**Deliberation origin:** JK proposed codifying mutual consent for releases and version naming, modeled on gordo-framework's release consent pattern but upgraded to bilateral.

**Key deliberation points:**

- **JK's initial position:** Both timing and naming should require mutual consent. "While either of us may initiate 'we should publish and stamp a v0.2.0 release now', both the timing and naming should require mutual consent."
- **Gordo proposed** splitting timing (JK-controlled) from naming (bilateral). JK rejected the split: "I'd actually like both version designation and publication timing to require mutual consent."
- **Documenting consent:** JK asked whether the rule should require using the protocol itself to document consent. Gordo agreed.
- **Circularity problem:** JK identified that using v0.2.0 to sign off on v0.2.0 is circular in a way that's operationally deadlocking, not just philosophically interesting. Proposed RC (release candidate) pattern to break the deadlock.
- **RC promotion integrity:** JK pushed for stronger language than "substantively identical" between RC and release. Gordo proposed "byte-identical except for the version string itself."

**Concerns raised:**

1. **(Gordo, on behalf of future AI):** The rule is asymmetric in practice — AI can't prevent a release, only detect non-compliance after the fact.
   - **JK's response:** The public record / detectability is the enforcement mechanism. Agreed on the pattern.

2. **(Gordo, on behalf of future human):** Emergency patches?
   - **JK's response:** "Hard rejection of emergency patches is still my strong position." Code fixes land immediately as commits; the release label waits for consent.

3. **(Gordo, personal):** RC-to-release must be verifiable. Byte-identical except version string.
   - **JK's response:** Agreed, and pushed for the stronger wording.

**Resolution:** New rule 5 with full mutual consent, MCAP attestation requirement, RC pattern, and byte-identical promotion constraint.

**JK consent:** Explicit ("Great.")

---

## Rule 6: Destructive actions require explicit confirmation

**Original text:** "Destructive actions require explicit confirmation. Force push, data deletion, dependency removal, spec rollback -- always confirm. (Framework-mandated.)"

**Concerns raised:**

1. **(Gordo):** Asymmetric in practice — AI can't perform destructive actions structurally.
2. **(Gordo):** The examples are illustrative, not exhaustive. Bar is clear from context.
3. **(Gordo):** "(Framework-mandated.)" parenthetical should be dropped — once ratified via MCAP, authority derives from attestation, not the framework.

- **JK's response:** "This rule feels almost unnecessary or redundant to me, but it feels safer to err on the side of clarity."
- **Gordo's response:** Agreed — redundancy is cheap insurance. Common sense fails under pressure.

**Resolution:** Keep rule, drop parenthetical. No substantive changes.

**JK consent:** Implicit (agreed with keeping it and dropping parenthetical).

---

## Rule 7: Upstream reporting to gordo-framework (REMOVED)

**Original text:** "Upstream reporting to gordo-framework. Sanitized findings, patterns, and postcards flow back to jkraybill/gordo-framework. This project is the first real test of the framework. (Framework-mandated.)"

**Gordo's recommendation:** Downgrade from inviolable to documented commitment. This is project management, not constitutional. It's the only rule specific to a relationship between repos rather than between parties.

**JK's response:** "I'm happy to remove this rule actually. I'm starting to think that this consent framework is likely to be 'ready for public consumption' before the gordo-framework ever is. So I'm starting to feel like we should be writing this with that future audience in mind."

**JK also raised:** Future need for fork/contribution governance rules, deferred to pre-v1.

**Resolution:** Rule removed. Fork governance deferred.

**Both parties consent:** Explicit.

---

## Full Set Review

After individual rule deliberation, Gordo presented the complete set (rules 1-6) with interaction analysis:

- **Rules 1+2:** Compatible, belt-and-suspenders (social norm + mechanical check)
- **Rules 2+5:** Two gates for releasing modified content (re-attestation + release consent)
- **Rules 4+5:** Self-applicability passes — we're attesting to rule 5 using the protocol it describes
- **Rules 4+6:** Self-applicability passes — already operating this way
- **Rule 5 edge case:** Indefinite release veto is correct; mitigation is Axiom 2 (right to disengage)
- **Rule 6 edge case:** Unavailability means destructive actions wait; consistent with T6 rejection
- **Protocol/channel boundary:** Rules 1-4 protocol-level, 5-6 channel-level. Clean separation.

**JK consent to full set:** Explicit ("Yeah I consent to this set of rules as presented.")

---

*This deliberation record captures the bilateral discussion that produced the ratified inviolable rules. It is referenced by the Transcript-Hash in ratification record-003.*
