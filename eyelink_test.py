import pylink
from datetime import date
import os
import platform
from psychopy import core, monitors, visual
import time
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy


# Parameters
session_folder = "/Users/robwoodry/Documents/Research/PsychoPy/"
session_identifier = date.today().strftime("Test_%m%d%y.EDF")

# Set up EDF File
edf_file = date.today().strftime("T%m%d%y.EDF")

# Connect to Eyelink
ip = "100.1.1.1"
eyetracker= pylink.EyeLink(ip)

# Open an EDF file on Host PC
try:
    eyetracker.openDataFile(edf_file)
    print(edf_file, "file created on Host PC")
except RuntimeError as err:
    print('ERROR:', err)
    # Close connection
    if eyetracker.isConnected():
        eyetracker.close()
    core.quit()
    sys.exit()
    
# Add header text
preamble = 'RECORDED BY %s' % os.path.basename(__file__)
eyetracker.sendCommand("add_file_preamble_text '%s'" % preamble)

# Configure the eyetracker
eyetracker.setOfflineMode()
file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'
eyetracker.sendCommand("file_event_filter = %s" % file_event_flags)
eyetracker.sendCommand("file_sample_data = %s" % file_sample_flags)
eyetracker.sendCommand("link_event_filter = %s" % link_event_flags)
eyetracker.sendCommand("link_sample_data = %s" % link_sample_flags)

# Create display window
full_screen = False
mon = monitors.Monitor('myMonitor', width=53.0, distance=70.0)
win = visual.Window(fullscr=full_screen,
                    monitor=mon,
                    winType='pyglet',
                    units='pix')
# get the native screen resolution used by PsychoPy
scn_width, scn_height = win.size

# Pass the display pixel coordinates (left, top, right, bottom) to the tracker
# see the EyeLink Installation Guide, "Customizing Screen Settings"
el_coords = "screen_pixel_coords = 0 0 %d %d" % (scn_width - 1, scn_height - 1)
eyetracker.sendCommand(el_coords)

# Write a DISPLAY_COORDS message to the EDF file
# Data Viewer needs this piece of info for proper visualization, see Data
# Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
dv_coords = "DISPLAY_COORDS 0 0 %d %d" % (scn_width - 1, scn_height - 1)
eyetracker.sendMessage(dv_coords)

# Set up calibration graphics
genv = EyeLinkCoreGraphicsPsychoPy(eyetracker, win)
foreground_color = (-1, -1, -1)
background_color = win.color
genv.setCalibrationColors(foreground_color, background_color)
genv.setTargetType('picture')
genv.setPictureTarget(os.path.join(session_folder, 'images', 'fixTarget.bmp'))
genv.setCalibrationSounds('', '', '')

# Request Pylink to use the PsychoPy window we opened above for calibration
pylink.openGraphicsEx(genv)

# Configure eyetracker
eyetracker.doTrackerSetup()

# Start Recording
eyetracker.startRecording(1, 1, 1, 1)

# Simulate trials
print("Simulating trials...")
n_trials = 10
for i in range(n_trials):
    status_msg = 'TRIAL number %d' % i
    print(status_msg)
    eyetracker.sendMessage('TRIALID %d' % i)
    eyetracker.sendCommand("record_status_message '%s'" % status_msg)
    time.sleep(1)
    
# Close connection
if eyetracker.isConnected():
    eyetracker.stopRecording()
    print("Stopping recording...")
    # Put tracker in Offline mode
    eyetracker.setOfflineMode()
    print("Eyetracker offline...")

    # Wait 500 ms
    pylink.msecDelay(500)
    
    # Close the edf data file on the Host
    eyetracker.closeDataFile()
    print("Datafile closed on Host PC...")
    # Download the EDF data file from the Host PC to a local data folder
    # parameters: source_file_on_the_host, destination_file_on_local_drive 
    local_edf = os.path.join(session_folder, session_identifier + '.EDF') 
    print("Attempting to receive data from Host PC -> Local PC...")
    try:
        eyetracker.receiveDataFile(edf_file, local_edf)
        print("Datafile received...")
    except RuntimeError as error:
        print('ERROR:', error)
    # Close the link to the tracker.
    eyetracker.close()

print("Test shutdown...")
time.sleep(5)
core.quit()
sys.exit()


