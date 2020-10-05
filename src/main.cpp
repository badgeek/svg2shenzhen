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
                             BMP2CMP_MOD_LAYER aModLayer, const char * layer_name = NULL,
			     bool center = true, bool createPad = false );


string pcb_header = "(kicad_pcb (version 4) (host pcbnew 4.0.7)"
"	(general"
"		(links 0)"
"		(no_connects 0)"
"		(area 77.052499 41.877835 92.193313 53.630501)"
"		(thickness 1.6)"
"		(drawings 8)"
"		(tracks 0)"
"		(zones 0)"
"		(modules 1)"
"		(nets 1)"
"	)"
"	(page A4)"
"	(layers"
"		(0 F.Cu signal)"
"		(31 B.Cu signal)"
"		(32 B.Adhes user)"
"		(33 F.Adhes user)"
"		(34 B.Paste user)"
"		(35 F.Paste user)"
"		(36 B.SilkS user)"
"		(37 F.SilkS user)"
"		(38 B.Mask user)"
"		(39 F.Mask user)"
"		(40 Dwgs.User user)"
"		(41 Cmts.User user)"
"		(42 Eco1.User user)"
"		(43 Eco2.User user)"
"		(44 Edge.Cuts user)"
"		(45 Margin user)"
"		(46 B.CrtYd user)"
"		(47 F.CrtYd user)"
"		(48 B.Fab user)"
"		(49 F.Fab user)"
"	)"
"	(setup"
"		(last_trace_width 0.25)"
"		(trace_clearance 0.2)"
"		(zone_clearance 0.508)"
"		(zone_45_only no)"
"		(trace_min 0.2)"
"		(segment_width 0.2)"
"		(edge_width 0.15)"
"		(via_size 0.6)"
"		(via_drill 0.4)"
"		(via_min_size 0.4)"
"		(via_min_drill 0.3)"
"		(uvia_size 0.3)"
"		(uvia_drill 0.1)"
"		(uvias_allowed no)"
"		(uvia_min_size 0.2)"
"		(uvia_min_drill 0.1)"
"		(pcb_text_width 0.3)"
"		(pcb_text_size 1.5 1.5)"
"		(mod_edge_width 0.15)"
"		(mod_text_size 1 1)"
"		(mod_text_width 0.15)"
"		(pad_size 1.524 1.524)"
"		(pad_drill 0.762)"
"		(pad_to_mask_clearance 0.2)"
"		(aux_axis_origin 0 0)"
"		(visible_elements FFFFFF7F)"
"		(pcbplotparams"
"			(layerselection 0x00030_80000001)"
"			(usegerberextensions false)"
"			(excludeedgelayer true)"
"			(linewidth 0.100000)"
"			(plotframeref false)"
"			(viasonmask false)"
"			(mode 1)"
"			(useauxorigin false)"
"			(hpglpennumber 1)"
"			(hpglpenspeed 20)"
"			(hpglpendiameter 15)"
"			(hpglpenoverlay 2)"
"			(psnegative false)"
"			(psa4output false)"
"			(plotreference true)"
"			(plotvalue true)"
"			(plotinvisibletext false)"
"			(padsonsilk false)"
"			(subtractmaskfromsilk false)"
"			(outputformat 1)"
"			(mirror false)"
"			(drillshape 1)"
"			(scaleselection 1)"
"			(outputdirectory \"\"))"
"	)"
"	(net 0 \"\")"
"	(net_class Default \"This is the default net class.\""
"		(clearance 0.2)"
"		(trace_width 0.25)"
"		(via_dia 0.6)"
"		(via_drill 0.4)"
"		(uvia_dia 0.3)"
"		(uvia_drill 0.1)"
"	)\n";
		
string  pcb_footer = "\n)\n";

/*funcion that show the help information*/
void showUsage()
{
  cout<<"" << endl;
  cout<<" bitmap2component-cli "<<endl;
  cout<<"" << endl;
  cout<<" Usage"<<endl;
  cout<<" ./bitmap2component <filename.png> <output filename> <layer> <negative|true/false> <dpi> <threshold|0-255> <center|true/false> <create pads|true/false>"<<endl;
  cout<<"\n\n\n" << endl;
}

int main(int argc, char* argv[])
{   

    bool negative = false;
    int threshold = 128;
    int dpi = 600;
    string image_filename;
    string output_filename;
    bool center = true;
    bool createPad = false;


    BMP2CMP_MOD_LAYER kicad_output_layer = MOD_LYR_FCU;
    const char * layer_name = NULL;

    showUsage();

    if (argc == 1) return 0;

    image_filename = string(argv[1]);
    output_filename = string(argv[2]);
        
    if (argc > 3){
        layer_name = argv[3];
    }


    if (argc > 4){
        if (string(argv[4]) == "true" ){
            negative = true;
        }else{
            negative = false;
        }
    }

    if (argc > 5){
        dpi = stoi(string(argv[5]));
    }    

    if (argc > 6){
        threshold = stoi(string(argv[6]));
    }      

    if (argc > 7){
	if (string(argv[7]) == "true"){
		center = true;
	}else{
		center = false;
	}
    }

    if (argc > 8){
	if (string(argv[8]) == "true"){
		createPad = true;
	}else{
		createPad = false;
	}
    }

    printf("[bitmap2component] Filename %s\n", image_filename.c_str());

    FILE * pFile;
    pFile = fopen (output_filename.c_str(),"w");

	std::vector<unsigned char> image; //the raw pixels
	unsigned width, height;
	//decode

    printf("[bitmap2component] Open bitmap\n");

	unsigned error = lodepng::decode(image, width, height, image_filename.c_str());

	//if there's an error, display it
	if(error) {
        std::cout << "[bitmap2component] Decoder error " << error << ": " << lodepng_error_text(error) << std::endl;
        return -1;
    }else{
        printf("[bitmap2component] Loaded png: %i x %i\n", width, height);
    }
	
   printf("[bitmap2component] Create bitmap\n");

   potrace_bitmap_t* potrace_bitmap = bm_new( width, height );

	// the pixels are now in the vector "image", 4 bytes per pixel, ordered RGBARGBA..., use it as texture, draw it, ...

   printf("[bitmap2component] Fill bitmap\n");

    /* fill the bitmap with data */
    
    for( int y = 0; y < height; y++ )
    {
        for( int x = 0; x < width; x++ )
        {
            unsigned char pix = image[4 * width * y + 4 * x + 1];

            //transparent = white
            if ( image[4 * width * y + 4 * x + 3] == 0)
                pix = 255;

            //grayscale
            // pix = (image[start+0] * 0.2126 + image[start+1] * 0.7152 + image[start+2] * 0.0722);

            //invert image
            if (negative)
                pix = 255-pix;

            // treshold 128
            if( pix < threshold )
                pix = 0;
             else
                pix = 255;

            BM_PUT( potrace_bitmap, x, y, pix ? 1 : 0 );
        }
        // printf("\n");
    }

   printf("[bitmap2component] Trace Dpi: %i\n", dpi);
   printf("[bitmap2component] Trace image\n");

//    fprintf(pFile, pcb_header.c_str());
   bitmap2component( potrace_bitmap, pFile, PCBNEW_KICAD_MOD, dpi, dpi, kicad_output_layer, layer_name, center, createPad);
//    fprintf(pFile, pcb_footer.c_str());


   fclose( pFile );

   printf("[bitmap2component] Done\n");

}
