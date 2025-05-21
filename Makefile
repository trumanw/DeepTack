.PHONY: clean run
clean:
	find . -type d -name __pycache__ -exec rm -r {} \+
	rm -rf dist build

run: clean
	streamlit run Overview.py