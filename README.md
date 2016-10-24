# ODI Post Calib

## Overview

This repo demonstrate how post-QR calibration is done on WIYN ODI
data to improve the astrometry and photometry (not yet done)

## Instructions

1. Clone the repo and install the dependencies

        $ git clone https://github.com/Jerry-Ma/ODIPostCalib.git

2. Install/setup dependencies

    * python 2.7

    * python packages available from pip:

            numpy scipy matplotlib astropy astroquery ruffus bottleneck
            multiprocess requests cycler wcsaxes

    * python packages by Jerry, should clone to `extern` subdirectory:

        `apus` https://github.com/Jerry-Ma/apus  
        `pyjerry` https://github.com/Jerry-Ma/pyjerry

            $ cd extern
            $ git clone https://github.com/Jerry-Ma/apus.git
            $ git clone https://github.com/Jerry-Ma/pyjerry

    * other:

        * `stilts`  http://www.star.bris.ac.uk/~mbt/stilts/  
        run the following to setup automatically:

                $ cd extern
                $ ./setup_stilts.sh

        * `SExtractor, SCAMP, SWarp` http://www.astromatic.net/  
        run the following to setup automatically:

                $ cd extern
                $ ./setup_astromatic.sh

            This will create a directory in extern named `astromatic` with
            the following structures (symlinks):

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
                        'path_prefix': '/usr/local/',
                        }

