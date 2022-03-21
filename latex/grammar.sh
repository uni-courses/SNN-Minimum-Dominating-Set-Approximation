#!/bin/bash
echo "starting spellcheck"
shopt -s nullglob
cd chapters
for i in *.tex; do
		echo $i
		java -jar /etc/language_tool/LanguageTool-5.4-SNAPSHOT/languagetool.jar $i
done
