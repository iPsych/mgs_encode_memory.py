#!/usr/bin/env python2
# -*- py-which-shell: "python2"; -*-

# https://github.com/psychopy/psychopy/blob/master/psychopy/demos/coder/experiment%20control/TrialHandler.py
# on archlinux, python is python3
# ^M-: (run-python "/usr/bin/python2")

from __future__ import division
from psychopy import visual, data, logging, gui  # , event
import datetime  # set timepoint default, start time
import sys
import os
from mgs_task import mgsTask, gen_run_info, \
                     take_screenshot, wait_until, getSubjectDataPath, \
                     host_tasktype
# from mgs_task import *

# ---- settings -----
# -- host specific --
run_total_time = {'mri': 420, 'eeg': 358, 'test': 15, 'unknown': 420}
nruns_opt = {'mri': 3, 'eeg': 4, 'test': 2, 'unknown': 3}
parallel_opt = {'mri': False, 'eeg': True, 'test': False, 'unknown': False}
arrington_opt = {'mri': True, 'eeg': False, 'test': False, 'unknown': True}

# -- general settings --
mgsdur = 2  # this is tr locked for fmri
# TODO check against traildf max

# what key does the scanner send on the start of a TR?
# ^, =, or esc
scannerTriggerKeys = ['asciicircum', 'equal', 'escape', '6']

# paths are relative to this script
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# default settings
show_instructions = True
isfullscreen = True
subjnum = ''
imgset = 'A'
# 2018 is tp1
timepoint = datetime.datetime.now().year - 2017
getReadyMsg = 'Waiting for scanner (pulse trigger)'

# settings based on tasktype
tasktype = host_tasktype()
if tasktype == 'unknown':
    print('unkown host, defaulting to mri')
    tasktype = 'mri'

nruns = nruns_opt[tasktype]
useArrington = arrington_opt[tasktype]
useParallel = parallel_opt[tasktype]


# # different defaults for different computers
if tasktype == 'eeg':
    scannerTriggerKeys = scannerTriggerKeys + ['space']
    getReadyMsg = 'Ready?'
elif tasktype == 'test':
    tasktype = 'test'
    subjnum = 'test'
    show_instructions = False
    isfullscreen = False
    scannerTriggerKeys = scannerTriggerKeys + ['space']
    getReadyMsg = 'TESTING TESTING TESTING'
elif tasktype == 'mri':
    pass
else:
    print('tasktype is "%s"! This should never happen' % tasktype)

# compute date compenent of id
subjdateid = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")

# # get subj info
# we can use the command line
# or we can get a windowed dialog box
if (len(sys.argv) > 1):
    subjnum = sys.argv[1]
    start_runnum = 1

else:
    box = gui.Dlg()
    box.addField("Subject ID:", subjnum)
    box.addField("Image Set", imgset, choices=['A', 'B'])
    box.addField("Date ID:", subjdateid)
    box.addField("Run number:", 1)
    box.addField("instructions?", show_instructions)
    box.addField("fullscreen?", isfullscreen)
    box.addField("eyetracking (mr)?", useArrington)
    box.addField("ttl (eeg)?", useParallel)
    box.addField("timing type", tasktype, choices=run_total_time.keys())
    box.addField("Time Point", timepoint, choices=[0, 1, 2, 3, 4])
    box.addField("total # runs", nruns)

    boxdata = box.show()
    if box.OK:
        subjnum = boxdata[0]
        imgset = boxdata[1]
        subjdateid = boxdata[2]
        start_runnum = int(boxdata[3])
        show_instructions = boxdata[4]
        isfullscreen = boxdata[5]
        useArrington = boxdata[6]
        useParallel = boxdata[7]
        tasktype = boxdata[8]
        timepoint = boxdata[9]
        nruns = int(boxdata[10])
    else:
        sys.exit(1)

subjid = subjnum + '_' + subjdateid
# maybe we want to auto add date?
# + datetime.datetime.strftime(datetime.datetime.now(),"_%Y%m%d")


