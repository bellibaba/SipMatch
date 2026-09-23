# SipMatch

SipMatch is a demo-ready drink recommendation platform for adults who enjoy social drinking but do not yet have a working vocabulary for wine, beer, or spirits. It converts familiar taste preferences into ranked recommendations, explains each match in plain language, suggests food pairings, and teaches foundational terminology through a short interactive quiz.

The prototype was built for a classroom presentation. It prioritizes a reliable end-to-end story over production-scale architecture: create an account, describe your taste, view ranked drinks, upload a shelf photo or search manually, understand pairings, log a rating, and see that rating in your profile.

## Quick start with Docker

Prerequisite: Docker Desktop (or Docker Engine with the Compose plugin).

```bash
docker compose up --build
```

Then open [http://localhost:5050](http://localhost:5050), create an account, and complete the short taste profile. MySQL initializes the catalogue automatically on the first run. Set `SIPMATCH_PORT` before the command if you prefer a different host port.

To stop the app:

```bash
docker compose down
```

To discard the local database and restart with the seed catalogue:

```bash
docker compose down -v
docker compose up --build
```

## Suggested presentation flow

1. Create an account and choose a sweet, fresh, light profile.
2. Point out that the Discover page ranks Riesling/cider-style options from those answers.
3. Search for `citrus`, `beer`, or `Riesling` to demonstrate manual fallback.
4. Open an image with clear label text and use **Read labels** to demonstrate local OCR.
5. Explain the pairing reasons and save a half-star rating.
6. Show the saved rating and preferences on Profile.
7. Complete one Taste Lab question and ask Sip, “What pairs with spicy food?”

## Architecture and file structure

```text
sipmatch/
├── app.py                    Flask routes, authentication, OCR, recommendations, ratings, and chatbot logic
├── schema.sql                MySQL schema plus seeded drinks, snacks, and pairing reasons
├── requirements.txt          Fully pinned Python runtime dependencies
├── Dockerfile                Python/Tesseract application image
├── docker-compose.yml        One-command Flask + MySQL development stack
├── .dockerignore             Files excluded from the container build context
├── .gitignore                Local Python, environment, and OS files excluded from Git
├── static/
│   ├── css/styles.css        Responsive brown/black/cream visual system and glassmorphism cards
│   └── js/main.js            Mobile navigation, quiz behavior, chat prompt chips, and feedback animation
└── templates/
    ├── base.html             Shared navigation, flash feedback, footer, and asset loading
    ├── index.html            Landing page, product explanation, and featured drinks
    ├── signup.html           Account registration form
    ├── login.html            Session login form
    ├── onboarding.html       Taste-preference and past-purchase capture
    ├── drinks.html           OCR upload, manual search, drink carousel, pairings, and rating controls
    ├── profile.html          Editable user details, preference summary, and rating history
    ├── glossary.html         Interactive five-question terminology quiz
    ├── chat.html             Rule-based Q&A and natural-language suggestion interface
    └── error.html            Friendly 404 and upload-size error state
```

## Dependencies

Application dependencies are pinned in `requirements.txt`:

- **Flask 3.1.2** — routing, server-rendered templates, signed sessions, and request handling.
- **mysql-connector-python 9.4.0** — direct MySQL queries without an additional ORM layer.
- **Pillow 11.3.0** — validates and decodes uploaded JPG/PNG images.
- **pytesseract 0.3.13** — Python adapter for local label-text recognition.
- **gunicorn 23.0.0** — production-style WSGI process used by the application container.

Container/runtime dependencies:

- **Python 3.12 slim** — compact application runtime.
- **Tesseract OCR** — performs image recognition locally; no API key or network call is required.
- **MySQL 8.4** — persistent relational store for users, drinks, snacks, pairings, ratings, and preferences.

No JavaScript packages or remote frontend libraries are required.

## Data model

- `users`: account name, unique email, securely hashed password, and creation date.
- `drinks`: catalogue metadata, taste dimensions, aggregate 1–5 rating, and rating count.
- `snacks`: reusable foods with short descriptions.
- `pairings`: drink-to-snack relationships and a plain-language reason.
- `ratings`: one self-reported half-star rating per user and drink; no purchase transaction is implied.
- `user_preferences`: sweetness, acidity, strength, preferred drink type, and self-reported past purchases.

## Recommendation approach

Recommendations use transparent weighted similarity rather than machine learning. Each drink receives:

- its community aggregate rating;
- up to 2.4 points for each matching sweetness, acidity, and strength dimension (partial credit for an adjacent level); and
- a 2.5-point boost when the preferred drink family matches.

This deterministic method is easy to explain during a presentation and immediately reflects profile edits. User ratings are stored for history and update the aggregate catalogue score, which feeds subsequent ranking.

## Assumptions and prototype decisions

- **Stack:** Flask with server-rendered Jinja templates was selected to keep the one-day implementation compact and demoable.
- **OCR:** Tesseract performs local OCR. Matches use recognizable words from OCR output against drink name, type, and flavor profile. Manual search is always visible because crowded shelves, glare, and stylized labels can reduce confidence.
- **Image handling:** uploaded images are read in memory and are not retained.
- **Chatbot:** Ask Sip is deliberately rule-based, requires no API key, and covers common terms, styles, and pairing questions.
- **Ratings:** the UI and database use a consistent 1–5 scale in 0.5 increments. Seed aggregate ratings make the catalogue useful before classmates add ratings.
- **Past purchases:** users self-report prior purchases as free text; the prototype preserves them on the profile and does not represent them as in-app transactions.
- **Lathena:** CSS requests a locally installed `Lathena` font for display text and falls back to Georgia. The licensed font file is not redistributed; body copy uses the system sans-serif stack for readability.
- **Responsible use:** the interface is intended only for adults of legal drinking age and displays a responsible-use notice.

## Known limitations

- OCR quality depends on lighting, image sharpness, label angle, and whether the exact drink exists in the small seeded catalogue.
- The seed catalogue contains ten representative drinks rather than a commercial-scale inventory.
- The chatbot is keyword/rule based and does not maintain conversation history or call an LLM.
- Recommendation scoring does not yet learn individual flavor weights from rating patterns; ratings influence the aggregate component only.
- Authentication has no email verification, password reset, CSRF tokens, rate limiting, or account lockout. The development secrets in `docker-compose.yml` must be replaced before any real deployment.
- Database queries use one short-lived connection per operation; a production version should use pooling and migrations.
- Images are not stored, and OCR results are not persisted.
- The prototype does not verify legal drinking age or provide health, medical, or safety advice.
- The Lathena font is used only when installed locally because its licensed asset is not included.

## Initial prompt

The first instruction supplied for this prototype was:

```text
System Prompt

You are a Software Developer with knowledge of all tech stacks. You are tasked with creating a prototype for this project to be presented tomorrow in class. You need to make sure that the deliverables as mentioned in the document is achieved successfully.

User Prompt
```

The referenced group deliverable described **SipMatch** as a guided recommendation app for casual drinkers who feel overwhelmed at the “wall of bottles.” It called for mood, occasion, taste, and food inputs; bottle/photo recognition; understandable confidence and educational layers; profiles, recommendations, and ratings; and validation of guided behavior, community interest, recommendation accuracy, pricing, and onboarding value.

## Full implementation prompt

The following prompt is preserved as project provenance. It is documentation, not runtime configuration.

```text
SYSTEM PROMPT

You are a full-stack software developer building a working prototype for a class presentation due tomorrow. Prioritize a functional, demoable product over exhaustive polish. Where a requirement is ambiguous, make a reasonable assumption, implement it, and note the assumption in the README rather than stopping to ask.



USER PROMPT



Build a web application called SipMatch, a recommendation platform that helps new drinkers choose alcoholic beverages and food pairings based on their taste preferences, and learn basic terminology along the way.

SCOPE & CONSTRAINTS

1. Confine all code, assets, and file operations to a single project directory: [sipmatch](sipmatch/) . Do not read or write outside it.
2. Provide a Docker Compose setup that starts the full stack (app + MySQL) with one command. Include a requirements.txt (Python) or package.json (Node) pinning all dependencies.
3. Follow standard code style for the chosen language/framework (e.g. PEP8 for Python, ESLint defaults for JS). Comment non-obvious logic, not every line.
4. Write a README.md covering: project purpose, setup instructions, folder/file structure with a one-line description of each major file, full dependency list with a one-line reason for each, and known limitations of the prototype.

TECH STACK

- Backend: [specify — e.g. Flask/Python or Node/Express]
- Frontend: [specify — e.g. React, or server-rendered templates]
- Database: MySQL, running in Docker, with a schema for: users, drinks, snacks, pairings, ratings, and user_preferences.
- Image label recognition: [specify approach — e.g. OCR via Tesseract, or a vision API] for extracting drink names from uploaded photos. Note: this is the highest-risk feature for a one-day build; consider a fallback (manual search/select if OCR confidence is low) so the demo doesn't break on an unclear photo.

FEATURES

1. Auth: Login/logout/signup with session-based or JWT auth. Store per-user preference history and self-reported past purchases to inform future recommendations.

2. Drinks page: User uploads a photo of a drink shelf. The app extracts label text (OCR) and matches it against the drinks database, displaying results as a carousel of flashcards with a glassmorphism style (frosted-glass background blur, subtle border). Each card shows name, type, flavor profile, and a short description.

3. Pairings: For each identified drink, show 2-3 recommended snacks with a one-sentence reason for the pairing (e.g. flavor contrast, regional tradition, palate cleansing).

4. Ratings: Central drinks table stores an aggregate rating. Users can voluntarily log a drink they tried and rate it after the fact (no purchase flow in-app — this is a self-report action, not a transaction).

5. Recommendations: An onboarding form captures taste preferences (sweetness, acidity, strength, preferred type, etc.). Use this plus rating history to drive a simple recommendation logic (e.g. weighted similarity or filtered ranking — full ML isn't necessary for the prototype).

6. Profile page: Displays user info and preferences, editable.

7. Glossary/info page: Explains terms like tannic, acidity, body, finish, etc. Present this as an interactive quiz format (multiple choice, immediate feedback, simple animation on correct/incorrect answers) rather than static text, to keep it engaging.

8. Rating scale: Use a 5-point (or Vivino-style 1-5 star with half-star precision) rating scale consistently across both the ratings feature and any drink display, since this is the basis for the recommendation logic.

9. Chatbot: A simple Q&A assistant (rule-based or LLM-backed, depending on time available) that answers user questions about alcohol types, terms, or pairing logic, and can suggest a drink based on a natural-language description of preferences.

DESIGN

- Color palette: brown, black, and cream, used as a gradient or complementary mix across the UI (e.g. cream background, brown accents, black text/contrast elements).
- Font: "Lathena" (https://www.1001fonts.com/lathena-font.html). Since this is a licensed display font, use it for headings/branding only, and pair it with a readable web-safe fallback (e.g. system sans-serif) for body text, since Lathena is a decorative script style not optimized for long-form reading.

DELIVERABLE PRIORITY (if time-constrained, build in this order)

1. Docker + DB schema + auth
2. Drinks page with manual search (OCR as a stretch goal, with graceful fallback)
3. Pairings + ratings
4. Preferences form + basic recommendation logic
5. Profile page
6. Glossary quiz
7. Chatbot



Write the prompt that i have given you here in the rEADME.MD as well as the initial prompt
```
