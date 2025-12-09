install-uv:
	@if [ "$(shell which uv)" = "" ]; then \
		if [ "$(shell which rustup)" = "" ]; then \
			curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y; \
			echo "Installed Rust."; \
		fi; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "Installed uv."; \
    else \
		echo "Updating uv..."; \
		uv self update || true; \
	fi
