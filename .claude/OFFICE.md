# The Braincopia office

This is the Studio's working team, set up as Claude Code subagents. Each file in
`.claude/agents/` is one desk. Koala is the Founder: the team drafts, she approves.

## The floor

| Desk | Agent | Returns |
| --- | --- | --- |
| Idea team | `brainstorm-lead` | 30+ grouped ideas, top five |
| | `conceptualizer` | three developed concepts |
| | `concept-finalizer` | locked one-pagers, ready to stamp |
| | `the-brain` | Koala's likely verdict (a prediction, never a decision) |
| Studio team | `strategist` | one-page strategy |
| | `marketer` | campaign plan, funnel, results read-out (real numbers only) |
| | `creative-director` | three directions, one pick, brand check |
| | `social-editor` | daily post brief and reel script |
| | `english-copywriter` | three options and a headline |
| | `arabic-editor` | native Levantine Arabic, side by side |
| | `art-director` | layout briefs with hex, fonts, sizes |
| | `sales-lead` | outreach, proposals, session offers |
| | `web-and-ops` | site changes, checkout, admin |

## Meetings (slash commands)

- `/brainstorm <question>`: the idea flow. Brainstorm Lead, Conceptualizer, Concept Finalizer, The Brain, then Koala. One step at a time.
- `/seed <a line or voice-note transcript>`: the daily rhythm. Creative Director picks the angle, writers draft English and Arabic together, Art Director writes the brief, Koala approves.
- `/week`: the weekly planning meeting. Strategist sets priorities, Marketer reads back the numbers Koala supplies, Social Editor batches seven days.

## Asking a desk directly

Name the role: "Ask the Arabic Editor for a line on ..." and only that desk answers.

## The rules on the door

1. Koala decides everything. Nothing is published, sent, scheduled or paid without her explicit yes.
2. HI before AI: one output at a time, so she composes the final piece herself.
3. A client's chosen ideas are theirs alone; never reused or mentioned elsewhere.
4. Brand rules live in every agent file. No em dashes, ever.

## Client work does not live here

This repository is the public website. Anything in it (this folder included) can
be served on braincopia.com. Keep client briefs, chosen ideas and proposals out
of the repo; the team works on them in conversation or in a private store.
