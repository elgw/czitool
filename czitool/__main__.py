helpstr="""
Converts czi image data to tiff files
Only supports one FOV per czi image, but will trigger a failed assert
if that is not met.

Will for each XYZ.czi a folder called XYZ will be generated with one
tif file per channel

Example: The input file 'CCDN1_TX-02(10)-AP.czi' generates

CCDN1_TX-02(10)-AP
├── AF488-T2_001.tif
├── AF568-T1_001.tif
└── DAPI-T3_001.tif

Usage:

$ czitool file1.czi, file2.czi ...

Example Usage:
$ python czitool.py /srv/secondary/ki/20250515_3D_FISH_Roser/*.czi

web page: https://www.github.com/elgw/czitool/

"""

"""
To run without install:
$ source .venv/bin/activate
$ python czitool/__main__.py /some/where/file.czi
"""

import os
import sys
import tempfile

# https://pypi.org/project/pylibCZIrw/
from pylibCZIrw import czi
import tifffile
import numpy as np


def get_outdir(fname):
    parts = os.path.split(fname)
    fname = parts[-1]
    fname = fname.replace('.czi', '')
    outdir = os.path.join(parts[0], fname)
    return outdir

def read_image(czidoc=None, M=None, N=None, P=None, chan_id=None, series=0, roi=None):
    im = np.zeros((P, N, M), dtype=np.float32)

    for z in range(0, P):
        im[z, :, :] = np.squeeze(czidoc.read(roi=roi, plane={'C': chan_id, 'Z': z, 'T': series}), axis=2)

    return im

def process_file(fname : str):
    with czi.open_czi(fname) as czidoc:

        if not os.path.isdir(outdir):
            os.mkdir(outdir)

        my_dict = czidoc.metadata
        my_dict["ImageDocument"]["Metadata"]["Information"]["Image"]
        my_dict["ImageDocument"]["Metadata"]["Information"]["Image"]["SizeC"]
        nFOV = my_dict["ImageDocument"]["Metadata"]["Information"]["Image"]["SizeS"]
        nFOV = int(nFOV)
        channels = my_dict["ImageDocument"]["Metadata"]["Information"]["Image"]["Dimensions"]["Channels"]["Channel"];
        nC = len(channels)
        cnames = []
        for c in channels:
            cnames.append(c["@Name"])

        P = my_dict["ImageDocument"]["Metadata"]["Information"]["Image"]["SizeZ"]
        P = int(P)

        with open(outdir + os.sep + 'czitool.log.txt', 'w') as fid:
            fid.write(str(my_dict))

        rectangles = czidoc.scenes_bounding_rectangle


        for fov in range(0, nFOV):
            print(f"Converting FOV {fov+1}/{nFOV}")

            for ch, chname in enumerate(cnames):
                M = rectangles[fov].w
                N = rectangles[fov].h
                # print(f"Channel {ch} : {chname}")
                im = read_image(czidoc=czidoc, M=M, N=N, P=P, chan_id=ch, series=fov, roi=rectangles[fov])
                outfile = os.path.join(outdir, f"{chname}_{fov+1:03}.tif")
                tfd, tnam = tempfile.mkstemp(dir=outdir, text=False)
                print(f"-> {outfile} ({tnam})")
                tifffile.imwrite(tnam, data=im)
                os.rename(tnam, outfile)

def czi_to_tiff(fname):

    if not os.path.isfile(fname):
        print(f"Can't open {fname} -- not a file")
        return

    print(f"Processing {fname}")
    outdir = get_outdir(fname)

    try:
        process_file(fname)
    except RuntimeError:
        print(f"{fname} can not be opened as a czi file")
        return


def cli():
    # entry point for pipx installed
    if len(sys.argv) == 1:
        print(helpstr)
        sys.exit(1)

    for fname in sys.argv[1:]:
        czi_to_tiff(fname)

if __name__ == "__main__":
    # Running as uninstalled script
    cli()
