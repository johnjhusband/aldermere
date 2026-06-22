# Aldermere

A multi-tenant web and mobile app that turns any task list into a continuing, AI-generated fantasy story.

One person — the **Governor** — starts a world, provides a task list, and invites players. The AI wraps the tasks into an ongoing narrative and keeps the story going forever as tasks are completed and added.

## Status

Pre-build. Active design phase. See [`PRD.md`](PRD.md) for the product requirements document.

## Stack (planned)

- **Front end (web + iOS + Android, one codebase):** Expo / React Native + React Native Web
- **Back end:** Node.js + TypeScript, Docker, Hetzner VPS
- **Database:** One-per-world (multi-tenant by isolation)
- **AI:** OpenAI (text, image, vision)
- **Email:** Resend
- **Auth:** Google Sign-In

## License

TBD.

---

*Published by Husband, LLC. Contact: john@husband.llc*
