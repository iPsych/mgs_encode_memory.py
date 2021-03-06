#!/usr/bin/env python2
"""
Mute and unmute all sessions
20180205WF - used to supress monitor changing audio notification
             in presentation of task
adapted from pycaw example documentation:
    https://github.com/AndreMiras/pycaw/blob/develop/examples/simple_audio_volume_example.py
"""
from __future__ import print_function
import os


class winmute():
    def __init__(self):
        try:
            from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
            sessions = AudioUtilities.GetAllSessions()
            self.volumes = [session._ctl.QueryInterface(ISimpleAudioVolume)
                            for session in sessions]
            # is already muted?
            self.origMute = [v.GetMute() for v in self.volumes]
        #except ImportError: # 20180409 -- if it fails for anyreason, continue
        except:
            # set no volumes and no origMutes, nothing will be done by funcs below
            if os.name in ['nt']:
                print("WARNING: no volume control; install pycaw")
                print("\tpython -m pip --user install https://github.com/AndreMiras/pycaw/archive/master.zip")
            self.volumes = []
            self.origMute = []

        # or change master volume with e.g. SetMasteRVolumeLevel(-20.0,None)
        # self.origvol = [volume.getMasterVolumeLevel()
        #                 for volume in self.volumes]

    def mute_all(self):
        for v in self.volumes:
            v.SetMute(1, None)

    def unmute_all(self):
        for v in self.volumes:
            v.SetMute(0, None)

    def undo_mute(self):
        for (v, om) in zip(self.volumes, self.origMute):
            v.setMute(om, None)
