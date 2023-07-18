build:
	sed -i 's/^version = .*/version = "$(v)"/' pyproject.toml
	sed -i 's/__version__ = '.*'/__version__ = "${v}"/' main.py
	poetry build

publish:
	poetry publish