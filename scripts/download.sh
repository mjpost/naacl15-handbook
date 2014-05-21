for x in papers shortpapers srw tutorials demos WMT14 BioNLP BEA9 SLPAT14 CMCL ArgMin ComputEL Metaphor SP14 LTCSS WASSA EntitySM NLPSD MORPHFSM EVENTS fsnlp LLVisInt CLPsych CoNLL2014; do
  [[ ! -d "data/$x" ]] && mkdir -p data/$x
  cd data/$x
  wget -N --no-check-certificate https://www.softconf.com/acl2014/$x/manager/aclpub/proceedings.tgz
  cd -
done
