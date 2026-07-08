# Dekho — Analytics \& PMF System: Build Spec for Antigravity

**Purpose of this document:** This is an execution-ready prompt/spec to hand to Antigravity to implement the analytics and PMF measurement system designed in `Dekho\_Analytics\_PMF\_Design.md`. It translates that strategic design into concrete build tasks: exact packages, file locations, event names, schema, and SQL.

**How to use this doc:** Paste the relevant "Task" section directly into Antigravity as a prompt. Each task is scoped to be independently buildable and testable. Do not hand Antigravity the whole document at once — feed it task by task, verify output, then move to the next.

**Flagged upfront — things I cannot verify from here and Antigravity/you must confirm before executing:**

* Exact table and column names in your Neon Postgres schema (I'm using best-guess names based on the product docs — e.g., `transactions`, `budgets`, `goals` — verify these against the actual schema before running any SQL below).
* Whether a merchant-memory or recurring-expense table already exists in the chatbot's preference store, or whether it needs to be created.
* Current PostHog account status (whether a project already exists or needs creation).

Do not let Antigravity guess-fill these — have it inspect the actual schema first (`\\d transactions` or equivalent) and adjust column names before running DDL/views.

\---

## TASK 0 — Pre-flight schema audit (run this first, always)

**Prompt for Antigravity:**

> Connect to the Neon Postgres database used by the Dekho main app. Run `\\dt` to list all tables, then `\\d <table>` for `transactions`, `budgets`, `goals`, `users`. Also connect to the chatbot's database (Postgres, since live DB integration is confirmed complete) and list tables including `user\_preferences`, `conversations`, `feedback`. Output the actual column names and types for each. Do not modify anything — this is read-only reconnaissance. Report back the schema before any further task proceeds.

**Why this matters:** Every SQL view in Task 3 below is written against assumed column names. If Antigravity writes views against wrong column names, they'll fail loudly (good) or silently reference the wrong data (bad, and harder to catch). Confirm schema first.

\---

## TASK 1 — PostHog integration (main app, Next.js)

**Scope:** Install PostHog, wire up identify + the minimal event taxonomy from the design doc. Nothing more — do not enable autocapture beyond default page views.

**Prompt for Antigravity:**

> In the Dekho main app (Next.js on Vercel), install `posthog-js`. Create a PostHog client provider that initializes once at app root, using `NEXT\_PUBLIC\_POSTHOG\_KEY` and `NEXT\_PUBLIC\_POSTHOG\_HOST` environment variables (values to be supplied separately — do not hardcode or invent a key).
>
> Requirements:
> 1. Call `posthog.identify(user\_id)` immediately after auth resolves on \*\*every app load\*\*, not only first signup — this is critical for iOS Safari, where storage behavior can otherwise fragment returning users into apparent "new" sessions.
> 2. Set a `display\_mode` person property to `"standalone"` or `"browser"` based on `window.matchMedia('(display-mode: standalone)').matches`, captured on every session start. This lets us later segment iOS PWA installed-app users from browser-tab users.
> 3. Set `platform` property (`ios` / `android` / `desktop`) using UA detection or existing device-detection logic if the app already has it.
> 4. Implement the following events, firing exactly at the described trigger point, with exactly these names (do not rename or add extra events without checking back — event-name discipline matters for later analysis):

|Event name|Trigger|Properties|
|-|-|-|
|`signup\_completed`|Account creation success|`platform`, `source` (from signup form's existing source field)|
|`first\_transaction\_logged`|User's first-ever transaction saved (check if this is their 1st, not just any transaction)|`platform`|
|`first\_budget\_created`|User's first-ever budget saved|`platform`|
|`dashboard\_viewed`|Home screen mounted|`platform`, `display\_mode`|
|`daily\_reflection\_viewed`|Reflection card rendered and visible (not just mounted — use an intersection observer or equivalent visibility check if easy; if not feasible for v1, mount-based firing is acceptable, flag this limitation in code comments)|`platform`|
|`streak\_checkin`|Daily check-in action completed|`platform`|
|`safe\_budgets\_viewed`|Budget summary section opened|`platform`|
|`chatbot\_opened`|Ask Dekho chat screen opened|`platform`|
|`chatbot\_message\_sent`|User sends a message to Ask Dekho|`platform`, `intent` (populate from the chatbot API response's intent field once returned — if the response is streamed, capture this from the `intent` SSE event)|
|`chatbot\_feedback\_given`|Thumbs up/down tapped|`platform`, `rating`, `intent`|

> 5. Do not add session recording (`posthog.startSessionRecording()`) yet — this is a deliberate scope limit for v1, not an oversight. Confirm with the founder before enabling replay, since replay behavior differs meaningfully between installed-PWA and browser-tab contexts on iOS and needs a separate validation pass.

**Acceptance test:** After implementation, manually trigger each event in a dev environment and confirm it appears in the PostHog "Activity" live event stream with the correct properties attached, on both an Android device/emulator and an iOS device (not just desktop Chrome — iOS Safari behaves differently and must be tested directly).

\---

## TASK 2 — Correction logging (main app + chatbot, if not already present)

**Scope:** The Layer 2 metrics (categorization accuracy, correction rate) depend on the app actually recording when a user corrects an auto-assigned category. Per Task 0's schema audit, confirm whether this is already captured. If it is not, this task adds it.

**Prompt for Antigravity:**

> After the schema audit from Task 0, check whether the `transactions` table has both an `auto\_category` (system-assigned) and `user\_corrected\_category` (nullable, populated only if the user changes it) column, or equivalent. If this distinction doesn't exist yet — e.g., there's only a single `category` field that gets overwritten on correction — this is a real gap: we cannot compute categorization accuracy without knowing what the system \*originally\* guessed versus what the user \*changed it to\*.
>
> If the gap exists, add:
> ```sql
> ALTER TABLE transactions
>   ADD COLUMN auto\_category TEXT,
>   ADD COLUMN was\_corrected BOOLEAN DEFAULT FALSE,
>   ADD COLUMN corrected\_at TIMESTAMPTZ;
> ```
> On the category-edit code path (wherever the UI currently updates `category`), preserve the original ML-assigned value into `auto\_category` at write-time (if not already stored), and set `was\_corrected = true` + `corrected\_at = now()` whenever a user manually changes it after the fact.
>
> Do not backfill historical data with guessed values — if `auto\_category` wasn't captured historically, leave it null for old rows rather than fabricating it. Flag in your output how many existing rows lack this data, so we know the accuracy metric's usable history starts from deployment date, not from app launch.

**This is flagged as uncertain** because I don't know your current schema. If the audit shows this already exists, skip this task entirely — don't let Antigravity "improve" a working schema unnecessarily.

\---

## TASK 3 — SQL views for Layer 2 PMF metrics

**Scope:** Read-only SQL views against the (now-confirmed) schema. Run against Neon Postgres. These are drafted against **assumed** column names — Antigravity must adjust to match Task 0's actual output before running.

**Prompt for Antigravity:**

> Using the confirmed schema from Task 0, create the following SQL views in Neon Postgres. Adjust column/table names to match reality — do not run these verbatim if they don't match the audited schema.
>
> \*\*View 1 — Categorization accuracy by user, rolling 30 days:\*\*
> ```sql
> CREATE OR REPLACE VIEW v\_categorization\_accuracy AS
> SELECT
>   user\_id,
>   COUNT(\*) AS total\_transactions,
>   SUM(CASE WHEN was\_corrected THEN 1 ELSE 0 END) AS corrected\_count,
>   ROUND(
>     1.0 - (SUM(CASE WHEN was\_corrected THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(\*), 0)),
>     3
>   ) AS accuracy\_rate
> FROM transactions
> WHERE created\_at >= now() - interval '30 days'
> GROUP BY user\_id;
> ```
>
> \*\*View 2 — Weekly correction rate trend:\*\*
> ```sql
> CREATE OR REPLACE VIEW v\_correction\_rate\_weekly AS
> SELECT
>   user\_id,
>   date\_trunc('week', created\_at) AS week,
>   COUNT(\*) AS total\_transactions,
>   SUM(CASE WHEN was\_corrected THEN 1 ELSE 0 END) AS corrections
> FROM transactions
> GROUP BY user\_id, date\_trunc('week', created\_at)
> ORDER BY user\_id, week;
> ```
>
> \*\*View 3 — Personalization Depth Score (v1, binary-weighted per design doc Section 4.1):\*\*
> ```sql
> CREATE OR REPLACE VIEW v\_personalization\_depth AS
> SELECT
>   user\_id,
>   (
>     (CASE WHEN response\_style IS NOT NULL THEN 1 ELSE 0 END) +
>     (CASE WHEN top\_interests IS NOT NULL AND jsonb\_array\_length(top\_interests) > 0 THEN 1 ELSE 0 END) +
>     (CASE WHEN corrections IS NOT NULL AND jsonb\_array\_length(corrections) > 0 THEN 1 ELSE 0 END) +
>     (CASE WHEN recurring\_merchant\_learned IS NOT NULL THEN 1 ELSE 0 END) +
>     (CASE WHEN salary\_detected IS NOT NULL THEN 1 ELSE 0 END)
>   ) \* 20 AS depth\_score
> FROM user\_preferences;
> ```
> \*\*Note:\*\* `recurring\_merchant\_learned` and `salary\_detected` are assumed columns based on the product doc's description of the preference-learning system. If these don't exist as distinct fields in `user\_preferences`, flag this back rather than inventing a proxy — we need to know if this signal is actually being captured anywhere before scoring against it.
>
> \*\*View 4 — Chatbot reuse (sessions per user per week):\*\*
> ```sql
> CREATE OR REPLACE VIEW v\_chatbot\_reuse\_weekly AS
> SELECT
>   user\_id,
>   date\_trunc('week', timestamp) AS week,
>   COUNT(DISTINCT session\_id) AS sessions
> FROM conversations
> GROUP BY user\_id, date\_trunc('week', timestamp)
> ORDER BY user\_id, week;
> ```
>
> Test each view returns rows without error after creation, and sanity-check row counts against known pilot user count (should not wildly exceed expected transaction/message volume — if it does, investigate before trusting the view).

\---

## TASK 4 — Metabase deployment (Railway)

**Prompt for Antigravity:**

> Deploy Metabase (open-source, official Docker image `metabase/metabase`) as a new service on Railway, in the same project as the existing backends. Connect it to the Neon Postgres instance using a \*\*read-only\*\* database user if one doesn't already exist — do not connect Metabase using the app's primary read-write credentials. If a read-only role doesn't exist, create one:
> ```sql
> CREATE ROLE metabase\_readonly WITH LOGIN PASSWORD '<generate securely, do not hardcode>';
> GRANT CONNECT ON DATABASE <dbname> TO metabase\_readonly;
> GRANT USAGE ON SCHEMA public TO metabase\_readonly;
> GRANT SELECT ON ALL TABLES IN SCHEMA public TO metabase\_readonly;
> ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO metabase\_readonly;
> ```
> Once deployed, build 4 dashboard cards pointing at the views from Task 3: categorization accuracy distribution, correction rate trend (line chart over weeks), personalization depth score distribution (histogram), chatbot reuse (weekly active chatters).
>
> Confirm Metabase is behind authentication (its own login, not publicly exposed) before considering this task complete — do not leave an analytics dashboard containing real user financial behavior data on an unauthenticated public URL.

\---

## TASK 5 — Explicit non-goals (do not let Antigravity scope-creep into these)

State this directly in the prompt context if Antigravity suggests any of the following — they are deliberately out of scope for this build pass:

* **Do not** build Monthly Wrap. It doesn't exist yet and is not part of this analytics task — flagged separately as a product gap, not something to bootstrap as a side effect of instrumentation work.
* **Do not** touch `ADD\_TRANSACTION` write-back logic in the chatbot. Unrelated to this task, and already a known deferred item.
* **Do not** enable PostHog session replay in this pass.
* **Do not** enable AUTH\_ENABLED as part of this work — that's a separate, higher-stakes task with its own review needed.
* **Do not** backfill or fabricate historical `auto\_category` data to make the accuracy metric look complete from day one.

\---

## Acceptance Checklist (run through before calling this "done")

* \[ ] Schema audit completed and all assumed column names corrected to match reality
* \[ ] PostHog events firing correctly on both Android and iOS test devices, with `identify()` confirmed working across repeat sessions (not just first load)
* \[ ] `was\_corrected` / `auto\_category` fields confirmed present or added, with historical-data gap documented
* \[ ] All 4 SQL views created, tested, and returning sane row counts
* \[ ] Metabase deployed on Railway, connected via read-only credentials, behind authentication
* \[ ] 4 dashboard cards built and manually verified against at least one known test user's real data

\---

*This spec should be fed to Antigravity task-by-task, not as one prompt. Verify each task's output against the acceptance checklist before proceeding to the next.*

