"""Tests for trello_client_api.exceptions coverage."""

from trello_client_api.exceptions import (
    TrelloAPIError,
    TrelloAuthenticationError,
    TrelloNotFoundError,
    TrelloRateLimitError,
)


def test_exception_classes_can_be_instantiated() -> None:
    api_err = TrelloAPIError("boom", 400)
    assert isinstance(api_err, TrelloAPIError)
    assert api_err.status_code == 400

    auth_err = TrelloAuthenticationError()
    assert isinstance(auth_err, TrelloAuthenticationError)

    nf_err = TrelloNotFoundError("missing")
    assert nf_err.status_code == 404

    rl_err = TrelloRateLimitError("slow down")
    assert rl_err.status_code == 429
