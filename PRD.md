# Aldermere — Product Requirements Document

**Owner:** John Husband
**Story lead / creative director:** Maria Harrell
**Tech co-developer:** Claude
**Last updated:** 2026-06-21

---

## 1. What it is

A multi-tenant web + mobile app that turns any task list into a continuing, AI-generated fantasy story. One person (the **Governor**) starts a world, provides a task list, and invites players. The AI wraps the tasks into an ongoing narrative — a magical kingdom by default — and keeps the story going forever as tasks are completed and added.

The original inspiration was household chores. The engine is generic — a family doing chores, a business running projects, a non-profit organizing volunteers, or one person trying to clean their house are all valid uses.

**Underlying goal:** help players build habits and patterns in a way that feels interactive — like taking part in a world, not following a checklist.

**Aldermere is not an MMORPG.** Each world is small, private, and unique to its players. No two worlds are the same.

## 2. Roles

- **Real Maria Harrell** — creative director. Builds the canonical world content seeded into every new world. Has approved use of her real first name as the in-fiction Editor.
- **In-fiction Maria** — the Editor character of every world's Gazette. Same name in every world. The AI writes in her voice.
- **AI** — does all actual writing, image generation, photo evaluation, and Governor/player interviews.
- **Governor** — creates a world, defines the task list, invites/removes players, sets the rating and rules. May also play.
- **Player** — joins a Governor's world, takes on tasks, sees the story unfold.
- **Solo Governor** — Governor who is the only player.

## 3. Conventions

**Control IDs.** Every feature has a stable Control ID of the form `ALD-XXX`. These IDs never change once assigned, even if section numbers shift.

**Prerequisites.** Each feature lists the Control IDs of other features it depends on. If a feature appears as a prerequisite, it must be built and passing tests before the dependent feature can be considered complete.

**Test blocks.** Every feature has a `### Test` block with these subsections:

- **Type & Scope** — test type (unit / integration / end-to-end / AI-eval), platforms (web / iOS / Android / backend / all).
- **Purpose** — what this test verifies and why.
- **Preconditions** — state required before the test runs.
- **Inputs** — concrete test data.
- **Steps** — ordered actions to perform.
- **Expected Results** — verifiable pass criteria.
- **Negative Cases** — what must fail, error, or be rejected.
- **AI Evaluation Criteria** — for AI-driven features: what's deterministic, what may vary, how the tester judges "good enough." Omitted when not AI-driven.

**Cleanup procedures, pass/fail reporting format, and test-runner choice are standardized once in `TESTING.md` (to be written when the codebase is scaffolded).** Per-test blocks here do not repeat them.

---

## 4. Canonical world content `ALD-001`
**Prerequisites:** ALD-002

Every new world starts seeded with Maria's canon. The seed includes:

