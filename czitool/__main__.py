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

Erik Wernersson, 2025-05-15

"""

"""
For bioformats, see https://pythonhosted.org/python-bioformats/
"""


import os
import sys
import javabridge
import bioformats
import tifffile
import numpy as np

def get_outdir(fname):
    parts = os.path.split(fname)
    fname = parts[-1]
    fname = fname.replace('.czi', '')
    outdir = os.path.join(parts[0], fname)
    return outdir

def read_image(reader=None, M=None, N=None, P=None, chan_id=None):
    im = np.zeros((P, N, M), dtype=np.float32)
    for z in range(0, P):
        im[z, :, :] = reader.read(c=chan_id, z=z)
    return im

def czi_to_tiff(fname):

    outdir = get_outdir(fname)

    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    metadata = bioformats.get_omexml_metadata(path=fname)
    o = bioformats.OMEXML(metadata)

    print(o.image().get_Name())
    print(o.image().get_AcquisitionDate())
    assert(o.get_image_count() == 1)
    nC = o.image().Pixels.get_channel_count()
    M = o.image().Pixels.get_SizeX()
    N = o.image().Pixels.get_SizeY()
    P = o.image().Pixels.get_SizeZ()
    print(f"size = {M} x {N} x {P}")

    reader = bioformats.ImageReader(fname)

    for ch in range(0, nC):
        chname = o.image().Pixels.channel(ch).get_Name()
        print(f"Channel {ch} : {chname}")
        im = read_image(reader=reader, M=M, N=N, P=P, chan_id=ch)
        outfile = os.path.join(outdir, f"{chname}_001.tif")
        print(f"-> {outfile}")
        tifffile.imwrite(outfile, data=im)

def cli():
    if len(sys.argv) == 1:
        print(helpstr)
        sys.exit(1)

    javabridge.start_vm(class_path=bioformats.JARS)

    for fname in sys.argv[1:-1]:
        czi_to_tiff(fname)

    javabridge.kill_vm()

if __name__ == "__main__":
    cli()
