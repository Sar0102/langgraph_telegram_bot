# Lang Graph Telegram Bot

## Run locally

1. Copy `.env_example` to `.env` and fill the required keys.
2. Install the project:

```bash
pip install .
telegram-agent
```

## Docker

```bash
docker build -t lang-graph-telegram-bot .
docker run --env-file .env -v ${PWD}/data:/app/data lang-graph-telegram-bot
```
