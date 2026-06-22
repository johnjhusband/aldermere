# Aldermere — Product Requirements Document

**Owner:** John Husband
**Story lead / creative director:** Maria Harrell
**Tech co-developer:** Claude
**Last updated:** 2026-06-21

---

## 1. What it is

A multi-tenant web + mobile app that turns any task list into a continuing, AI-generated fantasy story. One person (the **Governor**) starts a world, provides a task list, and invites players. The AI wraps the tasks into an ongoing narrative — a magical kingdom by default — and keeps the story going forever as tasks are completed and added.

The original inspiration was household chores. The engine is generic — a family doing chores, a business running projects, a non-profit organizing volunteers, or one person trying to clean their house are all valid uses.

**Aldermere is not an MMORPG.** Each world is small, private, and unique to its players. No two worlds are the same.

## 2. Roles

- **Real Maria Harrell** — creative director. Builds the canonical world content seeded into every new world. Has approved use of her real first name as the in-fiction Editor.
- **In-fiction Maria** — the Editor character of every world's Gazette. Same name in every world. The AI writes in her voice.
- **AI** — does all actual writing, image generation, photo evaluation, and Governor/player interviews.
- **Governor** — creates a world, defines the task list, invites/removes players, sets the rating and rules. May also play.
- **Player** — joins a Governor's world, takes on tasks, sees the story unfold.
- **Solo Governor** — Governor who is the only player.

## 3. Canonical world content

Every new world starts seeded with Maria's canon — characters like King Ferdian, places like the Fountain of Whispers and the Copper Kettle Tavern, institutions like the Laundry Guild, the Arcane Floorkeepers, the Knights of Vitality, the Animal Rights Coalition, etc.

The AI **adapts** the canon during the Governor interview — names, locations, factions, and tone can be tuned to fit the world's purpose. King Ferdian is always present in some form. The Gazette is always edited by Maria.

## 4. The Governor's setup interview

When a new world is created, the AI interviews the Governor to set:

- World name (default: Aldermere)
- Theme / setting / tone preferences and how to adapt canon to them
- **Content rating** — G, PG, PG-13, R, or NC-17 (locks AI content generation)
- **Language(s)** the world should be played in
- Task list (paste, upload, or pick a template: housework, office, etc.). If the AI doesn't understand a task, it asks clarifying questions.
- Per-task assignment vs. shared pool
- Photo policy — required, optional with bonus, or off
- Notification frequency for players (email cadence)
- Real-world time zone / region for the world
- Whether all players start in one location, or players in different time zones start in different parts of the world (and can travel to meet, for a cost)
- Guardrails for what players may request as rewards

## 5. Core mechanics

- Each task becomes a story beat / quest the AI weaves in. Tasks may be simple or complex; AI asks clarifying questions if needed.
- Completing a task gives base rewards: **Gold, Skill, Strength, Energy** (and others as needed).
- Submitting a **photo** gets the AI to evaluate completion quality. Bonus points for exceptional quality. The AI reports its opinion to the player and the Governor. The player may reshoot. The Governor may request a redo or accept the task as-is.
- Photos are visible to the AI and the Governor. The Governor may choose to publish a photo to other players (e.g. for celebration).
- Stats unlock cosmetic and narrative items: character images, mounts, armor, weapons, custom scenes (e.g. a wedding, a shirt color change). Bigger requests cost more tasks.
- Players can **propose new tasks**. They can begin work immediately but only earn rewards once the Governor approves.
- Players are encouraged to break large tasks into smaller ones — more rewards, more story.
- Skipping a task has narrative consequences (the party happens without you, the dragon finishes the soup) but never a punitive tone. Time-sensitive tasks get urgency arcs.
- Cross-world travel between separated player starting points costs tasks. The AI sets the cost adaptively.
- The game has no end. When a task list is exhausted and the Governor adds new tasks, a new storyline begins.

## 6. Game Names and identity

- Every Governor and every Player chooses a **Game Name** during onboarding.
- Game Name is the public identity inside the world. Real names and email addresses are not shown to other players.
- A Game Name can be changed later for a cost. The AI sets the cost adaptively per player based on what is motivating to them.
- One real user (Google account) may have a different Game Name in each world they play in.
- **DB naming:** The world's database is named after the Governor's Game Name **at the moment of world creation**. The DB name never changes, even if the Governor later changes their displayed Game Name. Pattern: `{governor_game_name_at_creation}` for the first world, `{governor_game_name_at_creation}_2`, `_3`, etc.

## 7. Players and the shared world

