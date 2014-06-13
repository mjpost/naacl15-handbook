# $@ the target
# $* the matched prefix
# $< the matched dependent

# -recorder records the files opened in a file with a .fls extension. This is used to infer
# the list of file dependencies.

latex = pdflatex -recorder

all: handbook.pdf

# pdflatex
# build dep file
# biber
# pdflatex
# fix index
# makeindex
# pdflatex
# pdflatex

%.pdf: handbook.tex
	${latex} handbook
	grep INPUT $< | perl -pe "s/INPUT /$*.dvi: /" > handbook.dep
	${latex} handbook

%.dvi:
	if [ -e $*.idx ]; then scripts/fix-index.perl < $*.idx > $*.idx.fixed && makeindex $*.idx.fixed -o $*.ind && ${latex} $*; fi
	(grep 'Rerun to get cross-references right.' $*.log && ${latex} $*) || echo -n ''

%.log: %.tex
	${latex} $*

# Produce a list of file dependencies by looking for INPUT lines in the .fls file
# (written from the first call to pdflatex because of the -recorder option)
%.dep: %.fls
	(grep 'run BibTeX on the file' $*.log && echo "$*.dvi: $*.bbl" >> $@) || echo -n ''

%.fls: %.tex
	${latex} $<
	rm -f $*.dvi
	biber $*
	${latex} $*

EXTENSIONS  = .ilg .ps .dvi .dep .idx .idx.fixed .ind .aux .idx.ilg
EXTENSIONS += .bbl .blg .bcf .toc .fls .log -blx.bib .run.xml .out

clean: 
	rm -f $(addprefix handbook, ${EXTENSIONS})

-include handbook.dep

.SECONDARY:
