#!/bin/sh
# me@msms.cf
mkdir -p ./backups
pushd ./_tools #need to be run from this folder
python ./_generate_repo.py
popd #return back to main folder
mv ./_repo/**/*.zip.* ./backups > /dev/null
