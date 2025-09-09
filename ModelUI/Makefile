# Variables
VENV=venv
ACTIVATE=$(VENV)/Scripts/activate
PYTHON=python
MAIN_FILE=__main__.py
PORT=5000

# Commands
.PHONY: all setup run clean

# Set up the virtual environment and install dependencies
setup:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && $(PYTHON) -m pip install -r requirements.txt

# Run the Flask server
run:
	$(ACTIVATE) && $(PYTHON) $(MAIN_FILE)

# Clean up the virtual environment
clean:
	rm -rf $(VENV)
