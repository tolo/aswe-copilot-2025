# Priority Filter Implementation Plan

## Overview
Add filter buttons (All, Low, Medium, High) above the todo list that dynamically filter displayed todos by priority using HTMX and Shoelace components.

## Current Implementation Analysis

### Search Functionality
- **Endpoint**: `GET /api/todos/search` in `routes/todos.py`
- **Parameters**: `list_id` (required), `q` (search query, optional)
- **Pattern**: Uses SQLAlchemy's `ilike()` for case-insensitive title filtering
- **Response**: Returns `partials/todos_list.html` with filtered todos
- **HTMX Integration**: Search input uses `hx-get`, `hx-trigger="keyup changed delay:300ms"`, `hx-vals` for list_id

### HTMX Patterns Used
- **hx-get**: Fetch HTML partials from server
- **hx-target**: Specify where to swap content (e.g., `#todos-list`)
- **hx-swap**: Strategy for DOM update (innerHTML, beforeend, etc.)
- **hx-vals**: Add parameters to requests (JSON or dynamic JavaScript)
- **hx-trigger**: Control when requests fire (events, delays, filters)

### Shoelace Components
- **Forms**: Shoelace components work with HTMX via native form events (no extension needed)
- **Button variants**: default, primary, success, warning, danger
- **Button groups**: `<sl-button-group>` for grouped buttons with unified styling
- **Active state**: Use `variant="primary"` or custom CSS classes

### Styling Patterns
- **CSS variables**: Defined in `:root` for colors, spacing, etc.
- **BEM-style naming**: `.list-header`, `.search-bar`, `.quick-add-form`
- **Active states**: `.active` class with primary color and border
- **Responsive**: Mobile-first with flexbox/grid layouts

## Implementation Plan

### 1. Backend Changes

**File**: `todo-app/src/app/routes/todos.py`

**Modify**: `search_todos()` endpoint

Add optional `priority` query parameter:
```python
@router.get("/search", response_class=HTMLResponse)
async def search_todos(
    request: Request,
    user_id: Annotated[str, Depends(get_current_user_id)],
    list_id: str,
    q: str = "",
    priority: str = "",  # NEW: optional priority filter
    db: Session = Depends(get_db),
):
```

Add priority filtering logic after title search:
```python
if q.strip():
    query = query.filter(Todo.title.ilike(f"%{q.strip()}%"))

# NEW: Filter by priority if specified
# Note: Treats NULL priority as valid (shows in "All" filter)
if priority and priority in ("low", "medium", "high"):
    query = query.filter(Todo.priority == priority)

todos = query.order_by(Todo.position).all()
```

**Why**: This allows combining search query and priority filter (AND logic). Empty priority string shows all priorities, including NULL values. This is correct since the database schema allows NULL, and existing todos may not have priority set.

### 2. Frontend Changes

**File**: `todo-app/src/app/templates/partials/todo_list_content.html`

**Add**: Priority filter buttons between search bar and quick-add form

Insert after `</div>` closing the search-bar div:
```html
<!-- Priority Filter -->
<div class="priority-filter">
    <sl-button-group label="Filter by priority">
        <sl-button 
            size="small" 
            variant="primary"
            data-priority=""
            hx-get="/api/todos/search"
            hx-target="#todos-list"
            hx-swap="innerHTML"
            hx-vals='js:{"list_id": "{{ current_list.id }}", "priority": "", "q": getSearchQuery()}'
            onclick="setActiveFilter(this)">
            All
        </sl-button>
        <sl-button 
            size="small"
            data-priority="low"
            hx-get="/api/todos/search"
            hx-target="#todos-list"
            hx-swap="innerHTML"
            hx-vals='js:{"list_id": "{{ current_list.id }}", "priority": "low", "q": getSearchQuery()}'
            onclick="setActiveFilter(this)">
            Low
        </sl-button>
        <sl-button 
            size="small"
            data-priority="medium"
            hx-get="/api/todos/search"
            hx-target="#todos-list"
            hx-swap="innerHTML"
            hx-vals='js:{"list_id": "{{ current_list.id }}", "priority": "medium", "q": getSearchQuery()}'
            onclick="setActiveFilter(this)">
            Medium
        </sl-button>
        <sl-button 
            size="small"
            data-priority="high"
            hx-get="/api/todos/search"
            hx-target="#todos-list"
            hx-swap="innerHTML"
            hx-vals='js:{"list_id": "{{ current_list.id }}", "priority": "high", "q": getSearchQuery()}'
            onclick="setActiveFilter(this)">
            High
        </sl-button>
    </sl-button-group>
</div>
```

