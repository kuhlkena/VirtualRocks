import os
import shutil
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import messagebox as mb
import scripts.PointCloudManager as pcm

# Progress Constants
STARTED = 0
PHOTOS = 10
MATCHER = 70
MESHER = 100

class ReconManager():

    def __init__(self, controller, projdir):
        """
        description about the whole class

        Args:
            controller (type?): what is it?
            projdir (type?): what is it?
        """
        self.controller = controller
        self.imgdir = None
        self.projdir = projdir
        self.progresspercent = 0
        self._update_progress("$$")

    # Main matcher pipeliningg code
    #   NOTE: This method runs in its own thread
    #   method should run all scripts accosiated with Colmap and result
    #   in a desnse reconstruction
    #   Runs matcher.py as a subprocess tracked by self.p
    def matcher(self):
        """
        description
        """
        clean = 'T'
        if (self.projdir / Path(r"database.db")).is_file():
            response = mb.askyesnocancel("Start Matcher", "Start clean and remove old database?")
            if response == None:
                return
            if response == True:
                clean = 'T'
            if response == False:
                clean = 'F'
        try:
            if self.p:
                self.cancel()
        except:
            pass
        self.controller.update_state(PHOTOS)
        self.controller.page2.cancel.config(state="active")
        self._send_log("__________Starting Matcher__________")
        colmap = Path("scripts/COLMAP.bat").resolve()
        workingdir = colmap.parent
        self.p = subprocess.Popen(['python', 'Matcher.py', self.projdir, self.imgdir, clean], cwd=str(workingdir), stdout=subprocess.PIPE, text=True)
        self._send_log()
        rcode = self.p.wait()
        if rcode == 0:
            if Path(self.projdir / "dense" / "fused.ply").is_file(): # If reconstruction exited normally
                dense = Path(self.projdir / "dense")
                pcm.create_heat_map(Path(dense / "fused.ply"), dense)
                pcm.create_height_map(Path(dense / "fused.ply"), dense)
                savefile = Path(dense / "save.ply")
                if os.path.isfile(savefile):
                    os.remove(savefile)
                shutil.copy(Path(dense / "fused.ply"), savefile)
                self.controller.update_state(MATCHER)
                self.controller.page2.cancel.config(state="disabled")
            else:
                self._send_log("Matcher failed, please retry")
        self.p = None

    # Main mesher pipeling code
    #   NOTE: This method runs in its own thread
    #   Runs mesher.py as a subprocess tracked by self.p
    def mesher(self):
        """
        description
        """
        try:
            if self.p:
                self.cancel()
        except:
            pass
        self.controller.update_state(MATCHER)
        self.controller.page2.cancel.config(state="active")
        self._send_log("__________Starting Mesher__________")
        colmap = Path("scripts/COLMAP.bat").resolve()
        workingdir = colmap.parent
        self.p = subprocess.Popen(['python', 'Mesher.py', self.projdir], cwd=str(workingdir), stdout=subprocess.PIPE, text=True)
        self._send_log()
        rcode = self.p.wait()
        if rcode == 0:
            if (self.projdir / Path(r"out\100k.obj")).is_file(): # If reconstruction exited normally
                self.controller.update_state(MESHER)
                self.controller.page2.cancel.config(state="disabled")
            else:
                self._send_log("Mesher failed, please retry")

    #  Methods for canceling current recon
    #   Should kill any active subprocess
    #   NOTE: When cancelling COLMAP, it may continur to run in the background and no longer be tracked by the app
    #   if the user runs matcher back to back the old process may conflict and need to manually be killed in task manager
    def cancel(self):
        """
        description
        """
        self.controller.page2.cancel.config(state="disabled")
        try:
            try:
                self.p.terminate()
                self.p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.p.kill()
        except:
            pass
        self._send_log("process was sent kill signal")
        self._send_log("$$")

    # method to handle auto reconstruction without setting any user bounds
    #   runs both the matcher and mesher in sequence
    def auto(self):
        """
        description
        """
        self.matcher()
        if (self.projdir / Path(r"dense\fused.ply")).is_file(): 
            self.mesher()

    # Method for updating progress bar and progress text
    #   when a process completes messages should be sent in the form: "$nextstep$""
    #   To reset the progress bar, send message "$$"
    def _update_progress(self, msg):
        """
        description

        Args:
            msg (string): what is it?
        """
        if msg == "$$":
            self.controller.page2.progress.stop()
            self.controller.style.configure('prog.Horizontal.TProgressbar', text='')
            self.controller.page2.progresstext.config(text=f"Nothing's running...")
            return
        pkg = msg.replace('$', '').split('.')
        currentstep = pkg[0]
        currentsubstep = pkg[1]
        percent = pkg[2]
        self.progresspercent = int(int(percent)/self.controller.page2.progress["maximum"] * 100) # if we only use this variable once, is it worth keeping?
        if currentsubstep == "":
            self.controller.page2.progresstext.config(text=f"Progress on {currentstep}: ")
        else:
            self.controller.page2.progresstext.config(text=f"Progress on {currentstep}, {currentsubstep}: ")
            currentstep = currentsubstep
        self.controller.style.configure('prog.Horizontal.TProgressbar', text='{:g} %'.format(self.progresspercent))
        self.controller.page2.progress.config(value=percent)
        if self.controller.page2.progress["value"] == self.controller.page2.progress["maximum"]:
            self.controller.page2.progresstext.config(text=f"{currentstep} complete!")
        
    # Method has two behaviors, if passed a string this method will act like a print() to the log
    #   if no args are provided this will capture any messages that self.p sends and send them to the log,
    #   returning when self.p finishes
    def _send_log(self, msg=None):
        """
        description

        Args:
            msg (string): what is it?
        """
        if msg:
            self.controller.page2.log(msg)
            if msg[0] == '$' and msg[-1] == '$':
                    self._update_progress(msg)
            return
        while self.p.poll() is None:
            msg = self.p.stdout.readline().strip() # read a line from the process output
            if msg:
                self.controller.page2.log(msg)
                if msg[0] == '$' and msg[-1] == '$':
                    self._update_progress(msg)