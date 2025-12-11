"""Tests for todo item routes."""

from datetime import date, datetime, timezone

import pytest

from app.database import Todo


class TestTodos:
    """Tests for todo CRUD operations."""

    def test_create_todo(self, authenticated_client, test_list, db_session):
        """Test creating a new todo."""
        response = authenticated_client.post(
            "/api/todos",
            data={
                "list_id": test_list.id,
                "title": "New Todo",
            },
        )
        assert response.status_code == 200
        assert b"New Todo" in response.content

        # Verify in database
        created = db_session.query(Todo).filter(Todo.title == "New Todo").first()
        assert created is not None
        assert created.list_id == test_list.id
        assert created.priority == "low"
        assert created.is_completed is False

    def test_create_todo_empty_title(self, authenticated_client, test_list):
        """Test creating todo with empty title fails."""
        response = authenticated_client.post(
            "/api/todos",
            data={
                "list_id": test_list.id,
                "title": "   ",
            },
        )
        assert response.status_code == 200
        assert b"required" in response.content

    def test_update_todo(self, authenticated_client, test_todo, db_session):
        """Test updating a todo."""
        response = authenticated_client.put(
            f"/api/todos/{test_todo.id}",
            data={
                "title": "Updated Title",
                "note": "Updated note",
                "due_date": "2025-12-31",
                "priority": "high",
            },
        )
        assert response.status_code == 200

        # Verify in database
        db_session.refresh(test_todo)
        assert test_todo.title == "Updated Title"
        assert test_todo.note == "Updated note"
        assert test_todo.due_date.year == 2025
        assert test_todo.priority == "high"

    def test_toggle_todo_complete(self, authenticated_client, test_todo, db_session):
        """Test toggling todo completion."""
        assert test_todo.is_completed is False

        # Toggle to complete
        response = authenticated_client.patch(f"/api/todos/{test_todo.id}/toggle")
        assert response.status_code == 200

        db_session.refresh(test_todo)
        assert test_todo.is_completed is True
        assert test_todo.completed_at is not None

        # Toggle back to incomplete
        response = authenticated_client.patch(f"/api/todos/{test_todo.id}/toggle")
        assert response.status_code == 200

        db_session.refresh(test_todo)
        assert test_todo.is_completed is False
        assert test_todo.completed_at is None

    def test_delete_todo(self, authenticated_client, test_todo, db_session):
        """Test deleting a todo."""
        todo_id = test_todo.id
        response = authenticated_client.delete(f"/api/todos/{todo_id}")
        assert response.status_code == 200

        # Verify deleted
        deleted = db_session.query(Todo).filter(Todo.id == todo_id).first()
        assert deleted is None

    def test_reorder_todo_move_up(self, authenticated_client, test_list, db_session):
        """Test reordering a todo to an earlier position."""
        # Create three todos
        todo1 = Todo(list_id=test_list.id, title="Todo 1", position=0)
        todo2 = Todo(list_id=test_list.id, title="Todo 2", position=1)
        todo3 = Todo(list_id=test_list.id, title="Todo 3", position=2)
        db_session.add_all([todo1, todo2, todo3])
        db_session.commit()

        # Move todo3 to position 0
        response = authenticated_client.post(
            f"/api/todos/{todo3.id}/reorder",
            data={"position": 0},
        )
        assert response.status_code == 200

        # Verify positions updated
        db_session.refresh(todo1)
        db_session.refresh(todo2)
        db_session.refresh(todo3)
        assert todo3.position == 0
        assert todo1.position == 1
        assert todo2.position == 2

    def test_reorder_todo_move_down(self, authenticated_client, test_list, db_session):
        """Test reordering a todo to a later position."""
        # Create three todos
        todo1 = Todo(list_id=test_list.id, title="Todo 1", position=0)
        todo2 = Todo(list_id=test_list.id, title="Todo 2", position=1)
        todo3 = Todo(list_id=test_list.id, title="Todo 3", position=2)
        db_session.add_all([todo1, todo2, todo3])
        db_session.commit()

        # Move todo1 to position 2
        response = authenticated_client.post(
            f"/api/todos/{todo1.id}/reorder",
            data={"position": 2},
        )
        assert response.status_code == 200

        # Verify positions updated
        db_session.refresh(todo1)
        db_session.refresh(todo2)
        db_session.refresh(todo3)
        assert todo2.position == 0
        assert todo3.position == 1
        assert todo1.position == 2

    def test_search_todos(self, authenticated_client, test_list, db_session):
        """Test searching todos."""
        # Create some todos
        todos = [
            Todo(list_id=test_list.id, title="Buy groceries", position=0),
            Todo(list_id=test_list.id, title="Buy milk", position=1),
            Todo(list_id=test_list.id, title="Send email", position=2),
        ]
        for todo in todos:
            db_session.add(todo)
        db_session.commit()

        # Search for "buy"
        response = authenticated_client.get(
            f"/api/todos/search?list_id={test_list.id}&q=buy"
        )
        assert response.status_code == 200
        assert b"Buy groceries" in response.content
        assert b"Buy milk" in response.content
        assert b"Send email" not in response.content

    def test_search_case_insensitive(self, authenticated_client, test_list, db_session):
        """Test search is case-insensitive."""
        todo = Todo(list_id=test_list.id, title="Buy Groceries", position=0)
        db_session.add(todo)
        db_session.commit()

        # Search with different case
        response = authenticated_client.get(
            f"/api/todos/search?list_id={test_list.id}&q=BUY"
        )
        assert response.status_code == 200
        assert b"Buy Groceries" in response.content

    def test_search_empty_query(self, authenticated_client, test_list, db_session):
        """Test search with empty query returns all todos."""
        todos = [
            Todo(list_id=test_list.id, title="Todo 1", position=0),
            Todo(list_id=test_list.id, title="Todo 2", position=1),
        ]
        for todo in todos:
            db_session.add(todo)
        db_session.commit()

        response = authenticated_client.get(
            f"/api/todos/search?list_id={test_list.id}&q="
        )
        assert response.status_code == 200
        assert b"Todo 1" in response.content
        assert b"Todo 2" in response.content


class TestTodoAccess:
    """Tests for todo access control."""

    def test_cannot_access_other_users_todo(self, client, test_todo, db_session):
        """Test users cannot access other users' todos."""
        import bcrypt
        from app.core.deps import create_session
        from app.database import User

        # Create another user
        hashed_password = bcrypt.hashpw(b"password", bcrypt.gensalt())
        other_user = User(email="other@example.com", password=hashed_password.decode('utf-8'))
        db_session.add(other_user)
        db_session.commit()

        # Authenticate as other user
        session_id = create_session(other_user.id)
        client.cookies.set("session_id", session_id)

        # Try to access the todo
        response = client.get(f"/api/todos/{test_todo.id}?list_id={test_todo.list_id}")
        assert response.status_code == 403

    def test_cannot_modify_other_users_todo(self, client, test_todo, db_session):
        """Test users cannot modify other users' todos."""
        import bcrypt
        from app.core.deps import create_session
        from app.database import User

        # Create another user
        hashed_password = bcrypt.hashpw(b"password", bcrypt.gensalt())
        other_user = User(email="other@example.com", password=hashed_password.decode('utf-8'))
        db_session.add(other_user)
        db_session.commit()

        # Authenticate as other user
        session_id = create_session(other_user.id)
        client.cookies.set("session_id", session_id)

        # Try to update the todo
        response = client.put(
            f"/api/todos/{test_todo.id}",
            data={"title": "Hacked!"},
        )
        assert response.status_code == 403

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
        # Should show empty state
        assert 'class="empty-todos"' in content

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
