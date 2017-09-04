file=$1

# Set the path to the LU MII Tagger
LUMII_tagger=path/to/lumii_tagger

# convert input to conll format
cat $file | sed 's/$/\n/g' | tr ' ' '\n' | python3 utils/raw2conll.py > $file.conll
# input tagging
cat $file.conll | java -jar $LUMII_tagger/tagger-1.0.0-jar-with-dependencies.jar -conll-in > $file.tagged 2> /dev/null
# get lemmas and tags
cat $file.tagged | python3 utils/get_tags_lv.py | grep -v '^$' > $file.tag
rm $file.conll $file.tagged
