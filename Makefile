run:
	docker compose up

build:
	@if [ "$$(uname -s)" = "Darwin" ]; then \
		sed -i '' 's/^VERSION = .*/VERSION = "$(v)"/' api/api/config.py; \
		docker build --platform linux/amd64 -t eotdl/api:${v} ./api; \
	else \
		sed -i 's/^VERSION = .*/VERSION = "$(v)"/' api/api/config.py; \
		docker build -t eotdl/api:${v} ./api; \
	fi
	
push:
	docker push eotdl/api:${v}

cli:
	rm -rf eotdl/dist
	# linux
	sed -i 's/^version = .*/version = "$(v)"/' eotdl/pyproject.toml
	sed -i 's/__version__ = '.*'/__version__ = "${v}"/' eotdl/eotdl/__init__.py
	# mac
	# sed -i '' 's/^version = .*/version = "$(v)"/' eotdl/pyproject.toml
	# sed -i '' 's/__version__ = '.*'/__version__ = "${v}"/' eotdl/eotdl/__init__.py
	cd eotdl && uv build

publish:
	cd eotdl && uv publish --username "__token__" --password "$(token)"
	# export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring

test:
	@if [ "$$(uname -s)" = "Darwin" ]; then \
		USER_IP=$$(ipconfig getifaddr en0 2>/dev/null); \
	else \
		USER_IP=$$(ip -4 addr show scope global | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n 1); \
	fi; \
	echo "Using IP: $$USER_IP"; \
	export S3_ENDPOINT=$$USER_IP:9000; \
	docker-compose -f docker-compose.test.yml up 

.PHONY: mcp
mcp:
	docker compose -f docker-compose.mcp.yml up

test-mcp:
	npx @modelcontextprotocol/inspector http://localhost:8001

build-mcp:
	if [ "$$(uname -s)" = "Darwin" ]; then \
		docker build --platform linux/amd64 -t eotdl/mcp:${v} ./mcp; \
	else \
		docker build -t eotdl/mcp:${v} ./mcp; \
	fi

push-mcp:
	docker push eotdl/mcp:${v}