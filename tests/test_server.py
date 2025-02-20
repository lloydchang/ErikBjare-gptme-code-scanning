import random

import pytest

flask = pytest.importorskip(
    "flask", reason="flask not installed, install server extras (-E server)"
)

# noreorder
from flask.testing import FlaskClient  # fmt: skip
from gptme.cli import init  # fmt: skip
from gptme.server import create_app  # fmt: skip


@pytest.fixture(autouse=True)
def init_():
    init(verbose=False, llm="openai", model="gpt-3.5-turbo", interactive=False)


@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client


@pytest.fixture
def conv(client: FlaskClient):
    convname = f"test-server-{random.randint(0, 1000000)}"
    response = client.put(f"/api/conversations/{convname}", json={})
    assert response.status_code == 200
    return convname


def test_root(client: FlaskClient):
    response = client.get("/")
    assert response.status_code == 200


def test_api_root(client: FlaskClient):
    response = client.get("/api")
    assert response.status_code == 200
    assert response.get_json() == {"message": "Hello World!"}


def test_api_conversation_list(client: FlaskClient):
    response = client.get("/api/conversations")
    assert response.status_code == 200


def test_api_conversation_get(conv, client: FlaskClient):
    response = client.get(f"/api/conversations/{conv}")
    assert response.status_code == 200


def test_api_conversation_post(conv, client: FlaskClient):
    response = client.post(
        f"/api/conversations/{conv}",
        json={"role": "user", "content": "hello"},
    )
    assert response.status_code == 200


@pytest.mark.slow
def test_api_conversation_generate(conv: str, client: FlaskClient):
    # Ask the assistant to generate a test response
    response = client.post(
        f"/api/conversations/{conv}",
        json={"role": "user", "content": "hello"},
    )
    assert response.status_code == 200

    response = client.post(
        f"/api/conversations/{conv}/generate",
        json={"model": "gpt-3.5-turbo"},
    )
    assert response.status_code == 200
    msgs = response.get_json()
    assert len(msgs) == 1
    assert msgs[0]["role"] == "assistant"
