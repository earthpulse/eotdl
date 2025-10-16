FROM ghcr.io/astral-sh/uv:0.6.17-python3.12-bookworm-slim

RUN uv venv

COPY requirements.txt requirements.txt

RUN uv pip install --no-cache-dir -r requirements.txt

COPY server.py server.py

CMD ["uv", "run", "server.py", "--host", "0.0.0.0", "--port", "8000"]