#include <bitmap2component.h>
#include <bitmap.h>

#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>

#include "lodepng.h"

#include <bitmap.h>

using namespace std;

extern int bitmap2component( potrace_bitmap_t* aPotrace_bitmap, FILE* aOutfile,
                             OUTPUT_FMT_ID aFormat, int aDpi_X, int aDpi_Y,
                             BMP2CMP_MOD_LAYER aModLayer );


/*funcion that show the help information*/
void showUsage()
{
  cout<<"" << endl;
  cout<<" bitmap2component-cli "<<endl;
  cout<<"" << endl;
  cout<<" Usage"<<endl;
  cout<<" ./bitmap2component <filename.png> <output filename> <negative|true/false> <threshold|0-255>"<<endl;
  cout<<"\n\n\n" << endl;
}

int main(int argc, char* argv[])
{   

    bool negative = false;
    int threshold = 128;
    string image_filename;
    string output_filename;

    showUsage();

    image_filename = string(argv[1]);
    output_filename = string(argv[2]);
        
    if (argc > 3){
        if (string(argv[3]) == "true" ){
            negative = true;
        }else{
            negative = false;
        }
    }

    if (argc > 4){
        threshold = stoi(string(argv[4]));
    }    

    printf("[bitmap2component] filename %s\n", image_filename.c_str());

    FILE * pFile;
    pFile = fopen (output_filename.c_str(),"w");

	std::vector<unsigned char> image; //the raw pixels
	unsigned width, height;
	//decode

    printf("[bitmap2component] open bitmap\n");

	unsigned error = lodepng::decode(image, width, height, image_filename.c_str());

	//if there's an error, display it
	if(error) {
        std::cout << "[bitmap2component] decoder error " << error << ": " << lodepng_error_text(error) << std::endl;
        return -1;
    }else{
        printf("[bitmap2component] loaded png s: %i x %i\n", width, height);
    }
	
   printf("[bitmap2component] create bitmap\n");

   potrace_bitmap_t* potrace_bitmap = bm_new( width, height );

	// the pixels are now in the vector "image", 4 bytes per pixel, ordered RGBARGBA..., use it as texture, draw it, ...

   printf("[bitmap2component] fill bitmap\n");

    /* fill the bitmap with data */
    
    for( int y = 0; y < width; y++ )
    {
        for( int x = 0; x < height; x++ )
        {
            int start = (y * width * 4) + x * 4;
            unsigned char pix = image[start+1];

            //grayscale
            // pix = (image[start+0] * 0.2126 + image[start+1] * 0.7152 + image[start+2] * 0.0722);

            // treshold 128
            if( pix < threshold )
                pix = 0;
             else
                pix = 255;

            //invert image
            if (negative)
                pix = 255-pix;

            BM_PUT( potrace_bitmap, x, y, pix ? 1 : 0 );
        }
        // printf("\n");
    }

   printf("[bitmap2component] trace image\n");

   bitmap2component( potrace_bitmap, pFile, PCBNEW_KICAD_MOD, width, height, MOD_LYR_ECO1 );
   fclose( pFile );

   printf("[bitmap2component] done\n");

}