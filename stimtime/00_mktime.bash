#!/usr/bin/env bash

# generate task timings

cd $(dirname $0)


## cue=[2];vgs=[2](NearLeft,NearRight,Left,Right * Indoor, Outdoor,None); dly=[15x 6, 7x 8, 2x 10]; mgs=[2]
# mean dly time is 6.91s * 24 = 166s; total task time (no iti) is 310
# mean task time  2+2+6.91+2  == 12.91
tr=2
dlystr="15x 6, 7x 8, 2x 10"
taskstr() { echo "cue=[$1];vgs=[$1](NearLeft,NearRight,Left,Right * Indoor, Outdoor,None); dly=[$2]; mgs=[$1]";}

genTaskTime  -o mri/s6e6_neverfirst -i 1000 "<420/24 stepsize:$tr iti:$tr-8 pad:6+6 iti_never_first> $(taskstr $tr "$dlystr")"
exit 0

#genTaskTime  -o mri_on6_anystart -i 1000 "<420/24 stepsize:$tr iti:$tr-8 pad:6+8> $(taskstr $tr "$dlystr")"

[ -d eeg ] && rm -r eeg
[ -d mri ] && rm -r mri
genTaskTime  -o mri -i 1000 "<420/24 stepsize:$tr iti:$tr-8 pad:8+8> $(taskstr $tr "$dlystr")"
genTaskTime  -o eeg -i 10   "<358/24 stepsize:.5 iti:1.5-2.5 iti_never_first> $(taskstr $tr "$dlystr")"
genTaskTime  -o test -i 1   "<15/12 stepsize:.01 iti:0.1 iti_never_first> $(taskstr .25 .25)"
genTaskTime  -o practice -i 1  "<140/20 stepsize:1 iti:2 iti_never_first> cue=[1];vgs=[1](Left,Right * None, Indoor); dly=[10x 1,8x 2,6,8]; mgs=[1]"
genTaskTime  -o behave -i 4   "<240/16 stepsize:.5 iti:1.5-2.5 iti_never_first> cue=[2];vgs=[2](NearLeft,NearRight,Left,Right * Indoor, None); dly=[$dlystr]; mgs=[2]"

exit 0

# mean task time  2+2+2+7.222  == 13.2 avg trial
dlystr="10x 6, 5x 8, 3x 10"
genTaskTime  -o mri/short -i 1000 "<338/18 stepsize:$tr iti:$tr-8 pad:6+6 iti_never_first> $(taskstr $tr "$dlystr")"

## explore
# # alle events ordered by timing
#for f in mri/065395552359387164/*1D; do tr ' ' '\n' < $f | sed "/^$/d;s/^/$(basename $f .1D)\t/"; done|sort -nk2|column -t
# # dist of iti
# for f in mri/3256956031658697997/*1D; do tr ' ' '\n' < $f | sed "/^$/d;s/^/$(basename $f .1D)\t/;s/:/\t/g"; done|sort -nk2|grep 'mgs\|cue'|sed 1d| perl -ne 'chomp; print $_ .(/cue/?"\n":"\t")'|sed '$d'| awk '{print $5-$2-$3}'|sort |uniq -c


# previous
#genTaskTime  -o stims '<300/30> vgs=[1.5](Left,Right * Indoor,Outdoor,None); dly=[15x 1.5, 10x 2, 3x 3, 2x 4 ]; mgs=[1.5]'
#genTaskTime -v 0  -o ../stims/ -i 2 '<300/24 stepsize:2> vgs=[2](Left,Right * Indoor, Outdoor,None); dly=[13x 6, 7x 8, 4x 10]; mgs=[2]'
# genTaskTime -v 0  -o ../stims/ -i 2 '<360/24 stepsize:2 iti:2-10 pad:10+10> vgs=[2](Left,Right * Indoor, Outdoor,None); dly=[13x 6, 7x 8, 4x 10]; mgs=[2]

