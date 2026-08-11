# IsarPunk Engagement Platform — High-Level Concept

**Status:** Concept v0 · **Audience:** project team  
**Spirit:** Small, sharp, fun, compliant — not an enterprise youth network.

---

## 1. Why this exists

School workshops sow the *Save Oma / FOSS upcycle* story. Without a place to **show progress**, energy evaporates after the bell.

The engagement platform is the **scoreboard and clubhouse** for that energy:

- School teams register and track meaningful actions (including Linux installs)
- Partner labs can **verify** claims
- Teams earn **badges** (status, not surveillance)
- Teams can publish **project ideas** and optional tip links (e.g. Buy Me a Coffee / Ko-fi)

IsarPunk runs **dispersal workshops** (~6 / school year). Hubs (MuCCC, repair shops, FabLab, Repair Cafés) own deep installs and refurb. The platform **amplifies** that split — it does not replace the hubs.

**Timeline advantage:** consumer Windows 10 ESU runs to **12 October 2027**. Use the runway to grow a capped, trusted challenge — not a panic app.

---

## 2. One-sentence product

> A **capped school-team challenge tracker** where Munich youth log FOSS / upcycle actions, get lab-verified badges, and optionally crowdfund their own follow-on projects — designed from day one for **minimal youth data**.

---

## 3. Goals

| Goal | Meaning |
|------|---------|
| **Engage** | Give workshop survivors a reason to come back |
| **Make progress visible** | Installs and missions show up for the team and (lightly) the city |
| **Route to hubs** | Verification and “go deeper” paths point at MuCCC / labs |
| **Stay shippable** | Experienced IT + AI; hard user caps; no social network feature creep |
| **Earn trust** | Youth + GDPR is the hardest problem — we design for it, not around it |

### Non-goals (v0)

- Chat, DMs, feeds, likes, or open social graph  
- Being the install / refurb service  
- Payment processing (tip links are outbound only)  
- Unlimited public signup  
- Replacing Jugend hackt, MuCCC, or school LMS  

---

## 4. Who it’s for

| Actor | Role |
|-------|------|
| **School team** | Klasse, AG, Projektgruppe — the primary identity |
| **Adult sponsor** | Lehrer:in or Eltern contact; accountable for the team account |
| **Participants** | Youth who do the work (may have limited or no personal login in v0) |
| **Lab verifier** | MuCCC / shop / café staff who confirm events |
| **IsarPunk admin** | Cap users, issue lab accounts, moderate team names / tip links |

---

## 5. Core loop

```text
Workshop spark
    → Team registers (sponsor + school)
        → Log actions (claimed)
            → Lab verifies (optional but badge-gated)
                → Badges unlock
                    → Team page shows progress (+ optional tip link)
                        → Curious kids go deeper at the hub
```

**Success looks like:** a teacher says “our AG has three badges”; a lab stamps two installs; a kid asks MuCCC how to finish Oma’s laptop.

---

## 6. Feature pillars (v0)

### 6.1 Team registration
- Register as a **team**, not as a free-for-all kid social profile  
- Fields (minimal): team name, school, sponsor name + email, approximate age band, optional workshop code  
- Hard **cap** on teams / users (product feature — advertise it)

### 6.2 Activity log
Suggested action types (start small):

| Action | Claimable in workshop? | Needs lab verify for full badge? |
|--------|------------------------|----------------------------------|
| Attended IsarPunk workshop | Yes | No |
| “Oma talk” / family awareness chat | Yes (honour) | No |
| Live USB / first boot demo | Yes | Optional |
| Linux install completed | Yes | **Yes** for verified badge |
| Lab visit / open night attended | — | **Yes** |
| Custom team project published | Yes | Optional review by admin |

State machine: `claimed → lab_confirmed` (and `rejected` if needed).

### 6.3 Badges / social credit
- Badges reward **behaviours we can seed**, not only rare perfect installs  
- Examples: *Seed Planter*, *Oma Diplomat*, *First Boot*, *Verified Install*, *Lab Explorer*, *Project Starter*  
- Display on team page; printable sticker twins for IRL workshops later  
- “Social credit” = **reputation within the challenge**, not a creepy score sold to anyone

