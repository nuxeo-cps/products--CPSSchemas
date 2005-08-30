.PHONY: clean check

check:
	pylint *.py

clean:
	find . "(" -name "*~" -or -name "*.pyc" ")" -print0 | xargs -0 rm -f

