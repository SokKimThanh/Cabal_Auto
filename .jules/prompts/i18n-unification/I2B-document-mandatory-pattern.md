# I2B - Document The Mandatory Pattern For New Screens

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 2 documentation task from .jules/i18n-sprint-roadmap.md.

Goal:
Write docs/guides/I18N_GUIDE.md describing the mandatory pattern for adding a new bilingual screen: define a *_TRANSLATIONS dict, self-register it at the bottom of its own data module (not from the consumer), choose a unique namespace string, and rely on the Sprint 2 audit test to catch a missed registration. Add a short pointer to this guide from CODING_RULES_QUICK_REFERENCE.md.

Files in scope:
- docs/guides/I18N_GUIDE.md (new)
- CODING_RULES_QUICK_REFERENCE.md

Boundaries:
- Keep the guide practical and short: a code example plus a checklist, not a long essay.
- Do not restate the entire roadmap; link to .jules/i18n-sprint-roadmap.md for historical context instead.

Acceptance criteria:
- A developer or Jules session can follow the guide alone to add a new bilingual screen correctly on the first try.

Validation:
- Re-read the guide as if implementing a brand-new screen from scratch and confirm every step is unambiguous.
```
