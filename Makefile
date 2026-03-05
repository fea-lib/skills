-include .env
export

.PHONY: opencode

opencode:
	-lsof -ti :$(OPENCODE_PORT) | xargs kill -9 2>/dev/null; sleep 1
	opencode web --port $(OPENCODE_PORT) --mdns --cors https://$(TAILSCALE_HOSTNAME) &
	until curl -s http://localhost:$(OPENCODE_PORT) > /dev/null 2>&1; do sleep 1; done
	caffeinate -s tailscale serve http://localhost:$(OPENCODE_PORT)