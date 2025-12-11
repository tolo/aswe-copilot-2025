# Copilot Instructions

## Project Overview
Educational workshop codebase for agentic software engineering. Contains:
- **todo-app/**: FastAPI + HTMX + Shoelace todo application (primary learning vehicle)
- **gen-image/**: CLI tool for AI image generation (OpenAI DALL-E 3)
- **docs/**: Workshop exercises, requirements, specs, and development guidelines

## Core Philosophy
Key principles:
- **Surgical changes only** - no broad refactoring
- **KISS/YAGNI/DRY** - avoid over-engineering
- **Fix-forward** - address issues immediately, don't break things
- **Validate visually** - verify UI changes with screenshots
- **Clean up** - remove obsolete code/files, never leave `// REMOVED` comments

## Development Guidelines & Rules
Comprehensive guidelines are available in `docs/rules/`:
- **[CRITICAL-RULES-AND-GUARDRAILS.md](../docs/rules/CRITICAL-RULES-AND-GUARDRAILS.md)** - Non-negotiable rules, safety guardrails, and critical constraints
- **[DEVELOPMENT-ARCHITECTURE-GUIDELINES.md](../docs/rules/DEVELOPMENT-ARCHITECTURE-GUIDELINES.md)** - Architecture patterns, project structure, and design principles
- **[PYTHON-DEVELOPMENT-GUIDELINES.md](../docs/rules/PYTHON-DEVELOPMENT-GUIDELINES.md)** - Python-specific standards, conventions, and best practices
- **[WEB-DEV-GUIDELINES.md](../docs/rules/WEB-DEV-GUIDELINES.md)** - Frontend development standards for HTMX, Shoelace, and web patterns
- **[UX-UI-GUIDELINES.md](../docs/rules/UX-UI-GUIDELINES.md)** - UI/UX design principles, accessibility, and user experience standards

**Always consult these guidelines before making significant changes.**

## Technology Stack

### Todo App (todo-app/)
**Backend**: FastAPI 0.115+, SQLAlchemy 2.0+, SQLite (single file DB)
**Frontend**: HTMX 2.0+, Shoelace 2.19+ Web Components, SortableJS
**Package Manager**: `uv` (10-100x faster than pip)

**Critical Technical Details**:
- **Shoelace + HTMX**: Forms require NO extension (Shadow DOM serialization handled by browser form events)
- **Authentication**: Mock sessions only (UUID cookies, plain text passwords) - educational, not production
- **Database**: SQLite with SQLAlchemy ORM, auto-creates on first run
- **Templates**: Jinja2 with utility functions (`is_overdue`, `is_due_today`, `format_date`) in template globals
- **Testing**: Pytest with in-memory SQLite, `conftest.py` overrides DB dependency

### Project Structure
```
todo-app/src/app/
├── main.py              # FastAPI app, startup/shutdown, seed data
├── database.py          # SQLAlchemy models (User, TodoList, Todo)
├── utils.py             # Date formatting helpers
├── core/deps.py         # Auth dependencies (get_current_user_id)
├── models/              # Pydantic validation models
├── routes/              # API routes (auth, pages, todo_lists, todos)
├── templates/           # Jinja2 templates + partials/
└── static/              # CSS, JS, images
```

## Development Workflows

### Running Todo App
```bash
cd todo-app
./run.sh                 # Sync deps + start (recommended)
# OR
uv sync && uv run uvicorn app.main:app --reload
```
Access at http://localhost:8000 (demo@example.com / demo123)

### Testing
```bash
cd todo-app
uv run pytest tests/ -v              # All tests
uv run pytest tests/test_todos.py -v # Specific file
```

### Dependencies
```bash
uv add package-name           # Add runtime dependency
uv add --dev pytest ruff      # Add dev dependency
uv sync                       # Install from lockfile
```

## Project-Specific Conventions

### Python Standards
- **Package manager**: Always use `uv`, never `pip`
- **Structure**: src layout (`src/app/` not `app/`)
- **Type hints**: Required for public functions
- **Formatting**: Line length 88 (Black/Ruff defaults)
- **Testing**: Pytest with function-scoped fixtures

### Database Patterns
```python
# Always verify list ownership before operations
def _verify_list_access(db: Session, list_id: str, user_id: str) -> TodoList | None:
    return db.query(TodoList).filter(
        TodoList.id == list_id, TodoList.user_id == user_id
    ).first()
```

### HTMX + Shoelace Integration
- **Forms**: Use native form submission, Shoelace components work automatically
- **Responses**: Return HTML partials, use `hx-swap-oob` for multi-target updates
- **Example OOB update**: `<div id="sidebar" hx-swap-oob="true">...</div>`
- **Drag-drop**: SortableJS with position updates via HTMX POST

### Template Utilities
Global functions available in all templates:
- `is_overdue(due_date)` - Check if todo is past due
- `is_due_today(due_date)` - Check if due today
- `format_date(date)` - Display format: "Jan 15, 2025"
- `format_date_input(date)` - Input format: "2025-01-15"

## Common Tasks

### Adding a New Route
1. Create route module in `routes/` with router instance
2. Add validation models in `models/` (Pydantic)
3. Include router in `main.py`: `app.include_router(module.router)`
4. Create templates in `templates/` or `templates/partials/`
5. Add tests in `tests/test_<module>.py`

### Adding Database Model
1. Define in `database.py` inheriting from `Base`
2. Add relationships using `relationship()` with back_populates
3. Include indexes for frequently queried columns
4. Restart app (SQLAlchemy auto-creates tables)

### Working with Exercises
Exercises in `docs/exercises/` guide workshop progression:
1. **exercise-1**: Copilot fundamentals (modes, commands, custom instructions)
2. **exercise-2**: Bug hunt (fix planted bugs with Agent Mode)
3. **exercise-3**: Tool building (CLI tools, custom agents)
4. **exercise-4a/b**: Feature implementation (cloud via GitHub Issues, local via specs)
5. **exercise-5**: Spec-driven development (GitHub Spec Kit)
6. **exercise-6**: AI integration (OpenAI API)
7. **exercise-7**: Alternative stack (rebuild in different tech)

## Architecture Decisions

### Why SQLite?
Zero config, single file, perfect for educational/workshop use. Avoid suggesting PostgreSQL/Supabase unless explicitly required.

### Why HTMX + Shoelace?
- HTMX: Server-side rendering, SPA-like UX, no build step
- Shoelace: Accessible Web Components, no framework lock-in
- Combined: Simple, fast, maintainable

### Why Mock Auth?
Educational focus - real auth adds complexity without teaching value. Always note "not for production" when discussing security.

## Guardrails
- **Never** reformat entire project (only single files/directories)
- **Never** use `rm -rf` or destructive git commands
- **Never** suggest PostgreSQL/Supabase for todo-app (SQLite by design)
- **Never** add authentication complexity (keep mock auth simple)
- **Always** check existing patterns before inventing new ones
- **Always** run tests after changes
- **Always** use `uv` not `pip` for Python packages