### 6.4 Projects + tip links
- Team can add a short **project idea** (title, 2–3 sentences, what they’d build)  
- Optional **Buy Me a Coffee / Ko-fi / similar** URL  
- IsarPunk never handles money; sponsor responsible for link appropriateness  
- Better fit for older teens; younger teams may skip funding fields

### 6.5 Lab verification
- Few privileged **lab accounts**  
- Labs confirm specific claims (install, visit) — no ID document uploads  
- Handoff narrative: verification *is* the bridge to the solution layer

---

## 7. Youth + GDPR as architecture

This is the hardest part — and the design constraint that keeps the product honest.

### Principles
1. **Minimal data** — only what the challenge needs  
2. **Team-first identity** — reduce per-child accounts  
3. **Adult sponsor** as primary contact / accountability  
4. **EU hosting** + written retention (e.g. wipe or anonymise after school year)  
5. **No behavioural adtech, no resale, no dark patterns**  
6. **Clear purpose** on signup: challenge participation and partner handoff  

### Practical v0 stance
- Prefer **sponsor login**; youth contribute through the team  
- If youth logins appear later: age-appropriate consent copy, sponsor acknowledgment, strict parental/guardian rules per GDPR / German practice  
- Public board shows **team names + badge counts**, not home addresses or birthdates  
- Publish a one-page privacy notice before pilot  

*(Detailed data map, DPIA-lite, and consent flows = follow-up doc.)*

---

## 8. Scope & caps

| Control | Intent |
|---------|--------|
| Invite / workshop codes | No infinite open internet signup |
| Max teams / max users | Operationally sane; “exclusive challenge” energy |
| Lab seats | Handful of trusted verifiers |
| Feature freeze for pilot | Tracker + badges + tip link; stop |

Pilot suggestion: workshops **1–3** cohorts only; expand caps when ops feel boring (that’s the green light).

---

## 9. What we build vs buy

| Need | Approach |
|------|----------|
| App (auth, teams, logs, badges) | Build thin (IT experience + AI) |
| Hosting | EU VPS / managed Postgres |
| Payments | **Don’t build** — outbound tip links |
| Chat | **Don’t build** — point to Matrix/hub nights if needed |
| Email | Transactional only (magic links / verify notices) |

Tech stack: deliberately undecided in this concept doc. Choose boring and fast when engineering starts.

---

## 10. Success metrics (platform)

| Metric | Why |
|--------|-----|
| Teams registered (under cap) | Adoption |
| Actions logged | Engagement |
| % lab-verified (where required) | Handoff health |
| Badges unlocked | Motivation working |
| Tip links added (optional) | Older-teen project energy |
| Qualitative: hub says “kids showed up because of the board” | Real loop |

Not a vanity metric: raw pageviews without teams.

---

## 11. Risks (and chin-up mitigations)

| Risk | Mitigation |
|------|------------|
| Empty board | Launch with workshop #1; seed demo teams |
| Labs won’t verify | Co-design the 10-second verify UX; start with MuCCC only |
| GDPR fear from schools | Sponsor model + privacy one-pager + minimal fields |
| Scope creep | Written non-goals; admin feature veto |
| Tip-link abuse | Sponsor responsibility + admin takedown |

---

## 12. Roadmap sketch

| Phase | Outcome |
|-------|---------|
| **Concept** (this doc) | Team alignment |
| **Data & consent one-pager** | GDPR checklist + field list |
| **UX wire skeleton** | Team page, log action, lab verify, badge wall |
| **Pilot build** | Capped deploy for first workshops |
| **Learn & tighten** | Badge balance, copy, lab workflow |
| **Widen** | More schools only after verify loop works |

---

## 13. Open questions for the team

1. Age band focus for pilot (12–15 vs 15–18)?  
2. Hard cap numbers (teams / users) for school year?  
3. Must MuCCC be verifier on day one, or IsarPunk admins stub verify until labs onboard?  
4. Public leaderboard vs opt-in team visibility?  
5. Brand name for the challenge layer (IsarPunk Challenge / Save Oma League / other)?  

---

## 14. Decision ask

Propose for goal-setting:

> **Ship a capped engagement platform** (school teams, activity log, lab verify, badges; optional tip links) under a youth-minimal GDPR design; pilot alongside workshops 1–3.

---

*Next doc candidates: `Data Map & Consent.md`, `Badge Ladder.md`, `Lab Verifier Guide.md`.*