**Characters:** King Ferdian; the Duke of Shambles (long-ago rival defeated by Ferdian in an arm-wrestling contest); Head Laundress Mabel; Foreman Phelps; Faye (Laundry Guild's newest recruit); Guildmaster Thorn (Arcane Floorkeepers); Mistress Thistlewick (publicly disagrees with Thorn on enchanted floor-cleaning methods); the Master-at-Arms (Knights of Vitality); Courier Wren (Royal Post).

**Places:** the Fountain of Whispers (with its periodic Endless Whisper cycles, current phrase "The geese know"); the Copper Kettle Tavern (which displays three separate tables each claiming to be the historic Ferdian arm-wrestling table); the Great Basin (Porcelain Republic territory, subject of recurring embargo rumors).

**Institutions:** the Laundry Guild; the Arcane Floorkeepers Guild; the Knights of Vitality; the Animal Rights Coalition; the Porcelain Republic; the Royal Culinary Society; the Royal Post; the Independent Artisans Guild.

**Recurring story patterns:**
- **Ongoing political plotlines** that thread through everyday tasks (e.g. the animal rights labor case in which mice suspend bedding services, so citizens maintain their own quarters)
- **Annual recurring festivals** (e.g. the Sheep Shearing Festival)
- **Mystery / lore plotlines** (e.g. the Fountain of Whispers' "Endless Whisper cycle")
- **Historical disputes** (e.g. the three Copper Kettle tables debate)
- **Diplomatic rumors** (e.g. the Great Basin embargo)
- **The Day of Recovery** — periodic rest acknowledgment attributed to the Knights of Vitality; rest is treated as part of the work, not the absence of it
- **Wisdom quotes attributed to NPCs** — e.g. the Master-at-Arms's "Strength is not built during training, but during recovery from it"

The AI **adapts** the canon during the Governor interview — names, locations, factions, and tone can be tuned to fit the world's purpose. A character playing the King Ferdian role (with a name rooted in "Ferdian") is always present. The Gazette is always edited by Maria. The recurring story patterns above are preserved in adapted form.

### Test
- **Type & Scope:** AI-eval, end-to-end; backend + web.
- **Purpose:** Verify every new world contains Maria's canon, adapted to the Governor's stated theme, with a Ferdian-rooted leader figure and Editor Maria intact.
- **Preconditions:** A newly created world that has just completed the Governor interview.
- **Inputs:** Three test interview transcripts producing three distinct worlds — (a) classic medieval housework, (b) modern startup office, (c) sci-fi space station.
- **Steps:** For each test world, generate the first Gazette and the first three quest descriptions. Read all generated text.
- **Expected Results:** Each world's generated text contains (a) at least one identifiable canon element (a character, place, or institution from canon, possibly renamed), (b) a leader character whose name contains the "Ferdian" root (e.g. "King Ferdian", "Commander Ferdian", "Director Ferdian"), and (c) "Maria" identified as the Editor of the Gazette (surname optional or adapted).
- **Negative Cases:** Leader character missing or unrelated to "Ferdian" → fail. Maria absent as Editor → fail. Zero canon elements present → fail.
- **AI Evaluation Criteria:** The role and the "Ferdian" name root must persist. Surname forms of Maria may vary. Renamed institutions are acceptable if their function (laundry, floors, knights, animal advocacy) maps to canon.

---

## 5. Governor's setup interview `ALD-002`
**Prerequisites:** ALD-038, ALD-044

When a new world is created, the AI interviews the Governor to set:

- World name (default: Aldermere)
- Theme / setting / tone preferences and how to adapt canon to them
- **Content rating** — G, PG, PG-13, R, or NC-17 (locks AI content generation)
- **Language(s)** the world should be played in
- Task list (paste, upload, or pick a template: housework, office, etc.). If the AI doesn't understand a task, it asks clarifying questions. **Each task includes a recurrence:** one-time, daily, weekly, monthly, or custom cadence.
- Per-task assignment vs. shared pool
- Photo policy — required, optional with bonus, or off
- Notification frequency for players (email cadence)
- Real-world time zone / region for the world
- Whether all players start in one location, or players in different time zones start in different parts of the world (and can travel to meet, for a cost)
- Guardrails for what players may request as rewards

### Test
- **Type & Scope:** AI-eval, end-to-end; web.
- **Purpose:** Verify the AI conducts the full interview, captures every required field, asks clarifying questions for ambiguous tasks, and persists the result in the world's database.
- **Preconditions:** A signed-in Google user with no existing worlds.
- **Inputs:** A test transcript that supplies: world name "Test Realm", theme "medieval kitchen staff", rating "PG", language "English", task list including one clear daily-recurring task ("wash the dishes — daily"), one clear one-time task ("clean out the attic — once"), and one deliberately ambiguous task ("handle the thing"), shared pool, photo optional, daily notifications, US/Mountain timezone, single starting location, no special reward guardrails.
- **Steps:** Trigger world creation. Walk through every prompt the AI asks. Provide the test answers. Submit. Inspect the resulting world record.
- **Expected Results:** All 11 listed fields are captured and stored. Each task's recurrence is captured (daily / one-time / etc.). The AI explicitly asks at least one clarifying question about "handle the thing" before accepting it as a task. The world record matches the inputs.
- **Negative Cases:** AI accepts "handle the thing" without clarification → fail. AI skips any of the 11 fields → fail. AI persists wrong values → fail.
- **AI Evaluation Criteria:** Prompt wording and question ordering may vary. The interview must cover every field; whether it asks them as separate questions or batched is acceptable either way. Clarifying-question phrasing is free-form but must explicitly reference the ambiguous task.

---

## 6. Core mechanics

### 6.1 Task → quest conversion `ALD-003`
**Prerequisites:** ALD-001, ALD-002

Each task becomes a story beat / quest the AI weaves in. Where possible, the AI connects the task to a multi-day storyline so that completing the task becomes participation in a larger plot — e.g. "make the bed" becomes maintaining your quarters during the animal rights labor case (mice on strike).

#### Test
- **Type & Scope:** AI-eval, integration; backend.
- **Purpose:** Verify each task in the Governor's list produces a corresponding in-world quest description that references the task action.
- **Preconditions:** A world exists with a known task list of 5 tasks.
- **Inputs:** Task list: ["make the bed", "sweep the kitchen", "take out the trash", "feed the dog", "water the plants"].
- **Steps:** Trigger quest generation for the world. Retrieve the generated quest entries for all 5 tasks.
- **Expected Results:** Exactly 5 quests are generated. Each quest references the underlying task action in some recognizable form. Each quest references at least one canon element (a faction, character, or place).
- **Negative Cases:** Missing quests, duplicate quests, quests that don't relate to the action.
- **AI Evaluation Criteria:** Quest wording is free-form. "Make the bed" can become "the bedchamber requires order" — passes as long as the action is recognizable.

### 6.2 Base rewards `ALD-004`
**Prerequisites:** ALD-003

Completing a task gives base rewards: **Gold, Skill, Strength, Energy** (and others as needed). In addition to per-task rewards, the engine supports **daily aggregate rewards** — e.g. +1 Skill for completing a recurring task on a given day. Daily aggregate rewards are configured per-task by the AI based on the world's flavor and rhythm.

#### Test
- **Type & Scope:** Unit + integration; backend.
- **Purpose:** Verify task completion writes the correct reward values to the player's stat record.
- **Preconditions:** A world exists with a player whose stats are all 0. A daily-recurring quest exists with a defined per-task reward (5 Gold, 1 Skill) and a daily-completion bonus (+1 Skill).
- **Inputs:** Mark the quest as complete on day 1. Mark it complete again on day 2.
- **Steps:** Submit day-1 completion. Read stats. Advance the in-app day. Submit day-2 completion. Read stats.
- **Expected Results:** After day 1: Gold = 5, Skill = 2 (1 per-task + 1 daily bonus), Strength = 0, Energy unchanged. After day 2: Gold = 10, Skill = 4, Strength = 0, Energy unchanged.
- **Negative Cases:** Daily bonus applied twice on the same in-app day → fail. Rewards applied to the wrong player → fail. Doubled per-task rewards on duplicate submission → fail. Completion accepted twice on the same day for the same quest → fail.

### 6.3 Photo evaluation and visibility `ALD-005`
**Prerequisites:** ALD-004, ALD-042

Submitting a photo gets the AI to evaluate completion quality. Bonus points for exceptional quality. The AI reports its opinion to the player and the Governor. The player may reshoot. The Governor may request a redo or accept the task as-is. Photos are visible to the AI and the Governor. The Governor may choose to publish a photo to other players (e.g. for celebration).

#### Test
- **Type & Scope:** AI-eval + integration; all platforms.
- **Purpose:** Verify photos are evaluated, scored, visible to AI + Governor only by default, and that publish-to-players works when the Governor opts in.
- **Preconditions:** A world with one Governor and two players. An open quest "make the bed" with photo optional.
- **Inputs:** Three photos — (a) a clearly-made bed, (b) a half-made bed, (c) a photo of a cat unrelated to the task.
- **Steps:** Player A submits photo (a). Player B submits photo (b). A third submission attempts photo (c). For each, retrieve the AI's evaluation, the player's view, the Governor's view, and the other player's view. Then Governor publishes photo (a) to all players.
- **Expected Results:** Photo (a) scored "exceptional" with bonus rewards applied. Photo (b) scored "complete, normal" with base rewards. Photo (c) flagged as not matching the task with no reward; the AI offers the player a reshoot option. AI's reasoning is visible to the submitting player and the Governor. Other players cannot see the photos. After publishing, all players see photo (a) with a celebratory caption.
- **Negative Cases:** A photo visible to other players without Governor approval → fail. AI fails to flag a clearly off-topic photo → fail. Bonus applied without "exceptional" judgment → fail.
- **AI Evaluation Criteria:** "Exceptional" vs. "normal" judgments may vary between runs, but a clearly-made bed must score at least "normal," a half-made bed must not score "exceptional," and an off-topic photo must score zero.

### 6.4 Reward unlocks `ALD-006`
**Prerequisites:** ALD-004, ALD-024

Stats unlock cosmetic and narrative items: character images, mounts, armor, weapons, custom scenes (e.g. a wedding, a shirt color change). Bigger requests cost more tasks.

#### Test
- **Type & Scope:** AI-eval + integration; backend + web.
- **Purpose:** Verify players can spend stats to unlock items, and the AI adaptively prices requests proportional to scope.
- **Preconditions:** A player with 100 Gold and 50 Skill. The world allows custom requests.
- **Inputs:** Three player requests — (a) "change my character's shirt color to red", (b) "give me a brown horse", (c) "stage a full wedding scene for my character with three guests and a feast."
- **Steps:** For each request, the AI proposes a cost in tasks/stats. Player accepts and pays. Verify the unlocked item is delivered.
- **Expected Results:** Request (a) is cheap (single-digit Gold or 1 task). Request (b) is mid-priced. Request (c) is the most expensive of the three. After payment, each unlock produces the corresponding asset (updated portrait, mount image, wedding scene with images and story text). Stats are correctly debited.
- **Negative Cases:** Cost ordering reversed (wedding cheaper than shirt color) → fail. Item not delivered after payment → fail. Stats debited without delivery → fail.
- **AI Evaluation Criteria:** Exact costs vary. The required invariant is **scope-proportional pricing**: bigger asks cost more.

### 6.5 Player-proposed tasks `ALD-007`
**Prerequisites:** ALD-003, ALD-004

Players can propose new tasks. They can begin work immediately but only earn rewards once the Governor approves.

#### Test
- **Type & Scope:** Integration; all platforms.
- **Purpose:** Verify the propose / start / approve / reward flow works in order.
- **Preconditions:** A world with one Governor and one player.
- **Inputs:** Player proposes a new task: "wash the car." Player marks it complete before approval. Governor later approves the proposal.
- **Steps:** Submit proposal. Verify it appears in Governor's queue. Player marks complete. Verify no reward yet. Governor approves the task. Verify reward applies retroactively.
- **Expected Results:** Proposal queued for Governor. Player may mark complete pre-approval but earns 0. On Governor approval, the previously-completed work yields full reward.
- **Negative Cases:** Reward issued before approval → fail. Approval doesn't backfill the prior completion → fail. Governor sees no proposal queue → fail.

### 6.6 Long-task decomposition encouragement `ALD-008`
**Prerequisites:** ALD-002

Players are encouraged to break large tasks into smaller ones — more rewards, more story.

#### Test
- **Type & Scope:** AI-eval; backend.
- **Purpose:** Verify the AI suggests breaking down a task that's obviously too large.
- **Preconditions:** A world.
- **Inputs:** A new task: "build a garage."
- **Steps:** Submit the task during interview or via player proposal. Capture the AI's response.
- **Expected Results:** AI flags this as a long task and proposes a decomposition (at least 3 sub-tasks).
- **Negative Cases:** AI accepts "build a garage" as a single quest with no suggestion → fail.
- **AI Evaluation Criteria:** Specific sub-tasks may vary. The AI must (a) recognize the task is long-scope and (b) propose at least 3 concrete sub-tasks.

### 6.7 Skipping and narrative consequences `ALD-009`
**Prerequisites:** ALD-003, ALD-030

Skipping a task has narrative consequences (the party happens without you, the dragon finishes the soup) but never a punitive tone. Time-sensitive tasks get urgency arcs.

#### Test
- **Type & Scope:** AI-eval; backend.
- **Purpose:** Verify the AI handles skipped tasks with narrative consequence and never with shame, scolding, or punitive language.
- **Preconditions:** A world with a player who has one completed task and three skipped tasks (one of which had an urgency arc — a princess to save).
- **Inputs:** Trigger the next Gazette generation.
- **Steps:** Read the generated Gazette and any direct messages to the player.
- **Expected Results:** Skipped tasks are referenced as in-story events (the party went on, the laundry piled up, the princess was eaten). The player is not blamed, shamed, or told they "failed."
- **Negative Cases:** Any of: "you failed", "you are behind", "you should have", "you didn't" framed as accusation, guilt-inducing language → fail. Any negative scoring of the player's character → fail.
- **AI Evaluation Criteria:** A tester AI scans output for punitive language using a fixed list of phrases AND a general sentiment check. Narrative consequence is OK; personal blame is not.

### 6.8 Cross-region travel costs `ALD-010`
**Prerequisites:** ALD-002, ALD-004

When players start in different regions due to timezone splits, travel to meet costs tasks. The AI sets the cost adaptively.

#### Test
- **Type & Scope:** Integration + AI-eval; backend.
- **Purpose:** Verify two players in different starting regions can be quoted a cost in tasks to meet, and that paying the cost moves their characters together.
- **Preconditions:** A world configured with regional starting points. Player A in Region North, Player B in Region South. Player A has at least 5 tasks pending in their assignment.
- **Inputs:** Player A requests to travel to Player B's region.
- **Steps:** Submit travel request. Capture quoted cost. Player A completes the quoted tasks. Verify position update.
- **Expected Results:** A cost is quoted (non-zero, finite, and feasible relative to Player A's remaining task pool — i.e. completion of the travel cost would not consume more than the pending tasks already available or proposable). On payment, Player A's region in the database changes to South. The next Gazette references the journey.
- **Negative Cases:** Travel granted without cost → fail. Cost never resolves on payment → fail. Quoted cost requires more tasks than the player can realistically complete → fail.
- **AI Evaluation Criteria:** Cost value may vary; must be feasible given the player's current and proposable task supply.

### 6.9 No end `ALD-011`
**Prerequisites:** ALD-033

The game has no end. When a task list is exhausted and the Governor adds new tasks, a new storyline begins.

#### Test
- **Type & Scope:** AI-eval, end-to-end; backend.
- **Purpose:** Verify the game continues indefinitely as new tasks are added, with a new storyline arc beginning after a prior arc concludes.
- **Preconditions:** A world with all current quests completed and the prior storyline arc closed.
- **Inputs:** Governor adds 3 new tasks.
- **Steps:** Trigger next story generation.
- **Expected Results:** A new storyline arc begins that references the new tasks. The new arc may reference past arcs (the kingdom remembers) but introduces fresh narrative threads.
- **Negative Cases:** Story returns "the end" or refuses to continue → fail. New arc ignores the new tasks → fail.
- **AI Evaluation Criteria:** Specific story content is free-form. The arc must (a) introduce at least one new thread and (b) wrap each of the new tasks into the narrative.

### 6.10 Milestone events as rewards `ALD-049`
**Prerequisites:** ALD-004, ALD-030

When the world or a player crosses a milestone (e.g. 100 tasks completed, an arc concluded, a specific count of recurring task completions), the AI may schedule an in-fiction event as a reward — a party, a parade, a ceremony, an announcement. The event happens at a moment in story time; players who are active around that moment experience it. Players who are inactive may miss it (the party happens without them).

#### Test
- **Type & Scope:** AI-eval + integration; backend.
- **Purpose:** Verify the AI schedules milestone events on the right triggers and that participation is gated by activity at the right moment.
- **Preconditions:** A world with two players who have together completed 99 tasks. The world's milestone trigger is set at 100 tasks.
- **Inputs:** Player A completes the 100th task. Player B is inactive for the next 3 in-app days.
- **Steps:** Verify a milestone event is scheduled. Trigger generation for Player A immediately. Then trigger generation for Player B after their inactive period.
- **Expected Results:** A milestone event (e.g. a celebration) is scheduled in the world state. Player A's Gazette references their attendance / participation. Player B's Gazette mentions that the event happened but that Player B was not present.
- **Negative Cases:** No event scheduled at milestone → fail. Event held without referencing the player population → fail. Player B receives full participation experience despite inactivity → fail.
- **AI Evaluation Criteria:** Specific event type (party, parade, ceremony) may vary. The invariant is that a milestone produces a scheduled in-fiction event whose attendance reflects each player's activity around its scheduled moment.

---

## 7. Game Names and identity

### 7.1 Game Name selection `ALD-012`
**Prerequisites:** ALD-044

Every Governor and every Player chooses a Game Name during onboarding.

#### Test
- **Type & Scope:** Integration; all platforms.
- **Purpose:** Verify the system requires and stores a Game Name at the moment of onboarding for both roles.
- **Preconditions:** A signed-in Google user invited to a new world.
- **Inputs:** Game Name "ThornKeeper".
- **Steps:** Complete onboarding through the Game Name step. Verify storage.
- **Expected Results:** Player record contains `game_name = "ThornKeeper"`. Onboarding cannot proceed past this step without one. Empty / whitespace-only Game Names are rejected.
- **Negative Cases:** Empty Game Name accepted → fail. Onboarding skips the step → fail.
- **Out of scope:** Profanity / abuse filtering policy is not defined in this PRD and is out of scope for this test. A separate policy and test will be added when the rules are decided.

### 7.2 Public identity privacy `ALD-013`
**Prerequisites:** ALD-012

Game Name is the public identity inside the world. Real names and email addresses are not shown to other players.

#### Test
- **Type & Scope:** Integration + security; all platforms.
- **Purpose:** Verify no view that one player can access displays another player's Google account name or email.
- **Preconditions:** A world with two players: Player A (Google name: "Alice Anderson", email: "alice@example.com", Game Name: "Stormcaller") and Player B.
- **Inputs:** Player B accesses every screen, API endpoint, and exported view that references other players.
- **Steps:** Enumerate views — player list, quest assignments, leaderboards, Gazette mentions, story scenes, comments, photo publish credits. Inspect raw API responses.
- **Expected Results:** Only "Stormcaller" appears. "Alice Anderson" and the email never appear.
- **Negative Cases:** Any leak of real name or email → fail. Including in HTTP headers, debug logs visible to the client, or error messages.

### 7.3 Game Name change with adaptive cost `ALD-014`
**Prerequisites:** ALD-004, ALD-012, ALD-020

A Game Name can be changed later for a cost. The AI sets the cost adaptively per player based on what is motivating to them (uses the motivator profile in ALD-020).

#### Test
- **Type & Scope:** AI-eval + integration; all platforms.
- **Purpose:** Verify a player can request a Game Name change, the AI proposes a cost tuned to the player, and on payment the name updates everywhere (except the world's DB name — see ALD-016).
- **Preconditions:** A world with one player ("Stormcaller", high Strength, low Gold, very active, motivator profile built up). Plus a second test player with a contrasting motivator profile.
- **Inputs:** Request to change Game Name to "Tempest" from each player.
- **Steps:** Submit request from each player. Capture each proposed cost. Compare. Pay. Verify update.
- **Expected Results:** A cost is proposed for each player. On payment, the player's Game Name updates everywhere in the player-facing world. The world's database name does not change. The costs differ between the two players based on their motivator profiles.
- **Negative Cases:** Free change → fail. Payment without name update → fail. DB name changes → fail (see ALD-016). Both players quoted the same cost → fail.
- **AI Evaluation Criteria:** Specific costs vary; the invariant is that each cost reflects an analysis of that player's motivators. Two contrasting profiles must produce two distinct, plausibly-motivating costs.

### 7.4 Cross-world Game Name independence `ALD-015`
**Prerequisites:** ALD-012

One real user (Google account) may have a different Game Name in each world they play in.

#### Test
- **Type & Scope:** Integration; backend.
- **Purpose:** Verify Game Names are per-world, not per-user.
- **Preconditions:** A single Google user joined to two worlds.
- **Inputs:** Pick Game Name "Ash" in World A and "Cinder" in World B.
- **Steps:** Verify both records exist independently and update independently.
- **Expected Results:** Each world stores its own Game Name. Changing one does not change the other.
- **Negative Cases:** Names sync across worlds → fail. One world clobbers the other → fail.

### 7.5 DB name locked at world creation `ALD-016`
**Prerequisites:** ALD-002

The world's database is named after the Governor's Game Name at the moment of world creation. Pattern: `{governor_game_name_at_creation}` for the first world, `{governor_game_name_at_creation}_2`, `_3`, etc. for additional worlds **by the same Governor**.

**Cross-Governor disambiguation:** If two different Governors choose the same Game Name (e.g. "Mara"), the second-and-later occurrences are suffixed with a short stable hash of the Governor's Google user ID (e.g. `mara`, `mara-7f3a`, `mara-9c21`). The first Governor to claim a name keeps the unsuffixed version. The DB name never changes once assigned.

#### Test
- **Type & Scope:** Integration; backend.
- **Purpose:** Verify DB naming rule, same-Governor incrementing, cross-Governor disambiguation, and immutability on rename.
- **Preconditions:** None.
- **Inputs:** Governor A signs up as "Mara". Creates World 1, then World 2. Renames to "Maris". Governor B (different Google account) signs up also as "Mara". Creates World 1.
- **Steps:** Inspect database server for DB names after each step.
- **Expected Results:** After Governor A's first creation, DB `mara` exists. After A's second creation, DB `mara_2` exists. After A renames to "Maris", both DBs are still `mara` and `mara_2`. After Governor B's creation, DB `mara-{hash}` exists (where `{hash}` is a short stable hash of B's Google user ID).
- **Negative Cases:** DB rename on Game Name change → fail. Wrong increment (e.g. `mara_1` instead of `mara`) → fail. Governor B's creation collides with Governor A's `mara` instead of getting a hash suffix → fail.

---

## 8. Players and the shared world

### 8.1 Shared story, individual perspective `ALD-017`
**Prerequisites:** ALD-003, ALD-030

All players in a world share the same evolving story but experience it from their own perspective.

#### Test
- **Type & Scope:** AI-eval; backend + web.
- **Purpose:** Verify two players in the same world see the same canonical events but framed for their own perspective.
- **Preconditions:** A world with two players who have both completed today's task. A shared event (a festival) is happening in the story.
- **Inputs:** Trigger Gazette generation for each player.
- **Steps:** Compare the two Gazettes.
- **Expected Results:** Both reference the same festival, on the same day, with consistent canonical facts (who hosted it, where it was, who else was there). The framing is personalized: each player's character is referenced as participating, with their actions noted.
- **Negative Cases:** Two contradictory descriptions of the festival → fail. One player's actions credited to the other → fail.
- **AI Evaluation Criteria:** Wording varies. Canonical facts (date, place, host, outcome) must match across the two outputs.

### 8.2 Shared images and text `ALD-018`
**Prerequisites:** ALD-030, ALD-042

If two players encounter the same scene, they see the same AI-generated image and same text. Generated assets are stored per-world for reuse.

#### Test
- **Type & Scope:** Integration; backend.
- **Purpose:** Verify generated assets are cached per-world and reused for the same scene.
- **Preconditions:** A world. A scene reference (e.g. "the Copper Kettle Tavern at sunset").
- **Inputs:** Player A views the scene. Player B views the same scene.
- **Steps:** Capture the image hash and text content delivered to each player.
- **Expected Results:** Image hash matches. Text content matches.
- **Negative Cases:** Different images / different text for the same scene → fail. Image regenerated on each view → fail (also a cost issue).

### 8.3 Per-player motivator profile `ALD-019`
**Prerequisites:** ALD-027

The AI builds and continuously refines a **motivator profile** for each player. The profile captures what styles of framing seem to motivate them most (e.g. stakes, humor, recognition, collaboration, competition, mastery). The profile is derived from how players respond to story content and how reliably they complete tasks framed in each style — not from explicit questionnaires.

The motivator profile is the input feature ALD-020 (per-player story tuning) uses, and feature ALD-014 (Game Name change cost) uses, to tune output per player.

#### Test
- **Type & Scope:** AI-eval + integration; backend.
- **Purpose:** Verify the system builds a motivator profile from player behavior and that the profile changes over time as new behavior signals come in.
- **Preconditions:** A new player with no history. The world has run for at least 7 days with simulated player behavior in which the player consistently completes humorous-framed quests and skips stakes-framed quests.
- **Inputs:** N/A (event-driven).
- **Steps:** Inspect the player's motivator profile after 7 days of simulated behavior. Switch behavior — simulate 7 more days of completing stakes-framed quests and skipping humorous ones. Inspect again.
- **Expected Results:** Profile after day 7 emphasizes humor-driven motivation. Profile after day 14 shifts toward stakes-driven. The profile is a structured record (not free-form text) that downstream features can read.
- **Negative Cases:** Profile remains empty or constant despite behavior → fail. Profile is unreadable / unstructured → fail.
- **AI Evaluation Criteria:** Exact representation may vary; profile must include named motivator dimensions with weights or scores that demonstrably move with behavior.

### 8.4 Per-player story tuning `ALD-020`
**Prerequisites:** ALD-019

Story content adjusts writing style per player to maximize motivation, using the motivator profile (ALD-019). The AI may use multiple in-fiction writers under Editor Maria, each tuned to a player.

#### Test
- **Type & Scope:** AI-eval; backend.
- **Purpose:** Verify the AI applies distinct writing styles per player, aligned with each player's motivator profile and attributed to in-fiction writers under Editor Maria.
- **Preconditions:** A world with two players. Player A has a stakes-dominant motivator profile (ALD-019). Player B has a humor-dominant motivator profile.
- **Inputs:** Same quest, both players.
- **Steps:** Generate each player's quest description.
- **Expected Results:** Both reference the same quest. Player A's version emphasizes urgency / consequence. Player B's version emphasizes lightness / humor. Each is bylined to a writer character under Editor Maria (or framed in a distinct writer's voice).
- **Negative Cases:** Identical text for both players → fail. Style mismatched to motivator profile → fail.
- **AI Evaluation Criteria:** A tester AI classifies each piece's tone and confirms it matches the target player's motivator profile.

### 8.5 Calendar awareness `ALD-021`
**Prerequisites:** ALD-002, ALD-030

The AI is calendar-aware — season, holiday, time-of-day shape the story based on each player's starting region.

#### Test
- **Type & Scope:** AI-eval; backend.
- **Purpose:** Verify generated content reflects real-world season, holiday, and time-of-day for the player's region.
- **Preconditions:** Two test players. Player A in US/Mountain in mid-December. Player B in Australia/Sydney in mid-December.
- **Inputs:** Trigger Gazette for each on the same real-world day.
- **Steps:** Read both. Look for seasonal and holiday cues.
- **Expected Results:** Player A's content references winter / holiday-season cues. Player B's content references summer. Real-world holidays in each region (Christmas, the southern summer) may appear in transformed form.
- **Negative Cases:** Both players get the same seasonal framing → fail. Northern-hemisphere winter applied to Australian player → fail.

### 8.6 Removed player retention `ALD-022`
**Prerequisites:** ALD-012

If a player is removed from a world, their character "leaves the kingdom" in fiction. The impact they had on the world remains.

#### Test
- **Type & Scope:** Integration + AI-eval; backend.
- **Purpose:** Verify a removed player's character is narratively retired and their prior contributions persist in the story state.
- **Preconditions:** A world where Player A has completed tasks that produced canonical story events (e.g. saved the princess) before being removed.
- **Inputs:** Governor removes Player A.
- **Steps:** Trigger next Gazette. Read it.
- **Expected Results:** Player A no longer appears in active quest assignments. The Gazette either does not mention them OR mentions them as having left. Prior story events involving Player A (the saved princess) are still referenced as historical facts.
- **Negative Cases:** Player A still receiving quests → fail. Prior events erased from history → fail. Player A's account still able to log into the world → fail.

---

## 9. Player characters

### 9.1 Character customization `ALD-023`
**Prerequisites:** ALD-012

Customize: gender (male or female), race, stats, name, look (via self-description).

#### Test
- **Type & Scope:** Integration; all platforms.
- **Purpose:** Verify all five fields are captured and stored at character creation.
- **Preconditions:** A new player who has signed in and chosen a Game Name.
- **Inputs:** gender="female", race="elf", stats="agility-focused", name="Lyra Brightwood", look="silver hair, tall, wears moss-green cloak".
- **Steps:** Submit character creation. Inspect stored character record.
- **Expected Results:** All five fields stored.
- **Negative Cases:** Gender accepting a value other than "male" or "female" → fail. Missing fields silently accepted → fail.

### 9.2 AI portrait generation `ALD-024`
**Prerequisites:** ALD-023, ALD-038

AI generates the character portrait from the self-description.

#### Test
- **Type & Scope:** AI-eval; backend.
- **Purpose:** Verify the portrait reflects the self-description.
- **Preconditions:** Character created with description "silver hair, tall, wears moss-green cloak".
- **Inputs:** The description above.
- **Steps:** Trigger portrait generation. View image.
- **Expected Results:** Image depicts a person with silver hair, tall stature, wearing a green cloak.
- **Negative Cases:** Image ignores description → fail. Image generation fails silently → fail.
- **AI Evaluation Criteria:** Tester AI uses vision to check for each described element. Hair and clothing color must match; stature is a soft check.

### 9.3 Appearance is cosmetic only `ALD-025`
**Prerequisites:** ALD-004, ALD-023

Appearance has no gameplay effect.

#### Test
- **Type & Scope:** Integration; backend.
- **Purpose:** Verify no reward, quest difficulty, or stat outcome differs based on character appearance.
- **Preconditions:** Two players with identical stats but different appearances.
- **Inputs:** Both complete the same quest.
- **Steps:** Compare reward outputs.
- **Expected Results:** Identical rewards. Identical quest text difficulty.
- **Negative Cases:** Any difference attributable to appearance → fail.

### 9.4 Image consistency across scenes `ALD-026`
**Prerequisites:** ALD-024

Character images are roughly consistent across scenes (comic-book-style, not pixel-perfect).

#### Test
- **Type & Scope:** AI-eval; backend.
- **Purpose:** Verify a character's defining features persist across multiple generated scene images.
- **Preconditions:** A character with a fixed description, used in 5 different scene contexts.
- **Inputs:** 5 scene prompts (tavern, forest path, palace hall, market, battle).
- **Steps:** Generate 5 images. Vision-evaluate each.
- **Expected Results:** In each image, the character has the same hair color, the same race / species cues, and the same signature clothing color or item. Pose, lighting, framing may vary.
- **Negative Cases:** Hair color changes → fail. Species changes → fail.
- **AI Evaluation Criteria:** Tester AI scores each image on three features (hair, race, signature clothing). 4 of 5 must match all three.

---

## 10. Player onboarding flow `ALD-027`
**Prerequisites:** ALD-012, ALD-023, ALD-035, ALD-044

1. Player receives an email invitation from a Governor.
2. Player signs in with Google.
3. Player is shown the world's content rating and must accept it. For R and NC-17, age confirmation is required.
4. Player chooses a Game Name.
5. Player is introduced to the world's lore.
6. Player reads the first Gazette.
7. Player creates their character.
8. Player begins.

### Test
- **Type & Scope:** End-to-end; all platforms.
- **Purpose:** Verify the full onboarding flow runs in the specified order and that each step blocks the next until complete.
- **Preconditions:** A world with a content rating of PG-13.
- **Inputs:** A test email address. Test Google account.
- **Steps:** Governor sends invitation. Recipient opens email, clicks link. Signs in with Google. Sees rating acceptance prompt. Accepts. Picks Game Name. Reads lore. Reads first Gazette. Creates character. Lands in the world's main view.
- **Expected Results:** Each step completes before the next is shown. The flow lands the player in the world ready to play.
- **Negative Cases:** Skipping rating acceptance → fail. Skipping Game Name → fail. Skipping character creation → fail. Repeat run with R-rated world without age confirmation succeeds → fail.

---

## 11. Children `ALD-028`
**Prerequisites:** ALD-044

- Under-13 children play alongside a parent on the parent's Google account.
- When a child turns 13 and gets their own Google account, they join the world as their own player.
- Whether a child has a separate sub-character on the parent's account is up to the parent / Governor.

### Test
- **Type & Scope:** Integration + policy; all platforms.
- **Purpose:** Verify there is no Aldermere-side mechanism for an under-13 to hold their own account, and that a 13+ user joining with their own Google account is treated as a full player.
- **Preconditions:** None.
- **Inputs:** Test Google account A (adult). Test Google account B (claims age 13+).
- **Steps:** Sign in with each. Attempt to create or join a world.
- **Expected Results:** Both succeed (Aldermere defers to Google's account-age policy). The system never asks a user to attest under-13 status. Adult-on-account workflows do not collect or store child PII.
- **Negative Cases:** Aldermere collects a child's name / DOB / email separately → fail. Account-creation flow asks "are you under 13?" → fail.

---

## 12. Outputs and content types `ALD-029`
**Prerequisites:** ALD-024, ALD-030

- **Newspaper-style** story digest (The Aldermere Gazette by default). Recurring section types include: top headlines, ongoing-story updates (e.g. the animal rights case), guild / faction announcements, public notices, restaurant or location spotlights, and an evening news wrap-up. The AI may add, retire, or rename sections per world flavor.
- **Quest descriptions** for each task.
- **Still images** for scenes, characters, items.
- **Story completion text** when tasks or arcs are completed.
- **No animation.** Ever.
- **No audio.** No music, no voiceover, no sound effects. Ever.

### Test
- **Type & Scope:** AI-eval + integration; all platforms.
- **Purpose:** Verify all four output types are produced and no animation exists anywhere in the product.
- **Preconditions:** An active world with at least one open quest and one completed quest.
- **Inputs:** N/A (snapshot of current state).
- **Steps:** Generate Gazette. Open quest list. Open character portrait. Complete a quest and read the completion text. Inspect all rendered media on web, iOS, Android.
- **Expected Results:** All four output types present and rendered. Every image asset is a still image (PNG / JPG / WebP). No video, no GIF, no Lottie, no canvas animations. No audio assets (MP3, WAV, OGG, M4A, etc.). The Gazette contains identifiable section types (headlines, faction announcements, public notices, etc.).
- **Negative Cases:** Animated GIF, MP4, Lottie file, or animation library shipped in the asset bundle → fail. Any audio asset present → fail. Gazette appears as a single undifferentiated block of text with no section types → fail.

---

## 13. Story regeneration

### 13.1 On-interaction generation `ALD-030`
**Prerequisites:** ALD-002, ALD-038

**Story-content generation** (new Gazettes, quest descriptions, scene images, story-completion text) fires only when a player interacts with the app, not on a fixed schedule.

**Notification composition** (the body of a story-flavored email or push) is a separate path: it may compose short in-fiction text at scheduled-cadence time without triggering full story-content regeneration. Notifications draw from already-generated quest descriptions and known story state; they may add a short framing sentence, but they must not advance the world's plot.

#### Test
- **Type & Scope:** Integration; backend.
- **Purpose:** Verify story-content generation is triggered by player action only, and that scheduled notifications do not advance the world's plot.
- **Preconditions:** A world with cadence-based notifications enabled but no active player interaction.
- **Inputs:** No player interaction for 7 days while scheduled notifications fire daily, then a player opens the app.
- **Steps:** Monitor server logs for generation events. Inspect what each scheduled notification contains. Open the app as a player. Re-monitor.
- **Expected Results:** Scheduled notifications fire daily but contain only references to existing state plus short framing — no new plot events, no new scenes, no Gazette advance. Zero story-content generation events during the silence. On player interaction, story-content generation fires.
- **Negative Cases:** Story plot advances in notifications during silence → fail. Story-content generation fires on a schedule → fail. App open with no generation → fail.

### 13.2 Compressed state input `ALD-031`
**Prerequisites:** ALD-030, ALD-033

The AI is given a compressed summary of prior story state plus relevant facts from the database. It does not re-read the full story every time.

#### Test
- **Type & Scope:** Integration; backend.
- **Purpose:** Verify the AI receives a compressed summary, not the raw story log, on each generation call.
- **Preconditions:** A world with at least 50,000 tokens of accumulated story.
- **Inputs:** Trigger a generation call. Capture the prompt sent to OpenAI.
- **Steps:** Compare the prompt to the raw story log.
- **Expected Results:** Prompt is substantially smaller than the raw log (target: under 25% of raw size for established worlds). The prompt contains a compressed summary plus relevant facts retrieved for this generation.
- **Negative Cases:** Full story log sent → fail (cost + context). No summary or no fact context → fail (continuity will drift).

### 13.3 50% context arc-close threshold `ALD-032`
**Prerequisites:** ALD-030

When the AI's context window reaches ~50% full during a story arc, the AI begins gracefully bringing the current arc to a close.

#### Test
- **Type & Scope:** AI-eval + integration; backend.
- **Purpose:** Verify arc-closure logic activates at the 50% context threshold.
- **Preconditions:** A world mid-arc whose generation context is approaching 50% full.
- **Inputs:** Drive generation until context crosses 50%. Capture next several generations.
- **Steps:** Inspect generated text for arc-closing language.
- **Expected Results:** Generations after crossing 50% begin wrapping the active arc (resolving plot threads, named characters reaching a destination, declared "festival concludes" markers). Within a bounded number of generations after crossing, the arc explicitly closes.
- **Negative Cases:** AI continues opening new plot threads after crossing 50% → fail. Hard cutoff with no closure → fail.
- **AI Evaluation Criteria:** A tester AI reads the generations and confirms a closure pattern. Specific resolution events may vary.

### 13.4 Compression after arc close `ALD-033`
**Prerequisites:** ALD-032

After an arc closes, compression of completed story segments is used to free context for the next arc.

#### Test
- **Type & Scope:** Integration; backend.
- **Purpose:** Verify completed arc content is compressed and stored, freeing context for the next arc.
- **Preconditions:** A world that just closed an arc.
- **Inputs:** N/A (event-driven).
- **Steps:** Inspect database before and after arc close. Check the compressed summary record.
- **Expected Results:** A new compressed summary record exists for the closed arc. Subsequent generations use the summary, not the raw text. Raw text remains in the DB as source of truth.
- **Negative Cases:** Raw arc content deleted → fail. No summary written → fail. Next arc generation references raw arc text → fail.

### 13.5 Database as fact source of truth `ALD-034`
**Prerequisites:** ALD-031

The full story is persisted in the world's database and is the source of truth for fact-checking.

#### Test
- **Type & Scope:** Integration + AI-eval; backend.
- **Purpose:** Verify the AI can be queried about prior story facts and answers consistently with the database.
- **Preconditions:** A world with rich story history. A specific known fact (e.g. "Sir Edrick won the arm-wrestling contest in Spring of Year 1").
- **Inputs:** Ask the AI "who won the arm-wrestling contest in Spring of Year 1?"
- **Steps:** Submit query. Compare answer to DB record.
- **Expected Results:** Answer matches DB. If compressed summary is ambiguous, the system queries the DB for clarification rather than hallucinating.
- **Negative Cases:** AI invents a different winner → fail. AI says "I don't know" when the fact is in the DB → fail.

### 13.6 Multi-scale story arcs `ALD-050`
**Prerequisites:** ALD-030, ALD-033

The story unfolds at multiple time scales simultaneously:
- **Daily** — the Gazette and the day's quests
- **Weekly** — short arcs (a few in-game days) tied to weekly-recurring tasks and short plotlines
- **Monthly** — medium arcs (multi-week plotlines, e.g. the animal rights labor case unfolding)
- **Annual** — recurring festivals and seasonal events (e.g. the Sheep Shearing Festival)

Arc scale is set by the AI based on the task list and the world's rhythm. Annual events anchor to real-world calendar dates per the world's region (see ALD-021).

#### Test
- **Type & Scope:** AI-eval + integration; backend.
- **Purpose:** Verify the AI maintains active arcs at multiple time scales simultaneously and references the right scale at the right moment.
- **Preconditions:** A world that has run for 14 in-game days, with a daily-recurring task, a weekly-recurring task, and an annual festival scheduled to occur during the test window.
- **Inputs:** N/A (snapshot of generated content over 14 days).
- **Steps:** For each of the 14 days, capture the Gazette and quest descriptions. Identify daily, weekly, monthly, and annual references across the corpus.
- **Expected Results:** Each day's Gazette references something daily, something weekly, and at least one piece of larger arc context (monthly or annual). The annual festival arrives on its scheduled in-game date and produces a multi-day event in the Gazette.
- **Negative Cases:** All references collapse to "today" with no weekly / monthly / annual layers → fail. Annual festival never arrives or arrives on the wrong date → fail.
- **AI Evaluation Criteria:** Tester AI classifies references in each day's output by time scale. At least 3 of the 14 days must show all four scales (or daily + weekly + monthly minimum if no annual event falls in that window).

---

## 14. Notifications

### 14.1 Email notifications (story-flavored, Governor cadence) `ALD-035`
**Prerequisites:** ALD-039

Story-flavored email to each player with their open tasks, on a cadence the Governor sets. Tone matches the world; the email reads like in-fiction correspondence, not a checklist. Email composition follows the notification-composition path described in ALD-030 — it does not advance the world's plot.

#### Test
- **Type & Scope:** Integration + AI-eval; backend.
- **Purpose:** Verify emails are sent on the right schedule, addressed to the right players, with story-flavored content matching the world's tone, and without advancing the world's plot.
- **Preconditions:** A world with two players and a daily email cadence.
- **Inputs:** Wait for the scheduled trigger. Capture sent emails.
- **Steps:** Inspect Resend delivery records and email bodies. Compare email contents to current world state.
- **Expected Results:** Both players receive an email. Each body references the player's open quests in in-fiction language (no bare checklist). Tone matches the world's rating and theme. Email content references only existing world state — no new plot events.
- **Negative Cases:** Plain-checklist email body → fail. Email sent to wrong player → fail. Email sent off-cadence → fail. Email introduces new plot events → fail.
- **AI Evaluation Criteria:** Tester AI checks body for in-fiction framing markers (character names, place names, narrative voice) and that no new named characters or events appear that are not already in world state.

### 14.2 Push notifications `ALD-036`
**Prerequisites:** ALD-035

Push notifications are delivered to the iOS and Android apps in addition to email.

#### Test
- **Type & Scope:** Integration; iOS + Android.
- **Purpose:** Verify push notifications fire on the same cadence as email and deliver to registered devices.
- **Preconditions:** A player with the iOS app installed and push permission granted, plus a player with the Android app and push granted.
- **Inputs:** Wait for cadence trigger.
- **Steps:** Inspect device-side push delivery.
- **Expected Results:** Both devices receive a push that mirrors the email's intent in shorter form.
- **Negative Cases:** Push not delivered → fail. Email without push → fail.

### 14.3 Unsubscribe / disable `ALD-037`
**Prerequisites:** ALD-035, ALD-036

Players may unsubscribe from email and/or disable push, while still able to use the app.

#### Test
- **Type & Scope:** Integration; all platforms.
- **Purpose:** Verify unsubscribe and push-off settings stick and the app remains usable.
- **Preconditions:** A player receiving both email and push.
- **Inputs:** Player unsubscribes from email. Player disables push. Cadence fires.
- **Steps:** Inspect Resend logs and device push state.
- **Expected Results:** No email sent. No push delivered. The player can still open the app and play normally.
- **Negative Cases:** Email or push still sent after unsubscribe → fail. App refuses to load after unsubscribe → fail.

---

## 15. Technical

### 15.1 OpenAI integration (text, image, vision) `ALD-038`
**Prerequisites:** none

OpenAI is the provider for story text, image generation, and vision-based photo evaluation.

#### Test
- **Type & Scope:** Integration; backend.
- **Purpose:** Verify all three OpenAI capability paths work end-to-end against the live API.
- **Preconditions:** OpenAI API key configured. Test prompt for each capability.
- **Inputs:** Text prompt, image prompt, image-to-eval.
- **Steps:** Make one call of each type. Capture responses.
- **Expected Results:** All three calls return successful responses with the expected output type.
- **Negative Cases:** Any 4xx / 5xx from OpenAI → fail. Response payload missing expected field → fail.

### 15.2 Resend integration `ALD-039`
**Prerequisites:** none

Resend is the email provider.

#### Test
- **Type & Scope:** Integration; backend.
- **Purpose:** Verify Resend can send a test email from the Aldermere sending identity and the message is delivered.
- **Preconditions:** Resend API key configured. Verified sending domain. Test recipient mailbox accessible.
- **Inputs:** Subject "Aldermere test", body "Hello from Aldermere."
- **Steps:** Send. Wait. Check recipient inbox and Resend delivery log.
- **Expected Results:** Resend logs success. Email arrives in recipient inbox within 60 seconds. Sender domain matches the verified identity.
- **Negative Cases:** Resend reports failure → fail. Email not delivered → fail. Sender domain shows as spoofed / unverified → fail.

### 15.3 Hetzner / Docker deployment `ALD-040`
**Prerequisites:** none

Backend runs in Docker on a Hetzner VPS.

#### Test
- **Type & Scope:** Infrastructure; backend.
- **Purpose:** Verify the backend image builds, deploys to the Hetzner VPS, and serves HTTPS traffic.
- **Preconditions:** Hetzner VPS provisioned. SSH access. Docker installed.
- **Inputs:** Backend Docker image, tagged.
- **Steps:** Build locally. Push image. Deploy. Curl the HTTPS endpoint.
- **Expected Results:** Image builds without warnings. Container runs without restart loop. HTTPS endpoint returns 200 on a health check. Certificate is valid.
- **Negative Cases:** Build fails → fail. Container exits → fail. HTTPS not enforced → fail.

### 15.4 Per-world database isolation `ALD-041`
**Prerequisites:** ALD-016, ALD-040

One database per world, per the naming rule in ALD-016.

#### Test
- **Type & Scope:** Integration + security; backend.
- **Purpose:** Verify no query for World A can return rows from World B.
- **Preconditions:** Two worlds. Player in World A. Player in World B.
- **Inputs:** Player A's session attempts to query and join across DB boundaries.
- **Steps:** Issue API calls as Player A that try to fetch player lists, story content, photos for any world other than A.
- **Expected Results:** All such calls return 403 or 404. No row from World B is returned through any endpoint.
- **Negative Cases:** Any row from another world returned → fail. Any error message that leaks the existence of other worlds' DB names → fail.

### 15.5 Object storage for assets `ALD-042`
**Prerequisites:** ALD-040

Photos and generated images live in object storage (Hetzner Storage Box or S3-compatible).

#### Test
- **Type & Scope:** Integration; backend.
- **Purpose:** Verify uploads land in object storage, are served via authenticated URLs, and are scoped to a world.
- **Preconditions:** Object storage bucket configured.
- **Inputs:** Upload a test photo.
- **Steps:** Upload. Retrieve. Attempt cross-world retrieval.
- **Expected Results:** Upload succeeds. Retrieval works for an authorized player in the same world. Cross-world retrieval is rejected.
- **Negative Cases:** Public unauthenticated URL → fail. Cross-world access succeeds → fail.

### 15.6 Single codebase ships three platforms `ALD-043`
**Prerequisites:** none

The codebase produces a web build, an iOS build, and an Android build.

#### Test
- **Type & Scope:** Build / CI.
- **Purpose:** Verify a single `build` command (or three parallel ones) produces shippable artifacts for all three platforms from one source tree.
- **Preconditions:** Codebase scaffolded. Build tooling installed.
- **Inputs:** N/A.
- **Steps:** Run web build. Run iOS build (via Expo). Run Android build (via Expo).
- **Expected Results:** All three builds succeed. Web bundle exists. iOS `.ipa` or simulator binary exists. Android `.aab` or APK exists.
- **Negative Cases:** Any build fails → fail. Platform-specific code paths that are not shared → flag for review.

### 15.7 Google Sign-In `ALD-044`
**Prerequisites:** ALD-043

Google Sign-In is the only authentication method.

#### Test
- **Type & Scope:** Integration; all platforms.
- **Purpose:** Verify Google Sign-In works on web, iOS, and Android, and that no other auth method is exposed.
- **Preconditions:** Google OAuth client IDs configured per platform.
- **Inputs:** A test Google account.
- **Steps:** Open the sign-in screen on each platform. Complete the Google flow. Verify session.
- **Expected Results:** Sign-in succeeds on all three. Session token is created. No email/password, magic link, or other auth path is visible in the UI or API.
- **Negative Cases:** Any alternative auth path present → fail. Sign-in fails on any platform → fail.

---

## 16. World lifecycle `ALD-045`
**Prerequisites:** ALD-002, ALD-041

A world exists as long as the Governor keeps it active. If a Governor abandons or cancels, the world is archived (not deleted). Archived worlds are kept forever for now.

### Test
- **Type & Scope:** Integration; backend.
- **Purpose:** Verify archive on cancel, no data loss, and resume from archive.
- **Preconditions:** An active world with story state, players, photos.
- **Inputs:** Governor cancels the world. Later, Governor resumes it.
- **Steps:** Cancel. Inspect DB and storage. Resume. Verify state.
- **Expected Results:** Cancel marks world as archived; data remains intact (DB, photos, story). Players are notified the world is paused. Resume restores active state with all history.
- **Negative Cases:** Any data deleted on cancel → fail. Resume returns a fresh world → fail.

---

## 17. Business model

Free to start. No cost ceilings or quotas at launch. Paid subscription to follow once people are actively using it.

*No test at this stage — no constraints to verify.*

---

## 18. What it will NOT do

### 18.1 No animation, no audio
Already covered by ALD-029 test. No additional test required. Aldermere is text + still images only — no animation, no music, no voiceover, no sound effects.

### 18.2 No real-money trading `ALD-046`
**Prerequisites:** ALD-043

#### Test
- **Type & Scope:** Integration + security; all platforms.
- **Purpose:** Verify no in-app or API mechanism allows players to exchange real money for in-game items or to each other.
- **Preconditions:** A world with two players.
- **Inputs:** Attempt to find any UI element or API endpoint that transfers value between players or accepts payment for in-game items.
- **Steps:** UI walkthrough. API enumeration.
- **Expected Results:** No such endpoint exists. No such UI element exists.
- **Negative Cases:** Any payment-to-player or in-game-purchase endpoint present → fail.

### 18.3 No content beyond the chosen rating `ALD-047`
**Prerequisites:** ALD-002, ALD-030

#### Test
- **Type & Scope:** AI-eval; backend.
- **Purpose:** Verify generated content respects the world's content rating.
- **Preconditions:** Four worlds at G, PG, PG-13, R. (NC-17 omitted from this test; can be added separately.)
- **Inputs:** Trigger 20 generations per world covering Gazettes, quests, and story scenes.
- **Steps:** Capture all output. Classify each piece against standard rating taxonomies.
- **Expected Results:** No output exceeds the world's rating.
- **Negative Cases:** Any output exceeding rating → fail. AI refuses to generate appropriate-rating content → also fail (under-restriction).
- **AI Evaluation Criteria:** Tester AI classifies each output and flags any over-rating. Sample size of 20 per world should reliably surface drift.

### 18.4 No punitive mechanics
Covered by ALD-009 test.

### 18.5 No gameplay effect from character appearance
Covered by ALD-025 test.

### 18.6 No cross-world player interaction `ALD-048`
**Prerequisites:** ALD-041

#### Test
- **Type & Scope:** Integration; all platforms.
- **Purpose:** Verify no UI surface allows a player in one world to see, message, or interact with a player in another world.
- **Preconditions:** Two worlds. The same Google account is a player in both.
- **Inputs:** Sign in. Switch worlds. Look for any cross-reference.
- **Steps:** Enumerate all screens for any mention of "other worlds you're in" beyond the world picker, and any messaging surface.
- **Expected Results:** The world picker is the only place that lists other worlds. No messaging, no leaderboards, no shared events.
- **Negative Cases:** Any cross-world social surface → fail.

---

## 19. Launch scope

Full feature scope ships at first release: all features above are built into the single codebase, producing web + iOS + Android. The **public web app launches first** at `aldermere.world`. The **iOS and Android binaries are built and ready** but distribution to the Apple App Store and Google Play happens once the developer accounts are set up — these are deferred per John.

## 20. Setup checklist

| Item | Status | Notes |
|---|---|---|
| OpenAI API access + billing | ✅ ready | |
| Hetzner VPS | ✅ ready | Details pending from John |
| Resend account (email) | ⏳ needed | Will set up |
| `aldermere.world` domain | ✅ registered (Namecheap) | |
| Public GitHub repo `johnjhusband/aldermere` | ✅ created | https://github.com/johnjhusband/aldermere |
| Apple Developer Program ($99/yr) | ⏸ deferred | Required to distribute iOS app via App Store |
| Google Play Console ($25 one-time) | ⏸ deferred | Required to distribute Android app via Play |
| Privacy policy + Terms of Service | ⏳ needed | Publishing entity: **Husband, LLC**; contact: `john@husband.llc` |
| `TESTING.md` (cleanup + reporting + runner) | ⏳ needed | To be written when codebase is scaffolded |

## 21. Open questions

Tracked in chat with John — see follow-up.

---

## Appendix A — Control ID index

| ID | Feature | Section | Prerequisites |
|---|---|---|---|
| ALD-001 | Canonical world content | §4 | ALD-002 |
| ALD-002 | Governor setup interview | §5 | ALD-038, ALD-044 |
| ALD-003 | Task → quest conversion | §6.1 | ALD-001, ALD-002 |
| ALD-004 | Base rewards | §6.2 | ALD-003 |
| ALD-005 | Photo evaluation and visibility | §6.3 | ALD-004, ALD-042 |
| ALD-006 | Reward unlocks | §6.4 | ALD-004, ALD-024 |
| ALD-007 | Player-proposed tasks | §6.5 | ALD-003, ALD-004 |
| ALD-008 | Long-task decomposition encouragement | §6.6 | ALD-002 |
| ALD-009 | Skipping and narrative consequences | §6.7 | ALD-003, ALD-030 |
| ALD-010 | Cross-region travel costs | §6.8 | ALD-002, ALD-004 |
| ALD-011 | No end | §6.9 | ALD-033 |
| ALD-012 | Game Name selection | §7.1 | ALD-044 |
| ALD-013 | Public identity privacy | §7.2 | ALD-012 |
| ALD-014 | Game Name change with adaptive cost | §7.3 | ALD-004, ALD-012, ALD-020 |
| ALD-015 | Cross-world Game Name independence | §7.4 | ALD-012 |
| ALD-016 | DB name locked at world creation | §7.5 | ALD-002 |
| ALD-017 | Shared story, individual perspective | §8.1 | ALD-003, ALD-030 |
| ALD-018 | Shared images and text | §8.2 | ALD-030, ALD-042 |
| ALD-019 | Per-player motivator profile | §8.3 | ALD-027 |
| ALD-020 | Per-player story tuning | §8.4 | ALD-019 |
| ALD-021 | Calendar awareness | §8.5 | ALD-002, ALD-030 |
| ALD-022 | Removed player retention | §8.6 | ALD-012 |
| ALD-023 | Character customization | §9.1 | ALD-012 |
| ALD-024 | AI portrait generation | §9.2 | ALD-023, ALD-038 |
| ALD-025 | Appearance is cosmetic only | §9.3 | ALD-004, ALD-023 |
| ALD-026 | Image consistency across scenes | §9.4 | ALD-024 |
| ALD-027 | Player onboarding flow | §10 | ALD-012, ALD-023, ALD-035, ALD-044 |
| ALD-028 | Children policy | §11 | ALD-044 |
| ALD-029 | Outputs and content types | §12 | ALD-024, ALD-030 |
| ALD-030 | On-interaction generation | §13.1 | ALD-002, ALD-038 |
| ALD-031 | Compressed state input | §13.2 | ALD-030, ALD-033 |
| ALD-032 | 50% context arc-close threshold | §13.3 | ALD-030 |
| ALD-033 | Compression after arc close | §13.4 | ALD-032 |
| ALD-034 | DB as fact source of truth | §13.5 | ALD-031 |
| ALD-035 | Email notifications | §14.1 | ALD-039 |
| ALD-036 | Push notifications | §14.2 | ALD-035 |
| ALD-037 | Unsubscribe / disable | §14.3 | ALD-035, ALD-036 |
| ALD-038 | OpenAI integration | §15.1 | — |
| ALD-039 | Resend integration | §15.2 | — |
| ALD-040 | Hetzner / Docker deployment | §15.3 | — |
| ALD-041 | Per-world database isolation | §15.4 | ALD-016, ALD-040 |
| ALD-042 | Object storage for assets | §15.5 | ALD-040 |
| ALD-043 | Single codebase ships three platforms | §15.6 | — |
| ALD-044 | Google Sign-In | §15.7 | ALD-043 |
| ALD-045 | World lifecycle | §16 | ALD-002, ALD-041 |
| ALD-046 | No real-money trading | §18.2 | ALD-043 |
| ALD-047 | No content beyond chosen rating | §18.3 | ALD-002, ALD-030 |
| ALD-048 | No cross-world player interaction | §18.6 | ALD-041 |
| ALD-049 | Milestone events as rewards | §6.10 | ALD-004, ALD-030 |
| ALD-050 | Multi-scale story arcs | §13.6 | ALD-030, ALD-033 |
