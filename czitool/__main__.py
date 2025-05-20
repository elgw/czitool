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
For bioformats, see https://pythonhosted.org/python-bioformats/

To run without install:
$ source .venv/bin/activate
$ python czitool/__main__.py /srv/secondary/ki/20250515_3D_FISH_Roser/16.5.25/CCDN1_TX_2-01-AP.czi
"""


import os
import sys

import bioformats

import javabridge
import tifffile
import numpy as np
import tempfile

def get_outdir(fname):
    parts = os.path.split(fname)
    fname = parts[-1]
    fname = fname.replace('.czi', '')
    outdir = os.path.join(parts[0], fname)
    return outdir

def read_image(reader=None, M=None, N=None, P=None, chan_id=None, series=0):
    im = np.zeros((P, N, M), dtype=np.float32)
    for z in range(0, P):
        im[z, :, :] = reader.read(c=chan_id, z=z, series=series, rescale=False)

    return im

def czi_to_tiff(fname):
    print(f"Processing {fname}")
    outdir = get_outdir(fname)

    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    metadata = bioformats.get_omexml_metadata(path=fname)
    o = bioformats.OMEXML(metadata)

    with open(outdir + os.sep + 'czitool.log.txt', 'w') as fid:
        fid.write(str(o))

    print(o.image().get_Name())
    print(o.image().get_AcquisitionDate())

    nFOV = o.get_image_count()

    reader = bioformats.ImageReader(fname)
    for fov in range(0, nFOV):
        nC = o.image(fov).Pixels.get_channel_count()
        M = o.image(fov).Pixels.get_SizeX()
        N = o.image(fov).Pixels.get_SizeY()
        P = o.image(fov).Pixels.get_SizeZ()
        print(f"size = {M} x {N} x {P}")
        for ch in range(0, nC):
            chname = o.image(fov).Pixels.channel(ch).get_Name()
            print(f"Channel {ch} : {chname}")
            im = read_image(reader=reader, M=M, N=N, P=P, chan_id=ch, series=fov)
            outfile = os.path.join(outdir, f"{chname}_{fov+1:03}.tif")
            tfd, tnam = tempfile.mkstemp(dir=outdir, text=False)
            print(f"-> {outfile} ({tnam})")
            tifffile.imwrite(tnam, data=im)
            os.rename(tnam, outfile)


def cli():
    # entry point for pipx installed
    if len(sys.argv) == 1:
        print(helpstr)
        sys.exit(1)

    # This suppresses the warning messages, solution found at
    # https://forum.image.sc/t/python-bioformats-and-javabridge-debug-messages/12578/12
    myloglevel="ERROR"  # user string argument for logLevel.

    javabridge.start_vm(class_path=bioformats.JARS)

    rootLoggerName = javabridge.get_static_field("org/slf4j/Logger","ROOT_LOGGER_NAME", "Ljava/lang/String;")
    rootLogger = javabridge.static_call("org/slf4j/LoggerFactory","getLogger", "(Ljava/lang/String;)Lorg/slf4j/Logger;", rootLoggerName)
    logLevel = javabridge.get_static_field("ch/qos/logback/classic/Level",myloglevel, "Lch/qos/logback/classic/Level;")
    javabridge.call(rootLogger, "setLevel", "(Lch/qos/logback/classic/Level;)V", logLevel)



    for fname in sys.argv[1:]:
        czi_to_tiff(fname)

    javabridge.kill_vm()

if __name__ == "__main__":
    # Running as uninstalled script
    cli()
