all:
	python3 euph.py
	pdflatex -file-line-error main.tex
	evince main.pdf
