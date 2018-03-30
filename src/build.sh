rm -fr *.o
g++ -c ../common/geometry/*  -lpotrace -L. -L../potrace  -I../include -I../polygon -I../potrace -I. -v -std=c++11 
g++ -c ../common/math/*  -lpotrace -L. -L../potrace  -I../include -I../polygon -I../potrace -I. -v -std=c++11 
g++ -c ../polygon/*  -lpotrace -L. -L../potrace  -I../include -I../polygon -I../potrace -I. -v -std=c++11 
g++ -c main.cpp bitmap2component.cpp lodepng.cpp -lpotrace -L. -L../potrace  -I../include -I../polygon -I../potrace -I. -L ../common/  -I ../common/ -std=c++11 
g++ -o bitmap2component *.o -lpotrace -L. -L../potrace  -I../include -I../polygon -I../potrace -I. -L ../common/  -I ../common/ -std=c++11 
