# Project Context

This repository is a front-end/back-end separated sign language learning and communication platform.

The frontend is located in `web-vue3/` and is built with Vue 3, TypeScript, Vite, Element Plus, Pinia, Vue Router, Axios, and ECharts.

The backend is located in `x-admin/` and is built with Spring Boot 3, Java 17, MyBatis Plus, MySQL, Redis, Spring Security, JWT, and SpringDoc OpenAPI.

Core features include question bank management, question set management, challenge mode, user management, RBAC-based role/menu permissions, learning progress tracking, and challenge history statistics.

## Project Rules

- Keep changes small and directly related to the requested task.
- Preserve the existing front-end/back-end separated architecture.
- Do not change existing API paths, database fields, route names, or permission logic unless explicitly requested.
- Backend controllers should stay thin; business logic belongs in service classes.
- When changing backend data logic, check entity, mapper, MyBatis XML, service, and controller together.
- When changing frontend pages, check related API definitions, routes, Pinia store, and Element Plus form/table logic together.
- For dynamic menu and keep-alive behavior, ensure component `name` matches the route/menu `name`.
- For permission-related changes, preserve the existing User -> Role -> Menu RBAC model.
- Do not hardcode database passwords, Redis passwords, JWT secrets, API addresses, or production URLs.
- Prefer readable and explainable code over large refactors or unnecessary abstraction.

## Common Commands

### Backend

```bash
cd x-admin
mvn spring-boot:run
mvn clean package
```

### Frontend

```bash
cd web-vue3
npm install
npm run dev:prod
npm run dev:test
npm run build:prod
npm run build:test
```

### Docker

```bash
docker compose up -d --build
docker compose logs -f
docker compose down
```

## Verification

Before finishing a task, summarize:

1. What changed
2. Which files were affected
3. How to run or verify it

---

# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them; don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it; don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" -> "Write tests for invalid inputs, then make them pass"
- "Fix the bug" -> "Write a test that reproduces it, then make it pass"
- "Refactor X" -> "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```text
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

Strong success criteria let you loop independently. Weak criteria such as "make it work" require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
