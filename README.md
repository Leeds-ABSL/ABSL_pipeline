# ABSL_pipeline
Scripts for the ABSL on-the-fly image processing pipeline

Contact fbscem@leeds.ac.uk for suggestions/bug reports

If you find the scripts here useful in your research please cite:

>Thompson RF, Iadanza MG, Rawson SD, Hesketh EL, Ranson NA. (2018) 
>Collection, pre-processing, and on-the-fly analysis of data for high-resolution, single-particle cryo-electron microscopy. 

## ABSL_micrograph_analysis.py
These program usse the star file output by GCTF for analyzing image statistics.

It requires the column \_rlnCtfMaxResolution to be present.  This is only written if eqiphase analysis is selected when GCTF is run if it is not present the program should produce and error.  If the column \_rlnPhaseShift is present, the program will also do phase shift analyses.

To run the script use the command:
`./ABSL_micrograph_analysis --i <micrographs star file>`

If run with a `--f` flag the program can filter micrographs based on any combination of resolution, defocus, astigmatism, or phase shift. If this option is used it will produce an new starfile with the original name with '\_culled' added. It will also generate a text file called 'bad_micrographs.txt' containing a list of micrographs discarded.

The filtering is rather simple - it functions as a lowpass filter with the value entered.  For more flexible filtering use Matt's rln_star_filter script: 

[https://twitter.com/mattiadanza/status/780380747286929408](https://twitter.com/mattiadanza/status/780380747286929408)

## ABSL_EPA_CC_threshold.py
Gctf estimates the resolution of a micrograph as the resolution at which the cross correlation coefficient (CCC) between the eqi-phase average and actual micrograph power spectrum falls to 0.  We feel this overestimates the resolution and prefer to use a CCC cutoff of 0.5.  EPA_CC_threshold.py reads the log files created by gCTF and then replaces the \_rlnMaxResolution column in Relion’s file micrographs_ctf.star with values determined using the 0.5 CCC value.

The script is run automatically by OTF.sh.  To run the script on its own use the command:
`./GCTFscript.py <micrographs_ctf.star>`

Use the optional flag `–CCC_cutoff <n>` to change the CCC cutoff from the default of 0.5, where “n” is the CCC cut off you would like to use.

## pipeliner.cpp
The standard Relion installation will crash if used on the fly for datasets of several thousand micrographs. This is due to how Relion decides a job is finished and starts the next job.  The program looks for the output file it expects at the end of the job, waits 10s and then starts next job in schedule. When the output file contains 1000's of lines the time taken to write this file out can exceed 10s. If this happens the next step will run on a list of files which is empty - which crashes the pipeline.

The workaround used in the OTF modificaton of Relion is to change the 10s wait time to 60s - this allows for the file to finish writing before the next process begins. In the src directory of Relion line 648 in the file pipeliner.cpp was changed to:

```
            // Now wait until that job is done!
            while (true)
            {
                if (!exists(fn_check))
                {
                    fn_check_exists = false;
                    break;
                }

                sleep(60);
                checkProcessCompletion();
                if (processList[current_job].status == PROC_FINISHED)"
```

Replace the pipliner.cpp in the `src/` directory of relion with this version and then recomplie the program.


## ABSL_OTF.sh
This script is used at leeds to copy files from the different microscope systems to a central drive for storge and processing and run the above analysis scripts.  It is provided more as an example as the setup of any individual system will vary greatly.  

Briefly, the script copies files to the approprite directories, runs ABSL_EP_CC_threshold.py and ABSL_micrograph_analysis.py and then waits 30 seconds minutes before doing it again until the time has elapsed. 

## EM_Pull_Files.ps1
This is a windows power shell script that is used to transfer data from the Gatan detector control computer to the Leeds file system and porperly set its access permissions.  This script is very specific to the Leeds system, a similar data transfer script may be necessary depending on the specific setup of an individual microscope and file system. 


## License information

These programs are free software: you can redistribute and/or modify them under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
 
These programs are distributed in the hope that they will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
