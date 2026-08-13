# IsarPunk Engagement Platform — High-Level Concept

**Status:** Concept v0.1 — **PARKED** after goal-setting (Aug 2026) · not a year-one delivery commitment  
**Audience:** project team  
**Spirit:** Small, sharp, fun, compliant — not an enterprise youth network.  
**Canonical project decisions:** [`Meetings/Minutes - Goal Setting.md`](../Meetings/Minutes%20-%20Goal%20Setting.md)

---

## 0. Fit with goal-setting decisions (review)

| Meeting decision | Implication for this concept |
|------------------|------------------------------|
| Primary delivery = **~6 workshops** from ~Nov | Platform is an **amplifier**, not the main KPI |
| Lead metric = **confidence** (stickers / forms) | Badges should encode confidence/missions, not only installs |
| Primary partners **now** = **repair shops & cafés** | Verifiers = shops/cafés first; MuCCC optional later |
| No hardware giveaways; handoff broken devices | Log “sent to repair” / “shop visit” as first-class actions |
| Software cos (Nextcloud, Tuxedo…) = after ~3–4 workshops | Tip links / deep FOSS projects = **phase 2+** features |
| Partner **cheat sheet** + outreach by mid-Sep | Do **not** build app before shop relationships exist |
| Engagement platform **not decided** this meeting | Stay in concept; revisit after workshops 1–3 / shop engagement |

**Verdict after review:** The product idea still fits IsarPunk — but **sequencing changed**. Ship workshops + shop handoff first; use the platform to make confidence and referrals *visible* once partners can actually verify.

---

## 1. Why this exists

School workshops sow the *Save Oma / FOSS upcycle / circular* story. Without a place to **show progress**, energy evaporates after the bell.

The engagement platform is the **scoreboard and clubhouse** for that energy:

- School teams register and track meaningful actions (workshop attendance, confidence missions, Linux installs, **repair-shop referrals**)
- Partner **shops / cafés** (and later labs) can **verify** claims
- Teams earn **badges** (status, not surveillance)
- Later: teams can publish **project ideas** and optional tip links (e.g. Buy Me a Coffee / Ko-fi)

IsarPunk runs **dispersal workshops** (~6 / school year). Repair shops, Repair Cafés, and similar hubs own deep installs and refurb. The platform **amplifies** that split — it does not replace the hubs.

**Timeline advantage:** consumer Windows 10 ESU runs to **12 October 2027**. Use the runway to grow a capped, trusted challenge — not a panic app. Funding calendar (Nebenan): interim ~Feb; final eval oriented ~Nov 2027.

---

## 2. One-sentence product

> A **capped school-team challenge tracker** where Munich youth log FOSS / circular-upcycle actions, get **shop- or lab-verified** badges, and later optionally crowdfund follow-on projects — designed from day one for **minimal youth data**.

---

## 3. Goals

| Goal | Meaning |
|------|---------|
| **Engage** | Give workshop survivors a reason to come back |
| **Make progress visible** | Confidence missions, installs, and shop referrals show up for the team |
| **Route to hubs** | Verification and “go deeper” paths point at **repair shops/cafés** (then MuCCC / software FOSS) |
| **Support reporting** | Soft evidence for Nebenan impact beyond “we spent the money” |
| **Stay shippable** | Experienced IT + AI; hard user caps; no social network feature creep |
| **Earn trust** | Youth + GDPR is the hardest problem — we design for it, not around it |

### Non-goals (v0)

