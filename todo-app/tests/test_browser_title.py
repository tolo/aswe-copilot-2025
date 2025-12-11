"""Tests for browser title todo count feature."""

import pytest
from app.database import Todo, TodoList


class TestBrowserTitleCount:
    """Test browser title shows incomplete todo count."""

    def test_title_shows_count_when_incomplete_todos(self, authenticated_client, test_list, db_session):
        """Test that title shows count when there are incomplete todos."""
        # Create 3 incomplete todos
        for i in range(3):
            todo = Todo(
                list_id=test_list.id,
                title=f"Todo {i+1}",
                is_completed=False,
                position=i,
            )
            db_session.add(todo)
        db_session.commit()

        # Get the app page
        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        assert response.status_code == 200
        
        # Check title contains count
        content = response.content.decode()
        assert f"<title>(3) {test_list.name} - Todo App</title>" in content

    def test_title_no_count_when_all_complete(self, authenticated_client, test_list, db_session):
        """Test that title doesn't show count when all todos are complete."""
        # Create 3 completed todos
        for i in range(3):
            todo = Todo(
                list_id=test_list.id,
                title=f"Todo {i+1}",
                is_completed=True,
                position=i,
            )
            db_session.add(todo)
        db_session.commit()

        # Get the app page
        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        assert response.status_code == 200
        
        # Check title doesn't contain count
        content = response.content.decode()
        assert f"<title>{test_list.name} - Todo App</title>" in content
        assert "(0)" not in content

    def test_title_no_count_when_empty_list(self, authenticated_client, test_list):
        """Test that title doesn't show count when list is empty."""
        # Get the app page with empty list
        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        assert response.status_code == 200
        
        # Check title doesn't contain count
        content = response.content.decode()
        assert f"<title>{test_list.name} - Todo App</title>" in content
        assert "(" not in content or "(0)" not in content

    def test_title_update_oob_on_toggle(self, authenticated_client, test_todo, db_session):
        """Test that toggling a todo returns OOB update for title."""
        # Ensure todo is incomplete
        test_todo.is_completed = False
        db_session.commit()

        # Toggle the todo
        response = authenticated_client.patch(f"/api/todos/{test_todo.id}/toggle")
        assert response.status_code == 200
        
        # Check response contains OOB title update
        content = response.content.decode()
        assert 'id="title-update"' in content
        assert 'hx-swap-oob="true"' in content

    def test_title_update_oob_on_create(self, authenticated_client, test_list):
        """Test that creating a todo returns OOB update for title."""
        response = authenticated_client.post(
            "/api/todos",
            data={
                "list_id": test_list.id,
                "title": "New Todo",
            },
        )
        assert response.status_code == 200
        
        # Check response contains OOB title update
        content = response.content.decode()
        assert 'id="title-update"' in content
        assert 'hx-swap-oob="true"' in content

    def test_title_update_oob_on_delete(self, authenticated_client, test_todo):
        """Test that deleting a todo returns OOB update for title."""
        response = authenticated_client.delete(f"/api/todos/{test_todo.id}")
        assert response.status_code == 200
        
        # Check response contains OOB title update
        content = response.content.decode()
        assert 'id="title-update"' in content
        assert 'hx-swap-oob="true"' in content
