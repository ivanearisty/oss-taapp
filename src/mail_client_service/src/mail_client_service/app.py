from fastapi import FastAPI

# Ensure Gmail implementation registers itself with the API factory via import side effects
import gmail_client_impl  # noqa: F401
import mail_client_api


app = FastAPI()


@app.on_event("startup")
def initialize_client() -> None:
    """Obtain a client instance from the factory.

    This ensures the Gmail implementation is registered and can be constructed.
    No application logic is re-implemented here.
    """

    # We call the factory to ensure instantiation works; we do not retain the instance
    mail_client_api.get_client(interactive=False)


