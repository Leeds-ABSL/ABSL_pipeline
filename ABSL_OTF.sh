#!/bin/sh

# University of Leeds Astbury Biostructure Laboratory 
# data copy script 
# move files from the offload server to users Equipment directry
# make symbolic links to the files in the Raw_data directoty
# run resolution replacement script to replace the EPA max resolution values with 0.5 CC values
# run micrograph_analysis script
# cycle until completed 

# Shaun Rawson
# modified - Matt Iadanza - 2018/06

# Astbury Biostructure Laboratory - University of Leeds
# contact fbscem@leeds.ac.uk with bugs and suggestions

########### external scripts - point these to the locations of these two scripts #################################

# matti's micrograph analysis
mic_analysis_path='/fbs/emsoftware2/LINUX/fbsmi/scripts/new_fetch/scripts_fetch/ABSL_micrograph_analysis.py'

#rado's replace ctf EPA max resolution values
res_replace_path='/absl/SCRATCH/Users/bssdr/test/scripts/ABSL_EPA_CC_threshold.py'

##################################################################################################################


src_dir=$4
inproj=$3
project=${inproj//[^[:alnum:]]/}
todays_date=$(date +"%d%m%Y")
current_user=$(whoami)
start_time=$(date +%s)
run_time=$(($1 * 60))
end_time=$(($start_time + $run_time))
current_time=$start_time

if [ "$#" -lt 4 ]; then
    echo "Error: Illegal number of parameters."
    echo "Usage: sh data_copy.sh runtime(minutes) server(krios1 | gatan) projectid sourcedir"
    echo "Example: sh data_copy 60 krios1 myproj"

    exit 1
fi

if [ "$project" == "" ]; then
    echo "Error: No valid project name given."
    echo "Usage: sh data_copy.sh runtime(minutes) server(krios1 | gatan) projectid sourcedir"
    echo "Example: sh data_copy 60 krios1 myproj"
    echo "project must consist only of alphanumeric characters."    

    exit 1
fi 

case "$2" in
gatan)
    server=GATAN
    src="/offload2/$src_dir"
    save_path="/absl/Equipment/$server/DoseFractions/$current_user/${todays_date}_${project}/"
    ext=Images-Disc1/Grid*/Data/*-*.mrc

    ;;
krios1)
    server=KRIOS1
    src="/offload1/$src_dir"
    save_path="/absl/Equipment/$server/$current_user/${todays_date}_${project}/"
    ext=Images-Disc1/Grid*/Data/*Fractions.mrc

    ;;
  *)
    echo "Error: Illegal server."
    echo "Usage: sh data_copy.sh runtime(minutes) server(krios1 | gatan) projectid sourcedir"
    echo "Example: sh data_copy 60 krios1 myproj"
    echo "Parameters are case sensitive."

    exit 1
    ;;
esac

if [ ! -d "$src" ]; then
    echo "Error: Source directory not found."
    echo "Usage: sh data_copy.sh runtime(minutes) server(krios1 | gatan) projectid sourcedir"
    echo "Example: sh data_copy 60 krios1 myproj"
    echo "Ensure that $src exists."

    exit 1
fi

if [ ! -d "$save_path" ]; then
    mkdir -p "$save_path"
fi

if [ ! -d "Raw_data" ]; then
    mkdir -p "Raw_data"
fi


echo "Start: $start_time End: $end_time"

while [ $current_time -lt $end_time ]
do
rsync -rutlDv "$src/" "$save_path"
ln -s $save_path$ext "Raw_data/" &>/dev/null
python $res_replace_path CtfFind/job003/micrographs_ctf.star
python $mic_analysis_path --i CtfFind/job003/micrographs_ctf_CC0.5.star
sleep 30
current_time=$(date +%s)
done
python $res_replace_path CtfFind/job003/micrographs_ctf.star
python $mic_analysis_path --i CtfFind/job003/micrographs_ctf_CC0.5.star