2. Edit `odi_post_calib.py` by following the comments inside the file;
or for quick start, create symbolic link from an existing data directory
to the repo, and name it as `demo_data`.

    The original data should layout in the default PPA way. The
    sym-linked `demo_data` should look like the following:

        demo_data/
            calibrated/
                20??????T*/
                    *.fz
                    *.fits

    Note that the data downloaded from PPA is `.fz`, therefore they should
    be uncompresed first, e.g., in bash:

        $ for i in */*.fz; do echo $i && funpack $i; done

3. Initialize the working directory

        python odi_post_calib.py init

4. (Optional) generate flowchart by

        python odi_post_calib.py --flowchart flowchart.png

5. Run the pipeline with

        python odi_post_calib.py

6. Check the result when finished

    The naming conventions of produced files

    * `ppa_{objname}_odi_{band}.fits`  
       Original QR calibrated images, symlinked from data directory
    * `masked_{objname}_odi_{band}.fits`  
       Images after applying the bpm files defined in QR `.bpm` directory
    * `linked_{objname}_odi_{band}.fits`  
       Symlink to `mask_*` files, according to the blacklist file `.ota` (see comments in `odi_post_calib.py`); only the linked files are used for the rest of the processes
    * `astro_masked_{objname}_odi_{band}.fits`  
       Initial sextractor LDAC catalogs (uncleaned) to be used for astrometry calibration
    * `astro_masked_{objname}_odi_{band}.cat`  
       SExtractor ACSII version of the catalogs
    * `astro_masked_{objname}_odi_{band}.cat`  
       SExtractor ACSII version of the catalogs
    * `astroclean_masked_{objname}_odi_{band}.asc`  
       ASCII tables of the cleaned catalogs: sources on the edge and around bright stars are masked
    * `astroclean_masked_{objname}_odi_{band}.reg`  
       DS9 region files to check the bright star masks
    * `scamp_masked_{objname}_odi_{band}.reg`  
       LDAC catalog converted from cleaned catalog, to be used by SCAMP
    * `scamp_masked_{objname}_odi_{band}.hdr_astro`  
       .head files produced by SCAMP
    * `linked_{objname}_odi_{band}.hdr_swarp`
       Normalized (fix `PV?_3` caveat) .head files ready to be used by SWarp
    * `swarp_astro_linked_{objname}_odi_{band}.fits`  
       Coadd from Swarp using the .hdr_swarp headers
    * `swarp_qr_linked_{objname}_odi_{band}.fits`  
       Coadd from Swarp using the QR default wcs calibration
    * `coadd_(astro|qr)_linked_{objname}_odi_{band}.fits`  
       the `swarp_*` coadd with the 0 value replaced by nan using the coadd weight map
    * `photsex_coadd_(astro|qr)_linked_{objname}_odi_{band}.asc`  
       SExtractor catalog from the coadd for quality verifing
    * `sdssphotsex_coadd_(astro|qr)_linked_{objname}_odi_{band}.asc`  
       `photsex_*` matched with SDSS catalog
    * `fig_sdssphotsex_coadd_(astro|qr)_linked_{objname}_odi_{band}_zp.eps`  
       plot showing the photometry zeropoint dispersion
    * `fig_sdssphotsex_coadd_(astro|qr)_linked_{objname}_odi_{band}_astro.eps`  
       plot showing the astrometry offset vector
    * `fig_scamp_distortion.eps`  
       plot showing the distortion `PV?_?` key stability

7. Tweak the configuration

    * Configuration files are generated on the fly
    * generated configurations are in directory `<jobdir>/config`
    * change the configuration file directly is NOT useful

    To tweak the configurations for scamp and swarp, modify the python dict
    `params` in `odi_post_calib.py`

    For further tweaks, e.g, the sextractor configurations, look into the
    `pp_*.py` scripts, looking for the relevant `params` dict defined in
    the `func='sex'` task dicts

8. Regenerate the result

    By default, tasks are up-to-date, i.e, the output files are present and newer than inputs files won't be automatically run if do:

        $ python odi_post_calib.py

    However, if you changed the `params` dict, the relevant task SHOULD (not guaranteed) be marked as out-dated and re-run.

    To forced a task (or multiple tasks) to rerun, do:

        $ python odi_post_calib.py --forced_tasks "task name 1" [--forced_tasks "task name 2"]

    To run the pipeline until a certain tasks, do:

        $ python odi_post_calib.py -T 'target task name'

    To list the available task names:

        $ python odi_post_calib.py -l

    * Notes on how to tell wether a task is re-run indeed:

        The output of the pipeline will be logged and all the executed commands
        will be printed on the screen, followed by a line showing the running time
        for the whole collection of command for that task, e.g.:

            % the command                            10:20:17 - DEBUG   - python -u recipes/plot_distortion.py u/demo_data/linked_20151202T204534.1_Perseus_odi_u_odi_u.hdr_swarp u/demo_data/linked_20151202T205723.1_Perseus_odi_u_odi_u.hdr_swarp u/demo_data/linked_20151202T205723.2_Perseus_odi_u_odi_u.hdr_swarp u/demo_data/linked_20151202T213240.1_Perseus_odi_u_odi_u.hdr_swarp u/demo_data/linked_20151202T213240.2_Perseus_odi_u_odi_u.hdr_swarp u/demo_data/linked_20151202T213240.4_Perseus_odi_u_odi_u.hdr_swarp u/demo_data/linked_20151203T011343.1_Perseus_odi_u_odi_u.hdr_swarp u/demo_data/linked_20151203T012705.1_Perseus_odi_u_odi_u.hdr_swarp u/demo_data/linked_20151203T012705.2_Perseus_odi_u_odi_u.hdr_swarp u/demo_data/linked_20151203T012705.3_Perseus_odi_u_odi_u.hdr_swarp u/demo_data/linked_20151203T012705.4_Perseus_odi_u_odi_u.hdr_swarp u/demo_data/fig_scamp_distortion.eps 1
            % the stdout/err of the cmd              10:20:18 - DEBUG   - number of extensions: 30
            % the mark of finishing of the cmd       10:20:38 - DEBUG   - finished
            % the mark of the finishing of the task  10:20:38 - DEBUG   - task         plot dist stability          finished @ 0:00:20.892252

## Notes on the pipeline and tasks

The processing steps are defined as apus tasks in `pp_*.py` files. Each task
will be interpreted by apus to a set of shell commands running as subprocess when the
pipeline runs. The commands are printed on to screens and logged in the `logs/`
directory. You can run the commands in a shell without modification if necessary.

1. `pp_prep.py`

    * get sky layout

        Generate the bounding box (RA min/max and DEC min/max)
        outlined by the set of input data, used for retrieving reference
        catalogs. NOTE: currently it doesn't handle wrapped RA (i.e. around 0h)

    * get bright star catalog

        Retrieve bright star catalog for each object (distinguished by object
        name) from GSC2.3, for masking of bright sources. Know issues: not able
        to handle proper motion; photmetry available only on a limited number
        of bands

    * get sdss catalog

        Retrieve SDSS catalog for each object (distinguished by object name),
        using the `astroquery.SDSS` module. By default, its DR12.

    * merge catalogs

        Merge the retrived catalogs across different object names

    * apply ota mask

        Apply bad pixel mask to images; also mask out bad OTAs specified in the `.ota` file

    * select initial

        Create symlinks from the masked images, for next step processing. No link is created
        if the image is blacklisted by the `.ota` file.

    * sex for astrometry

        Initial SExtractor LDAC catalog for astrometry calibration

    * astro ldac to cat

        Convert to SExtractor ASCII for cleanup

    * clean up astro cat

        Cleanup the catalog for sources on the edge, and those affected by bright star using GSC

    * create scamp cat

        Create LDAC catalog using the cleaned catalog

    * get scamp refcat wcs

        WCS info required for create SCAMP compatible reference catalog

    * create scamp refcat

        SCAMP reference catalog created using SDSS

    * scamp

        Run SCAMP to produce astrometry corrected headers

    * create swarp header

        Fix missing PV1_3 PV2_3 keys in the SCAMP header

    * plot dist stability

        Plot distortion PV?_? keywords across different exposure

    * swarp with astro

        Coadd using the SCAMP header

    * swarp without astro

        Coadd without using the SCAMP header (i.e., using the QR header)

    * fix nan pixel

        Replace zero value pixels in SWarp coadd by NAN using the weight maps

    * mosaic photometry

        SExtractor on the coadds

    * mosaic cat to ascii

        Convert to single-line header ASCII table

    * match mosaic to sdss

        Match the catalog to SDSS

    * plot zp residue

        Plot zeropoint residue

    * plot astrometry vector

        Plot astrometry vector


## Advanced


### Use the full ability of `APUS`

Unfortunately APUS is not fully documented. However, APUS inherits from the
`Ruffus.cmdline` module, which is documented [here]
(http://www.ruffus.org.uk/tutorials/new_tutorial/command_line.html).


### Troubleshoot

    N/A