- All players in a world share the same evolving story but experience it from their own perspective.
- If two players encounter the same scene, they see the **same AI-generated image and same text**. Generated assets are stored per-world for reuse.
- Story content adjusts writing style per player to maximize motivation. The AI may use multiple in-fiction writers under Editor Maria, each tuned to a player.
- The AI is calendar-aware — season, holiday, time-of-day shape the story based on each player's starting region.
- If a player is removed from a world, their character "leaves the kingdom" in fiction. The impact they had on the world remains.

## 8. Player characters

- Customize: **gender** (male or female), race, stats, name, look (via self-description).
- AI generates the character portrait from the description.
- Appearance is cosmetic only. Has no gameplay effect.
- Roughly consistent across scenes (comic-book-style, not pixel-perfect).

## 9. Player onboarding flow

1. Player receives an **email invitation** from a Governor.
2. Player signs in with Google.
3. Player is shown the world's content rating and must accept it. For R and NC-17, age confirmation is required.
4. Player chooses a Game Name.
5. Player is introduced to the world's lore.
6. Player reads the first Gazette.
7. Player creates their character.
8. Player begins.

## 10. Children

- Under-13 children play alongside a parent on the parent's Google account.
- When a child turns 13 and gets their own Google account, they join the world as their own player.

## 11. Outputs and content types

- **Newspaper-style** story digest (The Aldermere Gazette by default).
- **Quest descriptions** for each task.
- **Still images** for scenes, characters, items.
- **Story completion text** when tasks or arcs are completed.
- **No animation.** Ever.

## 12. Story regeneration

- **New content generates when a player interacts with the app**, not on a fixed schedule.
- The AI is given a compressed summary of prior story state plus relevant facts from the database. It does not re-read the full story every time.
- When the AI's context window reaches ~50% full during a story arc, the AI begins gracefully bringing the current arc to a close.
- If players keep playing, **compression** of completed story segments is used to keep the narrative going.
- The full story (text and image references) is persisted in the world's database and is the source of truth for fact-checking.

## 13. Notifications

- **Story-flavored** email and mobile push notifications to each player with their open tasks, on a cadence the Governor sets. Tone matches the world; the message reads like in-fiction correspondence, not a checklist.
- Push notifications are delivered to the iOS and Android apps in addition to email.
- Players may unsubscribe from email and/or disable push (still able to use the app).

## 14. Technical

- **AI provider:** OpenAI (text, image generation, vision for photo evaluation). Specific models chosen by Claude as build progresses.
- **Email service:** Resend.
- **Backend:** Docker on Hetzner VPS.
- **Database:** Multi-tenant by per-world isolation. One database per world. See §6 for naming.
- **Photo and asset storage:** Object storage (Hetzner Storage Box or S3-compatible).
- **Web:** Responsive HTTPS site.
- **Mobile:** Native iOS and Android apps. All three interfaces (web, iOS, Android) ship together at first release.
- **Codebase:** Single codebase. Stack: Expo / React Native + React Native Web for the front end. Node.js + TypeScript for the back end.
- **Auth:** Google Sign-In.

## 15. World lifecycle

- A world exists as long as the Governor keeps it active.
- If a Governor abandons or cancels, the world is **archived** (not deleted). Archived worlds are kept forever for now.

## 16. Business model

- Free to start. No cost ceilings or quotas at launch.
- Paid subscription to follow once people are actively using it.

## 17. What it will NOT do

- No animation.
- No real-money trading between players.
- No content beyond the Governor's chosen rating.
- No guilt-driven mechanics. Missed tasks are narrative, not punitive.
- No gameplay effect from character appearance.
- No cross-world player interaction. Each world is its own universe.

## 18. Launch scope

Full feature scope ships at first release: all features above are built into the single codebase, producing web + iOS + Android. The **public web app launches first** at `aldermere.world`. The **iOS and Android binaries are built and ready** but distribution to the Apple App Store and Google Play happens once the developer accounts are set up — these are deferred per John.

## 19. Setup checklist

| Item | Status | Notes |
|---|---|---|
| OpenAI API access + billing | ✅ ready | |
| Hetzner VPS | ✅ ready | Details pending from John |
| Resend account (email) | ⏳ needed | Will set up |
| `aldermere.world` domain | ✅ registered (Namecheap) | |
| Public GitHub repo `johnjhusband/aldermere` | ⏳ to create | |
| Apple Developer Program ($99/yr) | ⏸ deferred | Required to distribute iOS app via App Store |
| Google Play Console ($25 one-time) | ⏸ deferred | Required to distribute Android app via Play |
| Privacy policy + Terms of Service | ⏳ needed | Publishing entity: **Husband, LLC**; contact: `john@husband.llc` |

## 20. Open questions

Tracked in chat with John — see follow-up.
