CXX=g++
CXXFLAGS=-std=c++11
INCLUDES=-Iinclude -Ipolygon -Ipotrace -Isrc -IC:\MinGW\include
LIBS=

SOURCES:=\
	common/geometry/seg.cpp \
	common/geometry/shape_collisions.cpp \
	common/geometry/shape.cpp \
	common/geometry/shape_line_chain.cpp \
	common/geometry/shape_poly_set.cpp \
	common/math/math_util.cpp \
	polygon/clipper.cpp \
	src/main.cpp \
	src/bitmap2component.cpp \
	src/lodepng.cpp \
	potrace/curve.cpp \
	potrace/decompose.cpp \
	potrace/potracelib.cpp \
	potrace/trace.cpp
OBJECTS:=$(patsubst %.cpp,%.o,$(SOURCES))

ifneq ($(OS),Windows_NT)
	OS:=$(shell uname)
endif
ifeq ($(OS), Windows_NT)
	EXESUFFIX=.exe
endif

BITMAP2COMPONENT:=bitmap2component$(EXESUFFIX)
GIT_TAG_VERSION=$(shell git describe --tag)
RELEASE_FILENAME_PREFIX=svg2shenzhen-extension
DIST:=$(RELEASE_FILENAME_PREFIX)-$(GIT_TAG_VERSION).zip

.PHONY: clean all package

all: $(BITMAP2COMPONENT)

package: $(DIST)

clean:
	rm -f *.o common/geometry/*.p common/math/*.o polygon/*.o src/*.o potrace/*.o $(BITMAP2COMPONENT) $(DIST)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $^ -o $@

$(BITMAP2COMPONENT): $(OBJECTS)
	$(CXX) $(LIBS) $^ -o $@

$(DIST):
	zip $@ inkscape/svg2shenzhen/
	sed s/SVGSZ_VER/${GIT_TAG_VERSION}/g < inkscape/svg2shenzhen_about.inx | zip -q $@ -
	/bin/echo -e '@ -\n@=inkscape/svg2shenzhen_about.inx' | zipnote -w $@
	sed s/SVGSZ_VER/${GIT_TAG_VERSION}/g < inkscape/svg2shenzhen_export.inx | zip -q $@ -
	/bin/echo -e '@ -\n@=inkscape/svg2shenzhen_export.inx' | zipnote -w $@
	sed s/SVGSZ_VER/${GIT_TAG_VERSION}/g < inkscape/svg2shenzhen_prepare.inx | zip -q $@ -
	/bin/echo -e '@ -\n@=inkscape/svg2shenzhen_prepare.inx' | zipnote -w $@
