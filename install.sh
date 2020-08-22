#!/usr/bin/env bash
# Builds and installs the plugin
# into the local Inkscape extensions directory.
# NOTE Linux only! (so far)

# Exit immediately on each error and unset variable;
# see: https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
#set -Eeuo pipefail
set -Eeu

# shellcheck source=./
script_dir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
root="$script_dir"
cwd="$(pwd)"

EXT_DIR="$HOME/.config/inkscape/extensions/"

# setup
cd "${root:?}"

# build
make

# install
mkdir -p "$EXT_DIR"
cp -pr inkscape/* "$EXT_DIR/"
cp -p bitmap2component "$EXT_DIR/svg2shenzhen/bitmap2component_linux64"

# status report
cd "$EXT_DIR"
echo
echo "Installed plugin files:"
ls -lar ./*svg2shenzhen*

# cleanup
cd "$cwd"
echo
echo "done."
