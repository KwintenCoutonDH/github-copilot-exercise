"""Integration tests for static file serving."""

import pytest


class TestStaticFiles:
    """Test cases for static file serving."""

    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)

        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"

    def test_static_index_html_served(self, client):
        """Test that index.html is served correctly."""
        response = client.get("/static/index.html")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        content = response.text
        assert "<!DOCTYPE html>" in content
        assert "Mergington High School" in content

    def test_static_styles_css_served(self, client):
        """Test that styles.css is served correctly."""
        response = client.get("/static/styles.css")

        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]
        content = response.text
        assert "body" in content  # Basic CSS check
        assert "font-family" in content

    def test_static_app_js_served(self, client):
        """Test that app.js is served correctly."""
        response = client.get("/static/app.js")

        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]
        content = response.text
        assert "DOMContentLoaded" in content
        assert "fetchActivities" in content

    def test_static_file_not_found(self, client):
        """Test that non-existent static files return 404."""
        response = client.get("/static/nonexistent.txt")

        assert response.status_code == 404

    def test_api_docs_available(self, client):
        """Test that FastAPI documentation is available."""
        response = client.get("/docs")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        content = response.text
        assert "FastAPI" in content or "Swagger" in content

    def test_api_redoc_available(self, client):
        """Test that ReDoc documentation is available."""
        response = client.get("/redoc")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        content = response.text
        assert "ReDoc" in content or "redoc" in content.lower()

    def test_openapi_json_available(self, client):
        """Test that OpenAPI JSON spec is available."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
        assert "/activities" in data["paths"]