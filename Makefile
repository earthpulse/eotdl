build:
	sed -i 's/^VERSION = .*/VERSION = "$(v)"/' api/api/main.py
	docker build -t eotdl/api:${v} ./api

push:
	docker push eotdl/api:${v}

cli:
	sed -i 's/^version = .*/version = "$(v)"/' eotdl/pyproject.toml
	sed -i 's/__version__ = '.*'/__version__ = "${v}"/' eotdl/eotdl/__init__.py
	cd eotdl && poetry build

publish:
	cd eotdl && poetry publish
	# export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring

