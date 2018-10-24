#!/bin/bash
cwd=$(pwd)
BUILD_DIR=dist
GIT_TAG_VERSION=`git describe --tag`
mkdir -p $cwd/$BUILD_DIR
rm -fr $cwd/$BUILD_DIR/*
cp -r inkscape/* $cwd/$BUILD_DIR
find $cwd/$BUILD_DIR -name *.inx -type f -exec sed -i.bak s/SVGSZ_VER/${GIT_TAG_VERSION}/g '{}' \;
rm -fr $cwd/$BUILD_DIR/*.bak
