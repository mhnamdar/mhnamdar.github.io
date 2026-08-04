.PHONY: build dev check clean

build:
	python3 scripts/build.py

dev:
	python3 scripts/dev.py

check:
	python3 scripts/check.py

clean:
	rm -rf dist
