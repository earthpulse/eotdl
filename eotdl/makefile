build:
	sed -i 's/^version = .*/version = "$(v)"/' pyproject.toml
	sed -i 's/__version__ = '.*'/__version__ = "${v}"/' eotdl/__init__.py
	poetry build

publish:
	poetry publish