**Why**: 
- `hx-vals='js:{...}'` allows dynamic JavaScript evaluation to include current search query
- `data-priority` stores filter value for easy access
- `size="small"` matches UI scale
- Inline `onclick` for active state management (Shoelace pattern)

**Modify**: Search input to preserve priority filter

Update search input's `hx-vals` and add ID for stable reference:
```html
<sl-input
    id="todo-search"
    placeholder="Search todos..."
    clearable
    hx-get="/api/todos/search"
    hx-trigger="keyup changed delay:300ms, search"
    hx-target="#todos-list"
    hx-swap="innerHTML"
    hx-vals='js:{"list_id": "{{ current_list.id }}", "priority": getActivePriority()}'
    name="q">
    <sl-icon slot="prefix" name="search"></sl-icon>
</sl-input>
```

**Why**: ID-based selector (`#todo-search`) is more stable than class-based selector. The `getActivePriority()` helper ensures consistency with filter buttons.

### 3. JavaScript Changes

**File**: `todo-app/src/app/static/js/app.js`

**Add**: Filter state management functions

```javascript
// Priority filter state management
function setActiveFilter(button) {
    // Remove primary variant from all filter buttons
    const filterGroup = button.closest('sl-button-group');
    if (filterGroup) {
        filterGroup.querySelectorAll('sl-button').forEach(btn => {
            btn.setAttribute('variant', 'default');
            btn.removeAttribute('aria-pressed');
        });
    }
    
    // Set clicked button to primary with ARIA support
    button.setAttribute('variant', 'primary');
    button.setAttribute('aria-pressed', 'true');
}

function getActivePriority() {
    const activeButton = document.querySelector('.priority-filter sl-button[variant="primary"]');
    return activeButton ? activeButton.dataset.priority : '';
}

function getSearchQuery() {
    const searchInput = document.getElementById('todo-search');
    return searchInput ? (searchInput.value || '') : '';
}

// Re-initialize filter state after HTMX swaps
document.body.addEventListener('htmx:afterSwap', (evt) => {
    if (evt.detail.target.id === 'todos-list' || evt.detail.target.id === 'main-content') {
        initTodoSortable();
        
        // Reset "All" filter to active if no filter is set
        const filterGroup = document.querySelector('.priority-filter sl-button-group');
        if (filterGroup && !filterGroup.querySelector('sl-button[variant="primary"]')) {
            const allButton = filterGroup.querySelector('sl-button[data-priority=""]');
            if (allButton) {
                allButton.setAttribute('variant', 'primary');
                allButton.setAttribute('aria-pressed', 'true');
            }
        }
    }
});
```

**Why**: 
- Manages visual active state (primary variant) using `setAttribute()` for Shoelace web component compatibility
- Adds `aria-pressed` for screen reader accessibility
- Provides `getActivePriority()` helper to get current filter for search integration
- Provides `getSearchQuery()` helper using stable ID selector for consistency
- Resets to "All" after content swaps to maintain UI consistency
- Uses ID-based selector (`#todo-search`) instead of class-based for stability

### 4. CSS Changes

**File**: `todo-app/src/app/static/css/styles.css`

**Add**: After `.search-bar` styles (around line 340)

```css
/* Priority filter */
.priority-filter {
    margin-bottom: 16px;
}

.priority-filter sl-button-group {
    display: flex;
    width: 100%;
}

.priority-filter sl-button {
    flex: 1;
}

/* Ensure filter buttons are visually distinct when active */
.priority-filter sl-button[variant="primary"]::part(base) {
    background-color: var(--color-primary);
    color: white;
    border-color: var(--color-primary);
}

/* Responsive: Stack filters on mobile if needed */
@media (max-width: 480px) {
    .priority-filter sl-button-group {
        flex-wrap: wrap;
    }
    
    .priority-filter sl-button {
        flex: 1 1 45%;
        min-width: 80px;
    }
}
```

**Why**: 
- Consistent spacing with search bar
- Equal-width buttons for clean layout
- Primary variant styling for active state
- Mobile-responsive design

### 5. Testing

**File**: `todo-app/tests/test_todos.py`

**Add**: Test cases for priority filtering

```python
def test_filter_by_priority_low(self, authenticated_client, test_list, db_session):
    """Test filtering todos by low priority."""
    todos = [
        Todo(list_id=test_list.id, title="Low task", priority="low", position=0),
        Todo(list_id=test_list.id, title="High task", priority="high", position=1),
        Todo(list_id=test_list.id, title="Medium task", priority="medium", position=2),
    ]
    for todo in todos:
        db_session.add(todo)
    db_session.commit()

    response = authenticated_client.get(
        f"/api/todos/search?list_id={test_list.id}&priority=low"
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "Low task" in content
    assert "High task" not in content
    assert "Medium task" not in content

def test_filter_by_priority_medium(self, authenticated_client, test_list, db_session):
    """Test filtering todos by medium priority."""
    todos = [
        Todo(list_id=test_list.id, title="Low task", priority="low", position=0),
        Todo(list_id=test_list.id, title="High task", priority="high", position=1),
        Todo(list_id=test_list.id, title="Medium task", priority="medium", position=2),
    ]
    for todo in todos:
        db_session.add(todo)
    db_session.commit()

    response = authenticated_client.get(
        f"/api/todos/search?list_id={test_list.id}&priority=medium"
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "Medium task" in content
    assert "Low task" not in content
    assert "High task" not in content

def test_filter_by_priority_high(self, authenticated_client, test_list, db_session):
    """Test filtering todos by high priority."""
    todos = [
        Todo(list_id=test_list.id, title="Low task", priority="low", position=0),
        Todo(list_id=test_list.id, title="High task", priority="high", position=1),
        Todo(list_id=test_list.id, title="Medium task", priority="medium", position=2),
    ]
    for todo in todos:
        db_session.add(todo)
    db_session.commit()

    response = authenticated_client.get(
        f"/api/todos/search?list_id={test_list.id}&priority=high"
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "High task" in content
    assert "Low task" not in content
    assert "Medium task" not in content

def test_filter_all_shows_all_priorities(self, authenticated_client, test_list, db_session):
    """Test that empty priority filter shows all todos."""
    todos = [
        Todo(list_id=test_list.id, title="Low task", priority="low", position=0),
        Todo(list_id=test_list.id, title="High task", priority="high", position=1),
        Todo(list_id=test_list.id, title="Medium task", priority="medium", position=2),
    ]
    for todo in todos:
        db_session.add(todo)
    db_session.commit()

    response = authenticated_client.get(
        f"/api/todos/search?list_id={test_list.id}&priority="
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "Low task" in content
    assert "High task" in content
    assert "Medium task" in content

def test_filter_with_search_query(self, authenticated_client, test_list, db_session):
    """Test combining priority filter with search query."""
    todos = [
        Todo(list_id=test_list.id, title="Buy groceries", priority="low", position=0),
        Todo(list_id=test_list.id, title="Buy laptop", priority="high", position=1),
        Todo(list_id=test_list.id, title="Call mom", priority="high", position=2),
    ]
    for todo in todos:
        db_session.add(todo)
    db_session.commit()

    # Filter high priority + search "buy"
    response = authenticated_client.get(
        f"/api/todos/search?list_id={test_list.id}&priority=high&q=buy"
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "Buy laptop" in content
    assert "Buy groceries" not in content  # Low priority
    assert "Call mom" not in content  # Doesn't match "buy"

def test_filter_empty_results(self, authenticated_client, test_list, db_session):
    """Test filter showing empty state when no matches."""
    todos = [
        Todo(list_id=test_list.id, title="Low task", priority="low", position=0),
        Todo(list_id=test_list.id, title="Medium task", priority="medium", position=1),
    ]
    for todo in todos:
        db_session.add(todo)
    db_session.commit()

    response = authenticated_client.get(
        f"/api/todos/search?list_id={test_list.id}&priority=high"
    )
    assert response.status_code == 200
    content = response.content.decode()
    # Should show empty state with inbox icon and message
    assert 'class="empty-todos"' in content
    assert 'No todos yet' in content or 'No todos match' in content

def test_filter_invalid_priority_ignored(self, authenticated_client, test_list, db_session):
    """Test that invalid priority values are ignored."""
    todos = [
        Todo(list_id=test_list.id, title="Low task", priority="low", position=0),
        Todo(list_id=test_list.id, title="High task", priority="high", position=1),
    ]
    for todo in todos:
        db_session.add(todo)
    db_session.commit()

    # Invalid priority should show all (like empty filter)
    response = authenticated_client.get(
        f"/api/todos/search?list_id={test_list.id}&priority=invalid"
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "Low task" in content
    assert "High task" in content

def test_filter_handles_null_priority(self, authenticated_client, test_list, db_session):
    """Test that todos with NULL priority appear in 'All' filter."""
    todos = [
        Todo(list_id=test_list.id, title="Has priority", priority="low", position=0),
        Todo(list_id=test_list.id, title="No priority", priority=None, position=1),
    ]
    for todo in todos:
        db_session.add(todo)
    db_session.commit()

    # All filter should show both
    response = authenticated_client.get(
        f"/api/todos/search?list_id={test_list.id}&priority="
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "Has priority" in content
    assert "No priority" in content

    # Specific filter should only show matching priority
    response = authenticated_client.get(
        f"/api/todos/search?list_id={test_list.id}&priority=low"
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "Has priority" in content
    assert "No priority" not in content
```

**Why**: Comprehensive coverage of:
- Individual priority filters (low, medium, high)
- "All" filter behavior
- Combined search + priority filtering
- Empty results handling
- Invalid input handling

## Edge Cases & Considerations

### 1. NULL Priority Values
**Decision**: Show in "All" filter, hide in specific priority filters
**Rationale**: Database schema allows NULL (existing todos may not have priority set). "All" should be inclusive, specific filters should be exact matches.
**Implementation**: Backend query only filters when priority is in ("low", "medium", "high"), otherwise shows all including NULL.

### 2. Filter Persistence
**Decision**: Reset to "All" when switching lists
**Rationale**: Users expect fresh context per list; persisting filter across lists could be confusing
**Note**: Not implemented in this phase - filter state persists during session. Add list-switch event listener if this becomes a UX issue.

### 3. Search + Filter Interaction
**Implementation**: AND logic (both conditions must match)
**UX**: Clearing search preserves priority filter; changing filter preserves search query
**Technical**: `hx-vals='js:{...}'` dynamically reads current state using helper functions (`getSearchQuery()`, `getActivePriority()`)

### 4. URL State
**Decision**: Don't add to URL (client-side only)
**Rationale**: 
- Simpler implementation
- Filters are quick to toggle
- Search already doesn't persist in URL
- If needed later, add `hx-push-url` to filter buttons

### 5. Accessibility
**Implementation**:
- `sl-button-group` has `label` attribute for screen readers
- Keyboard navigation works via Shoelace's built-in support
- Visual active state clearly indicates selected filter
- `aria-pressed="true"` added to active button via `setActiveFilter()`

### 6. Performance
**Current**: No issues expected (small datasets, indexed queries)
**Optimization**: If lists grow large, consider:
- Adding database index on `(list_id, priority)`
- Caching filter results client-side
- Virtual scrolling for very long lists

## HTMX Patterns Research

