all:
	export QT_QPA_PLATFORM=wayland
	python3 euph.py
	pdflatex -file-line-error main.tex
	evince main.pdf
