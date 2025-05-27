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

def nfind(field_name, d, current_path=''):
    if not isinstance(d, dict):
        return

    if field_name in d:
        yield current_path

    for k in d:
        if isinstance(d[k], list):
            index = 0
            for array_element in d[k]:
                for j in nfind(field_name, array_element, current_path + f'.{k}.[{index}]'):
                    yield j

                index += 1

        elif isinstance(d[k], dict):
            for found in nfind(field_name, d[k], current_path + f'.{k}'):
                yield found

def get_outdir(fname):
    parts = os.path.split(fname)
    fname = parts[-1]
    fname = fname.replace('.czi', '')
    outdir = os.path.join(parts[0], fname)
    return outdir

def read_image(czidoc=None, P=None, chan_id=None, series=0, roi=None):
    M = roi.w
    N = roi.h
    im = np.zeros((P, N, M), dtype=np.float32)

    for z in range(0, P):
        im[z, :, :] = np.squeeze(czidoc.read(roi=roi, plane={'C': chan_id, 'Z': z, 'T': series}), axis=2)

    return im

def process_file(fname : str):
    outdir = get_outdir(fname)
    with czi.open_czi(fname) as czidoc:

        if not os.path.isdir(outdir):
            os.mkdir(outdir)

        meta = czidoc.metadata['ImageDocument']['Metadata']
        nFOV = 1
        try:
            nFOV = meta["Information"]["Image"]["SizeS"]
            nFOV = int(nFOV)
        except:
            print(f"The files does not contain Information->Image->SizeS, only one FOV?")

        channels =meta["Information"]["Image"]["Dimensions"]["Channels"]["Channel"];

        nC = len(channels)
        cnames = []
        for c in channels:
            cnames.append(c["@Name"])

        ## Number of planes per image. So each image in a czi file has to have
        # the same number of planes?


        P = int(meta["Information"]["Image"]["SizeZ"])

        ## Figure out the pixel size
        # 'DefaultUnitFormat' seems to indicate what unit to use when
        # showing the distance, the value seems to be given in meters [m]
        #
        # In one of the files it said:
        # meta["Scaling"]["Items"]["Distance"][0]['DefaultUnitFormat'] == 'µm':

        dx = meta["Scaling"]["Items"]["Distance"][0]['Value']
        dx_nm = float(dx)*1e9
        dy = meta["Scaling"]["Items"]["Distance"][1]['Value']
        dy_nm = float(dy)*1e9
        dz = meta["Scaling"]["Items"]["Distance"][2]['Value']
        dz_nm = float(dz)*1e9
        print(f"Pixel size: {dx_nm:.1f} x {dy_nm:.1f} x {dz_nm:.1f} nm")

        # Dump all the metadata for later reference.
        with open(outdir + os.sep + 'czitool.log.txt', 'w') as fid:
            fid.write(str(meta))

        # Each Field of View (FOV) is found in this dictionary
        # of bounding rectangles. They key is the numerical id
        # The roi_id's does not need to start at 0.

        rects = czidoc.scenes_bounding_rectangle

        # For a single FOV, sometimes this is set instead

        if(len(rects) == 0):
            rects = {0: czidoc.total_bounding_rectangle}

        for ii, roi_id in enumerate(rects.keys()):
            roi = rects[roi_id]
            print(f"Converting FOV #{roi_id+1} ({ii+1}/{nFOV})")

            for ch, chname in enumerate(cnames):
                # print(f"Channel {ch} : {chname}")
                im = read_image(czidoc=czidoc, P=P, chan_id=ch, series=roi_id, roi=roi)
                outfile = os.path.join(outdir, f"{chname}_{roi_id+1:03}.tif")
                tfd, tnam = tempfile.mkstemp(dir=outdir, text=False)
                print(f"-> {outfile} ({tnam})")

                md = {'spacing': dz_nm, 'unit': 'nm', 'axes': 'ZYX'}
                tifffile.imwrite(tnam, data=im, imagej=True, resolution=(1/dx_nm, 1/dy_nm), metadata=md)
                os.rename(tnam, outfile)

def czi_to_tiff(fname):

    if not os.path.isfile(fname):
        print(f"Can't open {fname} -- not a file")
        return

    print(f"Processing {fname}")

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
