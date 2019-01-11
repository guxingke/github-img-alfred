#!/usr/bin/env bash

mkdir dist temp

cp icon.png temp/
cp *.py temp/

cp workflow.yml temp/

pushd temp

cat workflow.yml | yq . > info.plist
plutil -convert xml1 info.plist

zip -r temp.zip *

popd

mv temp/temp.zip dist/mga.alfredworkflow

echo 'build dist wf done.'

rm -rf temp

