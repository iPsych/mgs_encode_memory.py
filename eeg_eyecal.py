#!/usr/bin/env python
# -*- elpy-use-ipython: "ipython"; -*-

from psychopy import visual, core, data, event
from mgs_task import mgsTask, wait_until
import numpy as np

isfullscreen = False
# if we are fullscreen, we're at eeg and want to send ttl too
usePP = isfullscreen

# how long to wait at each event
fixdur = 1
dotdur = .5

# setup screen
if isfullscreen:
    win = visual.Window(fullscr=True)
else:
    win = visual.Window([800, 600])

win.winHandle.activate()  # make sure the display window has focus
win.mouseVisible = False  # and that we don't see the mouse

# setup task (get send_ttl, crcl, iti_fix)
task = mgsTask(win, usePP = usePP)

# get 20 positions from 20% to 90% 
pos = np.linspace(.2,.9,20)
allpos =   np.concatenate( [pos, -1 * pos]) 
#ridx = np.random.permutation(len(allpos))
# fixed for all presentations
ridx = [34, 10, 32, 17, 20, 21, 22, 37,  7, 36, 18, 23, 13, 14, 16, 39,  2,
       25, 33, 35, 29, 27,  3, 24, 38,  6, 12,  9, 31, 11,  8, 26,  1, 30,
       28,  4,  0,  5, 15, 19]

ridx = [0,39,19,20,21]
def print_and_ttl(msg,ttl):
    print(msg)
    if usePP:
        task.send_ttl(ttl)


task.wait_for_scanner(['space'],'Ready?')
task.send_code('start',None,None)

winwidth = task.win.size[0]/2
print(winwidth)
for ri in range(len(ridx)):
    # find position and ttlcode
    i = ridx[ri]
    p = allpos[i] * winwidth

    # ttl -- avoid 128 and 129 (start and stop)
    posttl = i + 1   # 1 - 40
    fixttl = i + 201 # 201 - 240


    # draw cricle
    task.crcl.pos = (p,0)
    task.crcl.draw()
    win.callOnFlip(print_and_ttl,"p at %.02fx (%.02fpx)" % (allpos[i], p), posttl)
    ft=win.flip()
    # wait a big
    wait_until(ft + dotdur)
    event.waitKeys()

    # draw cross
    task.iti_fix.draw()
    win.callOnFlip(print_and_ttl,"back to fix", fixttl)
    ft=win.flip()
    # wait a bit
    wait_until(ft + fixdur)


task.send_code('end',None,None)
win.close()
