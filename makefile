# Define the virtual environment directory
VENV_COMMAND = conda activate easy-storage

# Tailwind CSS command
TAILWIND_CMD = twind -i static/css/input.css -o static/css/main.min.css --watch --minify
# TMUX session name
TMUX_SESSION = dev_session

# Default target
.PHONY: all
all: run

# Target to activate the virtual environment, run Django server, and TailwindCSS in tmux
.PHONY: run
run:
	@echo "Starting tmux session..."
	@tmux new-session -d -s $(TMUX_SESSION) \; \
	send-keys "$(VENV_COMMAND) && python manage.py runserver" C-m \; \
	split-window -h \; \
	send-keys "$(TAILWIND_CMD)" C-m \; \
	select-pane -t 0 \; \
	attach

# Target to clean up the tmux session
.PHONY: clean
clean:
	@echo "Killing tmux session..."
	@tmux kill-session -t $(TMUX_SESSION) || true

