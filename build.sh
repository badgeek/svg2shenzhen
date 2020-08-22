#!/usr/bin/env bash
# Creates distribution archives.
# Requires the binaries be already built (with make)
# and moved to the stageing area.

# Exit immediately on each error and unset variable;
# see: https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
#set -Eeuo pipefail
set -Eeu

# shellcheck source=./
script_dir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
root="$script_dir"
cwd="$(pwd)"

BUILD_DIR=dist

BUILD_DIR_STAGING=staging

GIT_TAG_VERSION="$(git describe --tag)"

RELEASE_FILENAME_PREFIX=svg2shenzhen-extension
# echo "$root/$BUILD_DIR/$BUILD_DIR_STAGING"
RELEASE_FILENAME_BASE="${root:?}/$BUILD_DIR/${RELEASE_FILENAME_PREFIX}-${GIT_TAG_VERSION}"

rm -fr "${root:?}/$BUILD_DIR/"*

mkdir -p "${root:?}/$BUILD_DIR/$BUILD_DIR_STAGING"

cp -r inkscape/* "${root:?}/$BUILD_DIR/$BUILD_DIR_STAGING"

find "${root:?}/$BUILD_DIR/$BUILD_DIR_STAGING" \
	-name "*.inx" \
	-type f \
	-exec sed -i.bak "s/SVGSZ_VER/${GIT_TAG_VERSION}/g" '{}' \;

rm -fr "${root:?}/$BUILD_DIR/$BUILD_DIR_STAGING/"*.bak

cd "${root:?}/$BUILD_DIR/$BUILD_DIR_STAGING"

tar -czvf "${RELEASE_FILENAME_BASE}.tar.gz" .
zip -m -x .DS_Store -r "${RELEASE_FILENAME_BASE}.zip" .

cd "$cwd"

ls "$BUILD_DIR"