# # trials using trialHandler and list of dicts
# possiblepos=[-1, 1, -.75, .75, -.5, .5]
# # numpy.linspace(.5,1,3).reshape(-1,1) * (-1,1)
# (sacc_images,novel_images) = image_sets()

# # put together for saccade trials
# C:\Users\Public\Desktop\Tasks\mgs_encode_memory.py\

# # paths
# like: "subj_info/10931/01_eeg_A"
(datadir, logdir) = getSubjectDataPath(subjid, tasktype, imgset, timepoint)

# # get all_runs_info
# all_run_info = {'imagedf': imagedf, 'run_timing': run_timing }
all_runs_info = gen_run_info(nruns, datadir, imgset, task=tasktype)


# # screen setup
# win = visual.Window([400,400],screen=0)
if isfullscreen:
    win = visual.Window(fullscr=True)
else:
    win = visual.Window([800, 600])

win.winHandle.activate()  # make sure the display window has focus
win.mouseVisible = False  # and that we don't see the mouse

task = mgsTask(win, useArrington=useArrington, usePP=useParallel)


# # instructions
# OR hack to have somthing in image
#    incase we start with a 'None' null image trial
#    (instructions would do this)
if show_instructions:
    task.sacc_instructions()
else:
    pass
    # not needed, we softcode the defsize (225,225)
    # replace_img(task.img, 'img/example.png', 1, task.imgratsize)
    # win.clearBuffer()

# take screenshots:
# takeshots="20171101"
takeshots = None

# this is kludgy. duration is included in timing files
# maybe iti should be an included 1D
if tasktype == 'test':
    mgsdur = .25

for runi in range(start_runnum-1, nruns):
    run = runi + 1
    print("### run %d" % run)
    
    trialdf = all_runs_info['run_timing'][runi]

    seconds = datetime.datetime.strftime(datetime.datetime.now(), "%H%M%S")
    
    # # logging
    logfilename = "info_%s_%d_%s.log" % (subjid, run, seconds)
    logfile = os.path.join(logdir, logfilename)
    lastLog = logging.LogFile(logfile, level=logging.INFO, filemode='w')
    logging.log(level=logging.INFO,
                msg='run %s, loading at epoch %s' % (run, seconds))
    logging.flush()  # when its okay to write

    # trial settings and timing
    sacc_trials = data.TrialHandler2(
                    trialdf.T.to_dict().values(),
                    1,
                    method='sequential',
                    extraInfo={'subjid': subjid,
                               'epoch': seconds,
                               })

    # # run saccade trials
    # blockstarttime=core.getTime()
    eyetrackingfile = '%s_run%d_%s.txt' % (subjid, run, seconds)
    task.eyetracking_newfile('%s' % eyetrackingfile)
    blockstarttime = task.wait_for_scanner(scannerTriggerKeys, getReadyMsg)
    logging.log(level=logging.INFO,
                msg='scanner trigger recieved at %d' % blockstarttime)

    # for all trials in this run
    for t in sacc_trials:
        # run the trial
        fliptimes = task.sacc_trial(t, blockstarttime, takeshots=takeshots,
                                    logh=logging)

        # give mgs it's time then put up the iti cross
        mgsoff = blockstarttime + t['mgs'] + mgsdur
        wait_until(mgsoff)
        fliptimes['iti'] = task.run_iti()

        # and take a screenshot if we want it
        if takeshots:
            take_screenshot(win, takeshots + '_05_iti')
            break

        # add fliptimes
        for k, v in fliptimes.items():
            sacc_trials.addData(k + '_flip', v)

    # finish up
    task.run_iti()

    savefile_csv = '%s_%s_%d_view.csv' % (subjid, tasktype, run)
    savefile_csv_path = os.path.join(datadir, savefile_csv)
    print('saving %s' % savefile_csv_path)
    sacc_trials.data.to_csv(savefile_csv_path)

    thisendtime = run_total_time[tasktype] + blockstarttime
    print("running to end of time (%.02f, actual %.02f)" %
          (run_total_time[tasktype], thisendtime))
    wait_until(thisendtime)
    task.run_end(run, nruns)  # end ttl/close eyefile, show finsihed text
    logging.flush()

# done will all runs
win.close()
