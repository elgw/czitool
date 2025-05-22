# czitool

A throwaway script (=used twice) to converts czi image data to tiff
files with the naming convention used by
[nd2tool](https://www.github.com/elgw/nd2tool)

For each input `XYZ.czi` file, a folder called `XYZ` will be generated
with one tif file per channel and series. Also the XML metadata will
be dumped to `czitool.log.txt`.

Example:

The input file `CCDN1_TX-02(10)-AP.czi` containing a single FOV generates

``` shell
CCDN1_TX-02(10)-AP
├── AF488-T2_001.tif
├── AF568-T1_001.tif
├── czitool.log.txt
└── DAPI-T3_001.tif
```

The file `CCDN1_TX_2-01-AP.czi` with multiple series and channels generates:

``` shell
CCDN1_TX_2-01-AP
├── AF488-T2_001.tif
├── AF488-T2_002.tif
├── AF488-T2_003.tif
├── AF568-T1_001.tif
├── AF568-T1_002.tif
├── AF568-T1_003.tif
├── czitool.log.txt
├── DAPI-T3_001.tif
├── DAPI-T3_002.tif
├── DAPI-T3_003.tif
...
```

## Usage:

`$ czitool file1.czi, file2.czi ...`

Example Usage:

`$ czitool /srv/secondary/ki/20250515_3D_FISH_Roser/*.czi`

## Installation
Requires `javac`, install that with `sudo apt install default-jdk` or similar.

- Install the script with [pipx](https://github.com/pypa/pipx)

``` shell
pipx install .
```

## Could be done

- Use
  [ZEISS/libczi](https://github.com/ZEISS/libczi) directly.
- Support more types of images (for example time series).
- Add some command line options: an `--overwrite` switch, a FOV
  selector, `--fov 1:10`, etc.
- Delete temporary files on crash/abort.
- Write ImageJ metadata to the tiff files.
- Summarize the important properties from the metadata (instead of
  just dumping the whole XML).
- Find some other tool that does all of this already.

## Changelog

- 0.1.1, 2025-05-20
  - Suppression of errors from bioformats.
  - Exporting non-scaled pixel values to the tif files.
