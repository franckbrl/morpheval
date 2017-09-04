# morpheval

Evaluation of the morphological quality of machine translation outputs.
The automatically generated test suite in English should be translated
into Czech or Latvian. The output is then analyzed and provide three
types of information:

* Adequacy: has the morphological information been well conveyed from the source?
* Fluency: do we have local agreement?
* Consistency: how well is the system confident in its prediction?

## Requirements

* Python 3
* Download the [test suite](https://ocsync.limsi.fr/index.php/s/br2eCuzvIzkFrPW) and put it in the main directory.
* [Morphodita](https://github.com/ufal/morphodita/releases/tag/v1.3.0) version 1.3 for Czech, as well as the [tagging model and dictionaries](https://lindat.mff.cuni.cz/repository/xmlui/handle/11858/00-097C-0000-0023-68D8-1)
* [LU MII Tagger](https://peteris.rocks/blog/latvian-part-of-speech-tagging/#lu-mii-tagger) for Latvian
* [Moses tokenizer]( https://github.com/moses-smt/mosesdecoder/blob/master/scripts/tokenizer)
* Download our [Latvian dictionary](https://ocsync.limsi.fr/index.php/s/LsfjCDpmSFSKp71) and put it in utils/

## Usage

Use your MT system to translate the source file `test_suite/morph_test_suite_limsi.en` (untokenized).
The next steps assume that the outputs are tokenized with [Moses tokenizer]( https://github.com/moses-smt/mosesdecoder/blob/master/scripts/tokenizer).

### Czech

* Adequacy and fluency:
** Run analysis:
`cat morph_test_suite_limsi.translated.cs | sed  's/$/\n/' | tr ' ' '\n' | morphodita/src/run_morpho_analyze czech-morfflex-131112-raw_lemmas.dict 1 --input=vertical --output=vertical > morph_test_suite_limsi.translated.cs.ambig`
** Run evaluation:
`python3 evaluate_morph_pairs_cs.py -i morph_test_suite_limsi.translated.cs.ambig -n morph_test_suite_limsi.en.info`

* Consistency:
** Run tagging:
`cat morph_test_suite_limsi.translated.cs | sed  's/$/\n/' | tr ' ' '\n' | morphodita/src/run_tagger czech-morfflex-pdt-131112-raw_lemmas.tagger-best_accuracy --input=vertical --output=vertical > morph_test_suite_limsi.translated.cs.disambig`
* Run evaluation:
`python3 evaluate_consistency_cs.py -i morph_test_suite_limsi.translated.cs.disambig -n morph_test_suite_limsi.en.info`

### Latvian

* Run tagging (outputs `morph_test_suite_limsi.translated.lv.tag`):
`./tags_lv.sh morph_test_suite_limsi.translated.lv`

* Adequacy and fluency:
** Generate ambiguities (analysis) with the dictionary:
` python3 make_ambig_lv.py -w morph_test_suite_limsi.translated.lv -t morph_test_suite_limsi.translated.lv.tag > morph_test_suite_limsi.translated.lv.tag.ambig`
** Run evaluation:
`python3 evaluate_morph_pairs_lv.py -i morph_test_suite_limsi.translated.lv.tag.ambig -n morph_test_suite_limsi.en.info`

* Consistency:
** Format output:
`python3 make_disambig_vert.py -w  morph_test_suite_limsi.translated.lv -t morph_test_suite_limsi.translated.lv.tag > morph_test_suite_limsi.translated.lv.tag.disambig`
** Run evaluation:
`python3 evaluate_consistency_lv.py -i morph_test_suite_limsi.translated.lv.tag.disambig -n morph_test_suite_limsi.en.info`
