#!/usr/bin/python
#
# fmadio capture rsync example 
#
# Change Log:
#
# 2016/01/05 : initial version. requires FW 1983+
#
#-------------------------------------------------------------------------------------------------------------

import os
import sys 
import time 
import fmadio 

fmadio.USERNAME		= "fmadio"
fmadio.PASSWORD		= "secret"
fmadio.PROTOCOL		= "http"
fmadio.HOSTNAME		= "192.168.11.95"
fmadio.CURL			= "/usr/bin/curl"
OUTDIR				= "./"
SPLIT_MODE			= "split_1min"

CaptureName			= None
ShowSplitList		= False
ShowCaptureList 	= False 

#-------------------------------------------------------------------------------------------------------------
def Help():
	print("capture_rsync <capture name> : RSync`s a capture to the local machine")
	print("")
	print("Options:")
	print(" --follow                    : run in follow/poll mode. (default false)")
	print(" --https                     : use HTTPS (defaults HTTP)") 
	print(" --host <hostname>           : specify host name") 
	print(" --user <username>           : HTTP(s) username") 
	print(" --pass <password>           : HTTP(s) password") 
	print(" --output <dir>              : output directory (default ./)") 
	print(" --splitmode <splitmode>     : select split mode (default 1min)") 
	print(" --splitlist                 : show split options") 
	print(" --list                      : show all captures on the remote machine") 

	sys.exit(0)

#-------------------------------------------------------------------------------------------------------------
# parse args 
i = 1
while (i < len(sys.argv)):
	arg = sys.argv[i]
	i = i + 1
	if (arg == sys.argv[0]): continue 

	if (arg == "--follow"):
		print("Follow Mode")
		IsFollow = True

	if (arg == "--https"):
		fmadio.PROTOCOL = "https"	
		fmadio.CURL     = fmadio.CURL + " --insecure"			# fmadio certficiate is self signed

	if (arg == "--host"):
		fmadio.HOSTNAME = sys.argv[ sys.argv.index(arg) + 1]
		i = i + 1

	if (arg == "--user"):
		fmadio.USERNAME = sys.argv[ sys.argv.index(arg) + 1]
		i = i + 1

	if (arg == "--pass"):
		fmadio.PASSWORD = sys.argv[ sys.argv.index(arg) + 1]
		i = i + 1

	if (arg == "--output"):
		OUTDIR = sys.argv[ sys.argv.index(arg) + 1]
		i = i + 1

	if (arg == "--split"):
		SPLIT_MODE = sys.argv[ sys.argv.index(arg) + 1]
		i = i + 1
	if (arg == "--splitlist"):
		ShowSplitList = True

	if (arg == "--list"):
		ShowCaptureList = True


	if (arg == "--help"):
		Help()

	if (arg[0] != "-"):
		CaptureName = arg
		print("RSync Capture Named ["+CaptureName+"]")

#-------------------------------------------------------------------------------------------------------------

# get list of streams
CaptureList 		= fmadio.StreamList()
if (len(CaptureList) == 0):
	print("No captures or bad username/password/hostname/etc")
	sys.exit(0)

if (ShowCaptureList == True):

	print("Capture List")
	for Capture in CaptureList:
		print("   " + Capture["Name"])	
	sys.exit(0)
		

# after a specific capture
Entry 		= CaptureList[0]
if (CaptureName != None):
	Entry = None
	for Capture in CaptureList:
		#print(Capture["Name"])	
		if (Capture["Name"] == CaptureName):
			Entry = Capture
			break
	if (Entry == None):
		print("Failed to find capture ["+CaptureName+"]")
		sys.exit(0)	

# get capture info 
View 		= fmadio.StreamView( Entry["Name"] )

if (ShowSplitList == True):

	print("Split Modes:")
	for Mode in View:
		print("   "+Mode["Mode"])

	sys.exit(0)

# find the split mode 
SplitView = None
for Mode in View:
	if (Mode["Mode"].strip() == SPLIT_MODE):
		SplitView = Mode 
		break

if (SplitView == None):
	print("Invalid SplitMode ["+SPLIT_MODE+"]. Use --splitlist to show options")
	sys.exit(0)

OutputDir = OUTDIR + Entry["Name"] + "_" + SPLIT_MODE
try:
	os.makedirs(OutputDir)
except:
	pass

# now sync it 

ShowGood = True 
while True:

	# get current split list
	SplitList 	= fmadio.StreamSplit( Entry["Name"], SplitView["Mode"])

	# rsync stream list to the output dir
	fmadio.StreamRSync(SplitList, OutputDir+ "/" + Entry["Name"], ShowGood) 

	# continoius follow/poll mode ? 
	if (IsFollow != True):
		break

	time.sleep(60)
	ShowGood = False

print("RSync complete")


