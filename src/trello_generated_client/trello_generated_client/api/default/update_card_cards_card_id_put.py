from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.trello_card import TrelloCard
from ...types import UNSET, Response, Unset


def _get_kwargs(
    card_id: str,
    *,
    name: None | str | Unset = UNSET,
    description: None | str | Unset = UNSET,
    list_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_name: None | str | Unset
    if isinstance(name, Unset):
        json_name = UNSET
    else:
        json_name = name
    params["name"] = json_name

    json_description: None | str | Unset
    if isinstance(description, Unset):
        json_description = UNSET
    else:
        json_description = description
    params["description"] = json_description

    json_list_id: None | str | Unset
    if isinstance(list_id, Unset):
        json_list_id = UNSET
    else:
        json_list_id = list_id
    params["list_id"] = json_list_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/cards/{card_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | TrelloCard | None:
    if response.status_code == 200:
        response_200 = TrelloCard.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | TrelloCard]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    card_id: str,
    *,
    client: AuthenticatedClient | Client,
    name: None | str | Unset = UNSET,
    description: None | str | Unset = UNSET,
    list_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | TrelloCard]:
    """Update Card

     Update an existing card.

    Args:
        card_id (str):
        name (None | str | Unset):
        description (None | str | Unset):
        list_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | TrelloCard]
    """

    kwargs = _get_kwargs(
        card_id=card_id,
        name=name,
        description=description,
        list_id=list_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    card_id: str,
    *,
    client: AuthenticatedClient | Client,
    name: None | str | Unset = UNSET,
    description: None | str | Unset = UNSET,
    list_id: None | str | Unset = UNSET,
) -> HTTPValidationError | TrelloCard | None:
    """Update Card

     Update an existing card.

    Args:
        card_id (str):
        name (None | str | Unset):
        description (None | str | Unset):
        list_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | TrelloCard
    """

    return sync_detailed(
        card_id=card_id,
        client=client,
        name=name,
        description=description,
        list_id=list_id,
    ).parsed


async def asyncio_detailed(
    card_id: str,
    *,
    client: AuthenticatedClient | Client,
    name: None | str | Unset = UNSET,
    description: None | str | Unset = UNSET,
    list_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | TrelloCard]:
    """Update Card

     Update an existing card.

    Args:
        card_id (str):
        name (None | str | Unset):
        description (None | str | Unset):
        list_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | TrelloCard]
    """

    kwargs = _get_kwargs(
        card_id=card_id,
        name=name,
        description=description,
        list_id=list_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    card_id: str,
    *,
    client: AuthenticatedClient | Client,
    name: None | str | Unset = UNSET,
    description: None | str | Unset = UNSET,
    list_id: None | str | Unset = UNSET,
) -> HTTPValidationError | TrelloCard | None:
    """Update Card

     Update an existing card.

    Args:
        card_id (str):
        name (None | str | Unset):
        description (None | str | Unset):
        list_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | TrelloCard
    """

    return (
        await asyncio_detailed(
            card_id=card_id,
            client=client,
            name=name,
            description=description,
            list_id=list_id,
        )
    ).parsed
