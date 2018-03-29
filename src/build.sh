rm -fr *.o
g++ -c ../common/geometry/*  -lpotrace -L. -L../potrace  -I../include -I../polygon -I../potrace -I. -v
g++ -c ../common/math/*  -lpotrace -L. -L../potrace  -I../include -I../polygon -I../potrace -I. -v
g++ -c ../polygon/*  -lpotrace -L. -L../potrace  -I../include -I../polygon -I../potrace -I. -v
g++ -c main.cpp bitmap2component.cpp lodepng.cpp -lpotrace -L. -L../potrace  -I../include -I../polygon -I../potrace -I. -L ../common/  -I ../common/
g++ -o bitmap2component *.o -lpotrace -L. -L../potrace  -I../include -I../polygon -I../potrace -I. -L ../common/  -I ../common/