- Chat, DMs, feeds, likes, or open social graph  
- Being the install / refurb / hardware service  
- Payment processing (tip links outbound only, and **not in first pilot**)  
- Unlimited public signup  
- Replacing Jugend hackt, MuCCC, school LMS, or Circular Munich’s [CircularCity Map](https://circular-munich.com/circularcitymap/)  
- Launching before ~3 workshops and at least one verifying shop partner  

---

## 4. Who it’s for

| Actor | Role |
|-------|------|
| **School team** | Klasse, AG, Projektgruppe — the primary identity |
| **Adult sponsor** | Lehrer:in or Eltern contact; accountable for the team account |
| **Participants** | Youth who do the work (may have limited or no personal login in v0) |
| **Shop / café verifier** | Repair partner who confirms visits, installs, referrals |
| **Lab verifier (later)** | MuCCC / FabLab if onboarded |
| **IsarPunk admin** | Cap users, issue verifier accounts, moderate team names |

---

## 5. Core loop

```text
Workshop spark (+ confidence sticker/form)
    → Team registers (sponsor + school)
        → Log actions (claimed)
            → Shop/café verifies (where badge requires it)
                → Badges unlock
                    → Team page shows progress
                        → Curious kids/families go to the repair partner
```

**Success looks like:** a teacher says “our AG has three badges”; a shop confirms two visits; confidence scores rise; a family shows up at a café because the workshop said so.

---

## 6. Feature pillars (v0 — when un-parked)

### 6.1 Team registration
- Register as a **team**, not as a free-for-all kid social profile  
- Fields (minimal): team name, school, sponsor name + email, approximate age band, optional workshop code  
- Hard **cap** on teams / users (product feature — advertise it)

### 6.2 Activity log
Aligned with meeting metrics:

| Action | Claimable in workshop? | Needs partner verify for full badge? |
|--------|------------------------|--------------------------------------|
| Attended IsarPunk workshop | Yes | No |
| Confidence check-in (pre/post) | Yes (workshop ritual) | No |
| “Oma talk” / family awareness | Yes (honour) | No |
| Live USB / first boot demo | Yes | Optional |
| Referred device / family to repair shop | Yes | **Yes** (shop stamp) |
| Shop / café visit attended | — | **Yes** |
| Linux install completed | Yes | **Yes** for verified badge |
| Custom team project published | Phase 2 | Optional admin review |

State machine: `claimed → partner_confirmed` (and `rejected` if needed).

### 6.3 Badges / social credit
- Badges reward **behaviours we can seed in a 90-min workshop**, not only rare installs  
- Examples: *Seed Planter*, *Confidence Climber*, *Oma Diplomat*, *First Boot*, *Shop Explorer*, *Verified Install*  
- Display on team page; **printable sticker twins** for IRL workshops (pairs with door-sticker confidence method)  
- “Social credit” = reputation within the challenge only

### 6.4 Projects + tip links (phase 2+)
- After workshops 1–3 and clearer student demand (same gate as Nextcloud outreach)  
- Short project idea + optional Buy Me a Coffee / Ko-fi URL  
- IsarPunk never handles money  

### 6.5 Partner verification
- Few privileged **shop/café accounts** first  
- Confirm visits / installs / referrals — no ID uploads  
- Co-design a **10-second verify** flow as part of the partner cheat sheet conversation  
- If no shop will verify yet: IsarPunk admin may stub-confirm workshop-only badges only

---

## 7. Youth + GDPR as architecture

Hardest problem — design constraint, not a kill switch.

### Principles
1. **Minimal data** — only what the challenge needs  
2. **Team-first identity** — reduce per-child accounts  
3. **Adult sponsor** as primary contact / accountability  
4. **EU hosting** + written retention (e.g. wipe or anonymise after school year)  
5. **No behavioural adtech, no resale, no dark patterns**  
6. **Clear purpose** on signup: challenge participation and partner handoff  

### Practical v0 stance
- Prefer **sponsor login**; youth contribute through the team  
- Public board: **team names + badge counts**, not birthdates or addresses  
- One-page privacy notice before any pilot  
- Confidence stickers in-room can stay **anonymous aggregates** even if the app later stores team-level scores  

*(Detailed data map, DPIA-lite, and consent flows = follow-up doc when un-parked.)*

---

## 8. Scope & caps

| Control | Intent |
|---------|--------|
| Invite / workshop codes | No infinite open internet signup |
| Max teams / max users | Operationally sane; exclusive challenge energy |
| Verifier seats | Handful of trusted shops/cafés |
| Feature freeze for pilot | Teams + actions + badges; **no tip links yet** |

Pilot suggestion: enable only after **workshop #1–3** and **≥1** verifying partner; expand caps when ops feel boring.

---

## 9. What we build vs buy

| Need | Approach |
|------|----------|
| App (auth, teams, logs, badges) | Build thin (IT experience + AI) — **after** shop cheat sheet + early outreach |
| Hosting | EU VPS / managed Postgres |
| Payments | Don’t build |
| Chat | Don’t build |
| Confidence capture v0 | May stay **analog** (stickers) or Forms until app exists |
| Partner visibility | Prefer Circular Munich [CircularCity Map](https://circular-munich.com/circularcitymap/) — don’t rebuild their map |

---

## 10. Success metrics (platform)

| Metric | Ties to meeting |
|--------|-----------------|
| Teams registered (under cap) | Adoption |
| Confidence-related actions / badges | Lead outcome |
| Shop referral / visit confirms | Handoff health |
| Verified installs | Secondary |
| Qualitative: shop says “kids showed up because of IsarPunk” | Real loop |

Not a vanity metric: pageviews without teams.

---

## 11. Risks (chin-up mitigations)

| Risk | Mitigation |
|------|------------|
| Empty board | Don’t launch until workshop #1 + seeded demo team |
| Shops won’t verify | Co-design verify UX into partner cheat sheet; start with one friendly café (e.g. volunteer-led) |
| Building too early | Keep **PARKED** until mid-Sep outreach and content v1 exist |
| GDPR fear from schools | Sponsor model + privacy one-pager + minimal fields |
| Scope creep | Non-goals; tip links / software FOSS deep-dives wait for phase 2 |
| Nebenan change control | If platform becomes a funded deliverable, clear it with foundation if it shifts approved content |

---

## 12. Roadmap sketch (re-sequenced)

| Phase | Outcome | Gate |
|-------|---------|------|
| **Concept** (this doc) | Aligned with minutes | Done |
| **Partner cheat sheet + shop outreach** | Verifiers possible | By ~15 Sep (team commitment) |
| **Workshop content v1 + #1 delivered** | Real users exist | From ~Nov |
| **Un-park decision** | Explicit team YES | After workshops 1–3 *or* strong shop pull |
| **Data & consent one-pager** | GDPR checklist | Before build |
| **Pilot build** | Capped deploy | Only after un-park |
| **Phase 2** | Tip links, software-cos, richer projects | After ~3–4 workshops |

---

## 13. Open questions (still open after meeting)

1. Age band for pilot (12–15 vs 15–18)?  
2. Hard cap numbers (teams / users)?  
3. First verifier: which shop/café commits?  
4. Public leaderboard vs opt-in visibility?  
5. Challenge brand name?  
6. Does Nebenan proposal already imply a digital platform, or must we amend if we build one?

---

## 14. Decision status

| Ask | Status |
|-----|--------|
| Ship capped engagement platform in parallel with workshops 1–3 | **Not agreed** — parked |
| Keep concept alive and align with shops + confidence metrics | **Yes** (this revision) |
| Revisit build when? | After partner traction + early workshops, or sooner if team explicitly prioritises |

---

*Next doc candidates (when un-parked): `Data Map & Consent.md`, `Badge Ladder.md`, `Shop Verifier Guide.md` (tied to partner cheat sheet).*
