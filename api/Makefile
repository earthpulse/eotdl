build:
	sed -i 's/^VERSION = .*/VERSION = "$(v)"/' api/main.py
	docker build -t eotdl/api:${v} .

publish:
	docker push eotdl/api:${v}