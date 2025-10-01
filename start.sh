# Remove and sync all new potential dependencies
rm -rf .venv
uv sync --all-packages --extra dev
sleep 2
source .venv/bin/activate

# Start the fastapi server
fastapi dev src/mail_client_service/src/mail_client_service/main.py