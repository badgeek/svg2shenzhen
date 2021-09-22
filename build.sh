#!/bin/bash

cwd=$(pwd)

BUILD_DIR=dist

BUILD_DIR_STAGING=staging

GIT_TAG_VERSION=`git describe --tag`

RELEASE_FILENAME_PREFIX=svg2shenzhen-extension
# echo "$cwd/$BUILD_DIR/$BUILD_DIR_STAGING"

rm -fr $cwd/$BUILD_DIR/*

mkdir -p "$cwd/$BUILD_DIR/$BUILD_DIR_STAGING"

cp -r inkscape/* $cwd/$BUILD_DIR/$BUILD_DIR_STAGING

find $cwd/$BUILD_DIR/$BUILD_DIR_STAGING -name *.inx -type f -exec sed -i.bak s/SVGSZ_VER/${GIT_TAG_VERSION}/g '{}' \;

rm -fr $cwd/$BUILD_DIR/$BUILD_DIR_STAGING/*.bak

cd $cwd/$BUILD_DIR/$BUILD_DIR_STAGING

tar -czvf $cwd/$BUILD_DIR/${RELEASE_FILENAME_PREFIX}-${GIT_TAG_VERSION}.tar.gz .
zip -m -x .DS_Store -r $cwd/$BUILD_DIR/${RELEASE_FILENAME_PREFIX}-${GIT_TAG_VERSION}.zip .

cd $cwd

ls dist