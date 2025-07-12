# $(patsubst pattern,replacement,text)
# 	Finds whitespace-separated words in text that match pattern and replaces them with replacement.
# $(wildcard *.ui)
#	List all .ui files
PYFILES := $(patsubst %.ui, %.py, $(wildcard *.ui))
$(info $$PYFILES is [${PYFILES}])

all: __init__.py $(PYFILES)

__init__.py:
	touch $@

# generate .py files from .ui files
%.py: %.ui
	pyside6-uic $< -o $@

.PYONY: clean
clean:
	rm -f $(PYFILES)

