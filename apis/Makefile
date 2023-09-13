build:
	sed -i 's/^VERSION = .*/VERSION = "$(v)"/' eotdl/main.py
	docker build -t eotdl/api:${v} -f Dockerfile.api .

publish:
	docker push eotdl/api:${v}