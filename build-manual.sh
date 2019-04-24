#! /bin/bash
# clones the dialogos wiki and builds a manual from it.
# needs pandoc.
# Author: Arne Köhn <arne@chark.eu>

mkdir -p documentation
cd documentation
if [[ -e wiki ]]; then
	cd wiki
	git pull
else
	git clone https://github.com/dialogos-project/dialogos.wiki.git wiki
	cd wiki
fi

for n in Manual Handbuch;do
	rm -f ../$n.md ../$n.pdf
	# grep for list of topics in the manual, strip wikilinks & link description, add .md
	grep "^[0-9][0-9]*\." $n.md | \
		sed 's/.*\[\[\(.*\)\]\]/\1/; s/.*|//; s/$/.md/' | \
		xargs cat | \
		grep -v "^\[\[(this page in" | \
		grep -v "^\[\[(diese Seite auf" > ../$n.md
	pandoc ../$n.md -o ../$n.pdf
done
