VPATH = doc
latex = pdflatex -recorder
all: handbook
handbook: handbook.pdf
docu: aclpub-setup.pdf chbk-howto.pdf

#doc/aclpub-setup.dvi:
#	${MAKE} -C doc -f ../Makefile aclpub-setup.pdf

aclpub-setup.dvi: doc/aclpub-setup.tex
	latex doc/$*
	(grep -i 'rerun' $*.log && ${latex} doc/$*) || echo -n ''

chbk-howto.dvi: doc/chbk-howto.tex
	latex doc/$*
	(grep -i 'rerun' $*.log && ${latex} doc/$*) || echo -n ''

%.pdf: %.ps
	@echo "No need to run 'ps2pdf $<'"

%.ps: %.dvi
	@echo "No need to run 'dvips $< -o $@ -t'"

%.dvi:
	if [ -e $*.idx ]; then scripts/fix-index.perl < $*.idx > $*.idx.fixed && makeindex $*.idx.fixed -o $*.ind && ${latex} $*; fi
	(grep 'Rerun to get cross-references right.' $*.log && ${latex} $*) || echo -n ''

%.log: %.tex
	${latex} $*

%.dep: %.fls
	grep INPUT $< | perl -pe "s/INPUT /$*.dvi: /" > $@
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
