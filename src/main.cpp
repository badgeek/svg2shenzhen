#include <bitmap2component.h>
#include <bitmap.h>

#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>

#include "lodepng.h"

#include <bitmap.h>


extern int bitmap2component( potrace_bitmap_t* aPotrace_bitmap, FILE* aOutfile,
                             OUTPUT_FMT_ID aFormat, int aDpi_X, int aDpi_Y,
                             BMP2CMP_MOD_LAYER aModLayer );


int main()
{   
    FILE * pFile;
    pFile = fopen ("myfile.txt","w");

	std::vector<unsigned char> image; //the raw pixels
	unsigned width, height;
	//decode
	unsigned error = lodepng::decode(image, width, height, "test.png");


	// //if there's an error, display it
	// if(error) {
    //     std::cout << "decoder error " << error << ": " << lodepng_error_text(error) << std::endl;
    // }else{
    //     printf("load png s: %i x %i\n", width, height);
    // }
	
    return 1;
   printf("create bitmap");

    potrace_bitmap_t* potrace_bitmap = bm_new( width, height );


   printf("fill bitmap");
     
    /* fill the bitmap with data */
    for( int y = 0; y < width; y++ )
    {
        for( int x = 0; x < height; x++ )
        {
            int start = (y * height * 4) + x * 4;
            unsigned char pix = image[start+1];

            //grayscale
            // unsigned char pix = (image[start+0] * 0.2126 + image[start+1] * 0.7152 + image[start+2] * 0.0722);

            //treshold 128
            // if( pix < 128 )
            //     pix = 0;
            // else
            //     pix = 255;

            //invert image
            // pix = 255-pix;

            BM_PUT( potrace_bitmap, x, y, pix ? 1 : 0 );
        }
        // printf("\n");
    }

   printf("gotobitmap2comp");

	
	//the pixels are now in the vector "image", 4 bytes per pixel, ordered RGBARGBA..., use it as texture, draw it, ...

    bitmap2component( potrace_bitmap, pFile, PCBNEW_KICAD_MOD, 52.9, 65.4, MOD_LYR_ECO1 );
    fclose( pFile );

    return 0;
}