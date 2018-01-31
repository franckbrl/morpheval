# morpheval

Evaluation of the morphological quality of machine translation outputs.
The automatically generated test suite in English should be translated
into Czech or Latvian. The output is then analyzed and provides three
types of information:

* Adequacy: has the morphological information been well conveyed from the source?
* Fluency: do we have local agreement?
* Consistency: how well is the system confident in its prediction?

More details [here](http://www.statmt.org/wmt17/pdf/WMT05.pdf).

## Requirements

* Python 3
* Download the [test suite](https://morpheval.limsi.fr/) (version 1) and put it in the main directory.
* [Morphodita](https://github.com/ufal/morphodita/releases/tag/v1.3.0) version 1.3 for Czech, as well as the [tagging model and dictionary](https://lindat.mff.cuni.cz/repository/xmlui/handle/11858/00-097C-0000-0023-68D8-1)
* [LU MII Tagger](https://peteris.rocks/blog/latvian-part-of-speech-tagging/#lu-mii-tagger) for Latvian
* [Moses tokenizer]( https://github.com/moses-smt/mosesdecoder/blob/master/scripts/tokenizer)
* Download our [Latvian dictionary](https://morpheval.limsi.fr/) and put it in utils/

## How To

Use your MT system to translate the source file `morph_test_suite_limsi.en` (untokenized).
The next steps assume that the outputs are tokenized with [Moses tokenizer]( https://github.com/moses-smt/mosesdecoder/blob/master/scripts/tokenizer) (use English tokenization for Latvian).

### Czech

* Adequacy and fluency:
	* Run analysis:<br>
`cat morph_test_suite_limsi.translated.cs | sed  's/$/\n/' | tr ' ' '\n' | morphodita/src/run_morpho_analyze czech-morfflex-131112-raw_lemmas.dict 1 --input=vertical --output=vertical > morph_test_suite_limsi.translated.cs.ambig`
	* Run evaluation:<br>
`python3 evaluate_morph_pairs_cs.py -i morph_test_suite_limsi.translated.cs.ambig -n morph_test_suite_limsi.en.info`

* Consistency:
	* Run tagging:<br>
`cat morph_test_suite_limsi.translated.cs | sed  's/$/\n/' | tr ' ' '\n' | morphodita/src/run_tagger czech-morfflex-pdt-131112-raw_lemmas.tagger-best_accuracy --input=vertical --output=vertical > morph_test_suite_limsi.translated.cs.disambig`
	* Run evaluation:<br>
`python3 evaluate_consistency_cs.py -i morph_test_suite_limsi.translated.cs.disambig -n morph_test_suite_limsi.en.info`

### Latvian

* Set the path to LU MII Tagger in `tags_lv.sh` and run tagging (outputs `morph_test_suite_limsi.translated.lv.tag`):<br>
`./tags_lv.sh morph_test_suite_limsi.translated.lv`

* Adequacy and fluency:
	* Generate ambiguities (analysis) with the dictionary:<br>
` python3 make_ambig_lv.py -w morph_test_suite_limsi.translated.lv -t morph_test_suite_limsi.translated.lv.tag > morph_test_suite_limsi.translated.lv.tag.ambig`
	* Run evaluation:<br>
`python3 evaluate_morph_pairs_lv.py -i morph_test_suite_limsi.translated.lv.tag.ambig -n morph_test_suite_limsi.en.info`

* Consistency:
	* Format output:<br>
`python3 make_disambig_vert.py -w  morph_test_suite_limsi.translated.lv -t morph_test_suite_limsi.translated.lv.tag > morph_test_suite_limsi.translated.lv.tag.disambig`
	* Run evaluation:<br>
`python3 evaluate_consistency_lv.py -i morph_test_suite_limsi.translated.lv.tag.disambig -n morph_test_suite_limsi.en.info`

## Publication

Franck Burlot and François Yvon, [Evaluating the morphological competence of machine translation systems](http://www.statmt.org/wmt17/pdf/WMT05.pdf). In Proceedings of the Second Conference on Machine Translation (WMT’17). Association for Computational Linguistics, Copenhagen, Denmark, 2017.
