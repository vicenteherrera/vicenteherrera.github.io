.PHONY: run

PORT ?= 8888

run:
	python3 server.py $(PORT)