### Best Practices Used
1. **Dynamic values**: `hx-vals='js:{...}'` for computed parameters
2. **Debounced search**: `delay:300ms` prevents excessive requests
3. **Target swapping**: `hx-target="#todos-list"` for partial updates
4. **Event coordination**: Search and filters both update same target
5. **State preservation**: JavaScript functions read current UI state

### Shoelace Button Group
- **Component**: `<sl-button-group>` provides visual grouping
- **Variants**: Use `variant="primary"` for active state
- **Shadow DOM**: Use `::part(base)` for styling internals
- **Events**: `onclick` works with Shoelace buttons (use inline or delegation)

## Files to Modify

1. **Backend**: `todo-app/src/app/routes/todos.py` - Add priority parameter
2. **Template**: `todo-app/src/app/templates/partials/todo_list_content.html` - Add filter UI
3. **JavaScript**: `todo-app/src/app/static/js/app.js` - Add state management
4. **CSS**: `todo-app/src/app/static/css/styles.css` - Add filter styles
5. **Tests**: `todo-app/tests/test_todos.py` - Add filter tests

## Files to Create

None - all changes are modifications to existing files.

## Implementation Notes

### Key Technical Decisions

1. **NULL Priority Handling**: Database allows NULL priority (schema has no NOT NULL constraint). The "All" filter shows todos with NULL priority, specific filters exclude them. This is correct behavior since older todos may not have priority set.

2. **Stable Selectors**: All JavaScript uses ID-based selectors (`#todo-search`) or data attributes (`data-priority`) instead of class-based selectors for stability across template changes.

3. **Helper Functions**: Introduced `getSearchQuery()` and `getActivePriority()` to centralize state reading logic, making code DRY and maintainable.

4. **Web Component Compatibility**: Using `setAttribute('variant', 'primary')` instead of direct property assignment for reliable Shoelace Shadow DOM updates.

5. **Accessibility**: Added `aria-pressed` attribute to filter buttons for screen reader support.

### Code Quality Checks

- [ ] All selectors use IDs or data attributes (no class-based)
- [ ] JavaScript helpers are DRY (no duplicated querySelector logic)
- [ ] ARIA attributes present for accessibility
- [ ] NULL priority handled correctly in backend
- [ ] Tests cover NULL priority edge case
- [ ] Empty state message matches actual template

## Acceptance Criteria

- [ ] Filter buttons visible and styled consistently
- [ ] "All" button active by default
- [ ] Clicking filter button updates todos list
- [ ] Active filter has primary variant styling
- [ ] Search + filter work together (AND logic)
- [ ] Clearing search preserves filter
- [ ] Changing filter preserves search query
- [ ] Empty state shows when no matches
- [ ] Invalid priority values ignored (shows all)
- [ ] All tests passing
- [ ] Mobile responsive layout
- [ ] Keyboard accessible
- [ ] Works with drag-drop (doesn't interfere)

## Implementation Order

1. Backend endpoint changes (easiest to test in isolation)
2. Add basic filter UI without JavaScript
3. Add CSS styling
4. Add JavaScript state management
5. Connect search with filter
6. Write and run tests
7. Visual validation in browser
8. Accessibility check

## Potential Issues

1. ~~**Shoelace variant not updating**~~: **FIXED** - Using `setAttribute('variant', 'primary')` for reliable web component property setting
2. ~~**Search input reference**~~: **FIXED** - Using ID selector `#todo-search` instead of fragile class-based selector
3. **HTMX afterSwap timing**: Filter state might reset on content swaps - handled in event listener by checking for active filter
4. **List switching**: Filter state currently persists across list switches - acceptable for MVP, but consider adding reset logic if UX feedback indicates confusion

## Future Enhancements

1. **Multi-select filters**: Allow filtering by multiple priorities at once
2. **Filter badges**: Show count of todos per priority
3. **Filter presets**: Save custom filter combinations
4. **URL state**: Add filters to URL for shareable links
5. **Filter animations**: Smooth transitions when switching filters
