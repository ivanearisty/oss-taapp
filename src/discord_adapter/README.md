# Discord Adapter

Adapter package that implements the `chat_client_api.ChatClient` interface by calling the
`discord_client_service_api_client` generated client which talks to the running `discord_service`.

This mirrors the approach used by `service_client_adapter` for the mail service.

Usage example:

```
from discord_adapter.main import DiscordAdapter

adapter = DiscordAdapter(base_url="http://127.0.0.1:8000")
# Provide an access token previously obtained via OAuth2 callback
adapter.set_token("<access-token>")
for m in adapter.get_messages(channel_id="123", max_results=10):
    print(m.content)
```

```
python3.11 - <<PY
from discord_adapter.main import DiscordAdapter
# create adapter pointing at running service
adapter = DiscordAdapter(base_url="http://127.0.0.1:8000")
print("adapter ready:", adapter)
# If you have a token:
# adapter.set_token("<ACCESS_TOKEN>")
PY
```
