# ODI Post Calib

## Overview

This repo demonstrate how post-QR calibration is done on WIYN ODI
data to improve the astrometry and photometry

## Instructions

1. Clone the repo and install the dependencies

    * python 2.7

    * python packages (available from pip):

        `numpy scipy matplotlib astropy astroquery ruffus bottleneck multiprocess requests`

    * python packages (home baked)

        `apus` https://github.com/Jerry-Ma/apus

            $ cd extern
            $ git clone https://github.com/Jerry-Ma/apus.git

        `pyjerry` https://github.com/Jerry-Ma/pyjerry

            $ cd extern
            $ git clone https://github.com/Jerry-Ma/pyjerry

    * other:

        `stilts`  http://www.star.bris.ac.uk/~mbt/stilts/

            $ cd extern
            $ ./setup_stilts.sh

        `SExtractor, SCAMP, SWarp` http://www.astromatic.net/

            $ cd extern
            $ ./setup_astromatic.sh

        This will create a directory in extern named `astromatic` with
        the following symlinks:

            astromatic/
                bin/
                    sex             # link to SExtractor executable
                    scamp           # link to SCAMP executable
                    swarp           # link to SWarp executable
                    ldactoasc       # link to ldactoasc executable comes along with SExtractor
                share/
                    sextractor/     # link to SExtroctor share directory
                    scamp/          # link to SCAMP share directory
                    swarp/          # link to SWarp share directory
        The symlinks should point to your installation of SExtractor, SCAMP
        and SWarp in your system (used `which` under the hood). If those programs
        are not installed in the default path/layout, you have to manually create those links.

        Or, you can skip running the astromatic setup script if the executables
        and folders are already placed in such way in your system, which is the
        default case if configured using `--prefix=/usr/local`:

            /usr/local/
                bin/
                    sex ...
                share/
                    sextractor ...

        In this case, `apus` is able to locate everthing it needs if you supply
        the following in your `odi_post_calib.py` file:

             conf.env_overrides = {
                     ...
            -        'path_prefix': 'extern/astromatic/'
            +        'path_prefix': '/usr/local/',
                     }


2. Edit `odi_post_calib.py` by following the comments inside the file;
or for quick start, create symbolic link from an existing data directory
to the repo, and name it as `demo_data`.

    The original data should layout in the default PPA way. The
    sym-linked `demo_data` should look like the following:

        demo_data/
            calibrated/
                2016xxxxTxxxx
                    o2016xxxx.fz
                    o2016xxxx.fits

    Note that the data downloaded from PPA is `.fz`, therefore they should
    be uncompresed first, e.g., in bash:

        $ for i in */*.fz; do echo $i && funpack $i; done

3. Initialize the working directory

        ./apus_shortcut.sh init

4. (Optional) generate flowchart by

        ./apus_shortcut.sh flowchart [flowchart.png]

5. Run the pipeline with

        ./apus_shortcut.sh run <module name>

    `<module name>` can be `all`, `prep`, `astro`, `phot`, `mosaic`

6. Check the result when finished

    * `orig_.fits`  original QR calibrated images, symlinked from data directory
    * `masked_.fits` images after applying the bpm files defined in QR `.bpm` directory
    * `sexinit_.fits` ldac catalogs SExtracted from `masked_.fits`
    * ...

7. Tweak the configuration

    * All configuration is in directory `config`

    * `config.py` configurable values used in the various python-based functions
    * `conf.sex_init` config that generates `sexinit_*.fits`
    * `conf.scamp_2mass` config for SCAMP
    * ...

8. Regenerate the result

        ./apus_shortcut.sh rerun <module name>

    This will rerun the given module. However, this is not the most efficient
    way, but it's more reliable and can make sure everthing is regenerated.

    or,

        ./apus_shortcut.sh run <module name>

    This will exploit the ability of `apus` of detecting outdated results
    and only regenerate those needed. Attention has to be paid on the
    timestamps of the files, also the output logs, to make sure everything you
    need to regenerate is regenerated.


## Advanced


### Use the full ability of `APUS`

Unfortunately APUS is not fully documented, but you can read
`apus_shortcut.sh` to find out some typical usage of `apus`.

Also, APUS inherits from the `Ruffus.cmdline` module, which
is documented [here] (http://www.ruffus.org.uk/tutorials/new_tutorial/command_line.html).


### Troubleshoot

    N/A
