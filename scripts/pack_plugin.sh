#!/usr/bin/env bash
set -euo pipefail

DIST_NAME="qgis-inaturalist-api"

mkdir -p $DIST_NAME

cp *.py $DIST_NAME &&
cp -r icons $DIST_NAME &&
cp -r ui $DIST_NAME &&
cp -r vendor $DIST_NAME &&
cp icon.png $DIST_NAME &&
cp metadata.txt $DIST_NAME &&
cp LICENSE $DIST_NAME &&
cp README.md $DIST_NAME &&

zip -r "${DIST_NAME}.zip" "$DIST_NAME"/* &&

rm -rf "$DIST_NAME" &&

echo "Plugin packaged successfully: ${DIST_NAME}.zip"
