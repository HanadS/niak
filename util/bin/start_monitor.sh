#!/bin/bash
niak_cmd.py Niak_fmri_preprocess --func_hint task-rest --subjects 8-9 --file_in /mnt/agrile/dataset/gsp_bids --folder_out results-dir --opt-psom-max_queued 4 --opt-slice_timing-type_scanner Bruker --opt-slice_timing-type_acquisition interleaved ascending --opt-slice_timing-delay_in_tr 0 --opt-resample_vol-voxel_size 10 --opt-t1_preprocess-nu_correct-arg '-distance 75' --opt-time_filter-hp 0.01 --opt-time_filter-lp Inf --opt-regress_confounds-thre_fd 0.5 --opt-smooth_vol-fwhm 6
