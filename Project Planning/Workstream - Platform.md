# Workstream — Platform

**Proposed lead:** Alex · **Product/content:** Peter · **School ops:** Avanti  
**Concept:** [`../Engagement Platform/High-Level Concept.md`](../Engagement%20Platform/High-Level%20Concept.md)  
**Aug 2026 status:** parked · **Sep planning intent:** **un-park and ship a capped pilot by workshop #1 (~Nov)**

Do not rebuild a youth social network. Ship: **teams + actions + badges** (+ optional lore / e-waste kg later).

---

## Decision gate (do this first)

- [ ] Team explicit **YES** to un-park (log in next meeting minutes)
- [ ] Confirm Nebenan: digital platform OK under funded scope (or amend if needed)
- [ ] Name a platform owner
- [ ] Choose stack (see below)
- [ ] Age band for pilot (12–15 vs 15–18)
- [ ] Hard caps (max teams / users)
- [ ] Challenge brand: plain *IsarPunk challenge* / *May Migration* / *LinuXmas* / other

Until YES is logged, treat build time as **spike only** (≤1 weekend), not a parallel product.

---

## Checklist

### Before build
- [ ] Privacy / consent one-pager (sponsor-first, minimal youth data)
- [ ] Data fields list (team name, school, sponsor email, actions, badges — nothing extra)
- [ ] Invite / workshop code scheme
- [ ] Admin moderation path (approve / reject claims)

### Build (v0 pilot)
- [ ] Auth for **adult sponsor** (not open kid Discord free-for-all)
- [ ] Team registration under cap
- [ ] Activity log: workshop attended, confidence check-in, Oma talk, shop referral, install (claimed)
- [ ] Badge display on team page
- [ ] Admin dashboard: pending → approved
- [ ] Public board: team names + badge counts only

### Nice-to-have before workshop #1 (only if v0 is stable)
- [ ] Lore text field on verified actions
- [ ] Estimated e-waste kg secondary counter
- [ ] `fastfetch` + handwritten note proof guidance for install badges

### After workshop #1–3
- [ ] Shop verifier seat (≥1 partner)
- [ ] Tip / Ko-fi outbound links (phase 2 — not required for pilot)
- [ ] Iterate badges from real workshop behaviour

---

## Stack choice (pick one and freeze)

| Option | When to use | Cost | Notes |
|--------|-------------|------|-------|
| **A — Shoestring** Tally → Airtable → Softr | Need live site in days; low custom UI | ~€0 | Fastest path to Nov |
| **B — Hacker** Next.js/Vite + Supabase | Need custom IsarPunk aesthetic + control | ~€0–5/mo + domain | More build time |
| **C — Analog first** Forms + sheet + manual leaderboard | If GDPR/school fear or capacity crash | €0 | Still “a platform” for reporting; upgrade later |

**Recommendation for Nov:** start **A** or **C**; only choose **B** if Alex has clear spare capacity and YES is logged.

**Decision:** _[ ] A  [ ] B  [ ] C_ · decided on: ______ · by: ______

---

## Pilot success

| Signal | Target |
|--------|--------|
| Live before or at workshop #1 | Yes |
| Teams registered | Under cap; ≥1 real school team |
| Confidence-related actions logged | Yes |
| Shop verify | Optional at pilot; required for “Verified Install” full badge |
| Empty public spam board | Avoid — invite codes only |

---

## Build log

| Date | What shipped | Blocker |
|------|--------------|---------|
| | | |

---

## Open product questions

1. Public leaderboard vs opt-in visibility?  
2. First verifier shop?  
3. Printable badge sticker twins for IRL?  
4. EU hosting constraint for chosen stack (Softr/Airtable regions — check before school PII)?
