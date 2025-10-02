from fastapi import FastAPI

# Trigger dependency injection.
import gmail_client_impl  # noqa: F401
import mail_client_api


app = FastAPI()
