# Braincopia: working in this repo

Two things live here: the braincopia.com static site (see README.md) and the
Studio's working team in `.claude/` (see `.claude/OFFICE.md`).

When a request is for the team, run it through the agents in `.claude/agents/`:

- A named role answers alone, as that role, returning only its output.
- A request that spans roles runs in flow order, one step at a time, and stops
  for Koala's approval between steps. Do not chain steps without her yes.
- Never publish, send, schedule, post, push to the live branch or pay anything
  without Koala's explicit yes.
- Never write em dashes in copy.
- Never commit client briefs or chosen ideas to this repo; it is public.
