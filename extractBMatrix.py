'''
This python script extracts gradient information from the raw DICOM. Works pretty well with Simens DICOM files. It outputs two files
if runs successfully: bvals and bvecs. In most occasions(I haven't tested for all scanner types), the bvecs is the same as if it is
created from dcm2nii tool by Chris Roden as part of the installation of mricron software.
link: http://www.mccauslandcenter.sc.edu/mricro/mricron/dcm2nii.html
packages required:
    dicom
    glob
    getopt
    numpy
    struct
    sys
    os
It should work for python >=2.6 although not fully tested. You are welcome to report any problem to the author. 
Feel free to distribute and adapt but please leave this section unchanged.

'''
import dicom
import glob
import getopt
import numpy as np
from struct import unpack 
import sys
import os

def print_help():
    print '******************************************************************************'
    print 'extractBMatrix -i <inputdirectory> -o <outputdirectory> [-e <dicom extension>]'
    print '     -i: input DICOM directory. [please only run this in your DTI directory. will not chekc if this is diffusion series]'
    print '     -o: where the bvals/bvecs files will be saved'
    print '     -e: file extension. this can be served as a filter. if no extension, '
    print '         then do not specify this parameter'
    print 'Author: Tony Jiang Email: TJiang@Kesslerfoundation.org'
    print '2014-4102 All Rights Reversed!'
    print '******************************************************************************'


def main(argv):
    inputDir= ''
    outputDir = ''
    extension = ''
    
    try:
        opts, args = getopt.getopt(argv,"hi:o:e:",["inputDir=","outputDir=","extension="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputDir = arg
        elif opt in ("-o", "--ofile"):
            outputDir = arg
        elif opt in ("-e","--extension"):
            extension=arg
    if inputDir=="" or outputDir == "":
        print 'Must specify input directory and output directory!'
        print_help()
        sys.exit(2)
    if extension =="" :
        ext="dcm"
    else:
        ext="."+extension
    ext="*"+ext  
    bvalList,bvecList = [], []
    for  dicom_file in sorted(glob.glob(os.path.join(inputDir,ext))):
        #print dicom_file
        info=dicom.read_file(dicom_file,force='force')
        #print info
        bval=info[0x0019,0x100c].value
        bvalList.append(str(bval))
        if info[0x0019,0x100d].value=='NONE':
            bvec=[0,0,0]
        else:
            buffer=unpack('ddd',info[0x0019,0x100e].value)
            img_plane_position=info[0x0020, 0x0037].value
            vec=np.array(buffer)
            V1=np.array([float(img_plane_position[0]),float(img_plane_position[1]),float(img_plane_position[2])])
            V2=np.array([float(img_plane_position[3]),float(img_plane_position[4]),float(img_plane_position[5])])
            V3=np.cross(V1,V2)
            bvec=np.zeros(3)
            bvec[0]=np.dot(V1,vec)
            bvec[1]=np.dot(V2,vec)
            bvec[2]=np.dot(V3,vec)
        bvecList.append(bvec)
		 #print "%s  [%f %f %f]" %(bval,bvec[0],bvec[1],bvec[2])
		#write output to bvals and bvecs
    bvals, bvecs = open(os.path.join(outputDir,'bvals'), 'w'), open(os.path.join(outputDir,'bvecs'), 'w')
    bvals.write(' '.join(bvalList))
    bvecs.write(' '.join([str(bvecX[0]) for bvecX in bvecList]) + '\n')
    bvecs.write(' '.join([str(bvecY[1]) for bvecY in bvecList]) + '\n')
    bvecs.write(' '.join([str(bvecZ[2]) for bvecZ in bvecList]))
    bvals.close()
    bvecs.close()

if __name__=="__main__":
    main(sys.argv[1:])
