build:
	# linux
	# sed -i 's/^VERSION = .*/VERSION = "$(v)"/' api/api/main.py
	# docker build -t eotdl/api:${v} ./api
	# mac
	sed -i '' 's/^VERSION = .*/VERSION = "$(v)"/' api/api/main.py
	docker build --platform linux/amd64 -t eotdl/api:${v} ./api
	
push:
	docker push eotdl/api:${v}

cli:
	rm -rf dist
	# linux
	# sed -i 's/^version = .*/version = "$(v)"/' eotdl/pyproject.toml
	# sed -i 's/__version__ = '.*'/__version__ = "${v}"/' eotdl/eotdl/__init__.py
	# mac
	sed -i '' 's/^version = .*/version = "$(v)"/' eotdl/pyproject.toml
	sed -i '' 's/__version__ = '.*'/__version__ = "${v}"/' eotdl/eotdl/__init__.py
	cd eotdl && uv build

publish:
	uv publish --username "__token__" --password "$(token)"
	# export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring

