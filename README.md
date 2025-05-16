# czitool

A throwaway script that converts czi image data to tiff files
Only supports one FOV per czi image, but will trigger a failed assert
if that is not met.

Will for each `XYZ.czi` a folder called `XYZ` will be generated with
one tif file per channel.

Example: The input file `CCDN1_TX-02(10)-AP.czi` generates

``` shell
CCDN1_TX-02(10)-AP
├── AF488-T2_001.tif
├── AF568-T1_001.tif
└── DAPI-T3_001.tif
```

I.e., the naming convention is the same as for
[nd2tool](https://www.github.com/elgw/nd2tool)

Usage:

`$ czitool file1.czi, file2.czi ...`

Example Usage:

`$ python czitool.py /srv/secondary/ki/20250515_3D_FISH_Roser/*.czi`

## Installation

- Install the script with [pipx](https://github.com/pypa/pipx)

``` shell
pipx install .
```


## Todo

- It would of course be nice to use
  [ZEISS/libczi](https://github.com/ZEISS/libczi) directly.
- Support more types of images
- Add some command line options, ...
