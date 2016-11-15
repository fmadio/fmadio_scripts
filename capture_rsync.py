#!/usr/bin/python
#
# fmadio capture rsync example 
#
# Change Log:
#
# 2016/01/24 : compressed into single file (no external deps) 
#            : added compress mode + time range modes
# 2016/01/06 : add verbose mode 
#            : support compression on download
# 2016/01/05 : initial version. requires FW 1983+
#
#-------------------------------------------------------------------------------------------------------------

import os
import sys 
import time 
import signal
import math 
import commands 
import datetime 
import ConfigParser

#-------------------------------------------------------------------------------------------------------------

USERNAME			= "fmadio"
PASSWORD			= "secret"
PROTOCOL			= "http"
HOSTNAME			= "192.168.1.1"
CURL				= "/usr/bin/curl"
VERBOSE				= False 
OUTDIR				= "./"
SPLIT_MODE			= "split_1GB"
#ZIP7_CMD			= "7z a -an -txz -si -so -m0=lzma2 -mx=9 "			# lzma2 mode at max level to use all CPU`s
																		# this is extremely slow ~ 10Mbps
ZIP7_CMD			= "7z a -an -txz -si -so -m0=lzma2 -mx=0 "			# lzma2 mode at fastest and use all CPU`s
																		# results in compression rates of ~ 700-800Mbps 
																		# on an 8 HWT system

CaptureName			= None
ShowSplitList		= False				# show the split options for the specified capture
ShowCaptureList 	= False 			# show the list of captures on the device
IsFollow			= False				# poll / follow mode
IsFilter			= False				# filter mode
IsCompressFast		= False				# fast compression mode
IsCompressUltra		= False				# use maximum compression  
IsCompressClient7z	= False				# client size 7z max compression mode 
IsSingleFile		= False				# download entire capture as a single file
StartTime			= None				# used for time based capture filtering
StopTime			= None				# used for time based capture filtering
IsStartTime			= False				# start time has been specified
IsStopTime			= False				# stop time has been specified
IsDate				= False				# date has been specified
IsVLANIgnore		= False				# ignore vlan information
IsVLANStrip			= False				# strip vlan header (will loose FCS)
IsNoProxy			= False				# disable use of http proxy 

FilterArg			= ""				# default filtering args
CompressClient 		= ""				# default client side compression args (no compress)

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
	print(" --single                    : downloads capture as a single PCAP)") 
	print(" --split <splitmode>         : select split mode (default 1GB)") 
	print(" --splitlist                 : show split options") 
	print(" --start <HH:MM:SS>          : start time") 
	print(" --stop  <HH:MM:SS>          : stop time") 
	print(" --list                      : show all captures on the remote machine") 
	print(" --compress                  : compress at the source (~1Gbps throughput)") 
	print(" --compress-xz               : client side compression 7zip maximum level (xz archive)") 
	print(" --filter <filterop>         : filter option") 
	print("                             : FilterIPHost=1.2.3.4") 
	print("                             : FilterIPHost=1.2.3.4/32") 
	print("                             : FilterIPSrc=1.2.3.0/24") 
	print("                             : FilterIPDst=1.2.3.0/24") 
	print("                             : FilterTCPPort=1234")
	print("                             : FilterTCPPort=1000-2000")
	print("                             : FilterUDPPort=1234")
	print("                             : FilterUDPPort=1000-2000")
	print("                             : FilterTCP=true")
	print("                             : FilterUDP=true")
	print("                             : FilterDNS=true")
	print("                             : FilterHTTP=true")
	print("                             : FilterHTTPS=true")
	print("                             : FilterICMP=true")
	print("                             : FilterIGMP=true")
	print(" --vlan-ignore               : ignore vlan header") 
	print(" --vlan-strip                : strips vlan header (will loose FCS)") 
	print(" --date-jp                   : specify a Japanese date YYYYMMDD (also requires start/stop time)")
	print(" --date-us                   : specify a US date       MMDDYYYY (also requires start/stop time)")
	print(" --date                      : specify a normal date   DDYMMYYY (also requires start/stop time)")
	print(" --noproxy                   : disable use of proxy") 
	print(" -v                          : verbose output") 

	sys.exit(0)

#-------------------------------------------------------------------------------------------------------------
# ctrl-c exit handler
IsExit = False
def sigint_handler(signum, frame):
	global IsExit

	# force immediate exit 
	if (IsExit == True):
		sys.exit(0)

	print('\nCtrl-C Exit Requested\n')
	IsExit = True;

signal.signal(signal.SIGINT, sigint_handler)

#######################################################################################################################
#######################################################################################################################

# str to int with default value
def default_int(Str, Default):
	try:
		return int(Str);
	except:
		return Default

#-------------------------------------------------------------------------------------------------------------
# issue CURL command
def CURLCmd(URL, Suffix = "", Silent = "-s" ):

	Cmd 	= CURL
	if (IsNoProxy == True):
		Cmd += ' --noproxy "*"'
	Cmd 	+= ' ' + Silent
	Cmd		+= ' -u ' + USERNAME + ':' + PASSWORD
	Cmd		+= ' "'+PROTOCOL+'://'+HOSTNAME+'/'+URL+'"' + Suffix

	if (VERBOSE == True):
		print("\r[%s]\n" % Cmd)
		sys.stdout.flush()

	List 	= commands.getstatusoutput(Cmd)

	#p = subprocess.Popen(shlex.split(Cmd),
	#	                 stdout=subprocess.PIPE, 
	#						 stderr=subprocess.PIPE, 
	#						 stdin=subprocess.PIPE)
	#Out =  p.communicate()

	#print("stdout", Out[0])
	#	print("stderr", Out[1])
	return List[1]

# create a hash of all streams on the device 
def StreamList():
	List = [] 

	# get all current acpture streams 
	Str = CURLCmd("/plain/list")
	Lines = Str.split("\n")
	for Line in Lines:
		L = Line.split(",")

		if (L[0].strip() == "Filename"): continue

		# ignreo the title header
		if (len(L) >= 8):
			# break each line into its components

			Name	 	= L[0].strip()	
			Bytes		= L[1]
			Packets		= L[2]
			Date		= L[3]
			URL			= L[4]

			TSStart		= default_int(L[5], 0)
			TSEnd		= default_int(L[6], TSStart)

			List.append( { "Name": Name, "Bytes":Bytes, "Packets":Packets, "Date":Date, "URL":URL, "TS":TSStart, "TSStart":TSStart, "TSEnd":TSEnd } )
			#print FileName

	# return capture list in newest first order 
	def getkey(item):
		return item["TS"]

	return sorted(List, key=getkey, reverse=True)

#-------------------------------------------------------------------------------------------------------------
# create an arrway of all views of the specified stream
def StreamView(CaptureName):

	List = [] 

	# get all current acpture streams 
	Str = CURLCmd("/plain/view?StreamName="+CaptureName)
	Lines = Str.split("\n")
	for Line in Lines:
		L = Line.split(",")

		# invalid line 
		if (len(L) != 2): continue
		
		# ignreo the title header
		if (L[0].strip() == "SplitMode"): continue

		# break each line into its components

		Mode	 	= L[0]	
		URL			= L[1]

		List.append( { "Mode":Mode, "URL":URL } )

		#print FileName

	return List

#-------------------------------------------------------------------------------------------------------------
# create list of all pcap`s for a specific view 
def StreamSplit(CaptureName, SplitMode):

	List = [] 

	# get all current acpture streams 
	Str = CURLCmd("/plain/split?StreamName="+CaptureName+"&StreamView="+SplitMode)
	Lines = Str.split("\n")
	for Line in Lines:
		L = Line.split(",")

		# invalid line 
		if (len(L) != 4): continue
		
		# ignreo the title header
		if (L[0].strip() == "Name"): continue

		# break each line into its components
		Time	 	= L[0].strip()	
		Bytes		= int(L[1])
		Packets		= int(L[2])
		URL			= L[3]

		List.append({ "Time":Time, "Bytes":Bytes, "Packets":Packets, "URL":URL })
		#print Line 

	return List

#-------------------------------------------------------------------------------------------------------------
#  rsync the stream capture files
def StreamRSync(Split, Prefix, ShowGood=True, Suffix="", URLArg = ""):

	FileName =  Prefix + '_' + Split["Time"] + Suffix
	IsDownload = True

	try:
		Size = os.path.getsize(FileName)
		dSize = Split["Bytes"] - Size

		# 2016/9/24: when compression is enabled the file size delta
		# will be very large, because it reports the uncompressed size
		# It uses uncompressed size because the system compresses on
		# download based on the requested filtering(which could be anything)
		# Thus it does not know the compressed size when spliting based 
		# on metadata
		if (IsCompressFast == True) and (Size > 0):
			IsDownload = False
			if (ShowGood == True):
				print("["+FileName+"] GOOD skipping (compressed)")

		# NOTE* 2016/01/05
		#       Split byte count is is in rounded up multiples of 256KB
		#       Its in 256KB chunks so the file splitter only looks at 
		#       the metadata. It does NOT load in actual packet data 
     	#  2016/9/19:
		#       Regressions showing delta`s of up to 512KB, thus 
		#       delta for a good acpture is 512KB now. This is
	 	#		difference of file size on the final packet of a
		#		capture only
		elif (abs(dSize) <= 2*256*1024):
			#print("file good")
			IsDownload = False
			if (ShowGood == True):
				print("["+FileName+"] GOOD skipping")
	except:
			IsDownload = True 

	# file requires downloading
	if (IsDownload == True):
		print "["+FileName+"] RSync Downloading...",
		sys.stdout.flush()
		TS0 = time.time()

		URL = Split["URL"] + URLArg

		CURLCmd(URL, CompressClient + ' > "' + FileName + '"') 
		TS1 = time.time()

		Size = os.path.getsize(FileName)
		dT = TS1 - TS0
		Bps = Size * 8 / dT
		print " %6.3f GB" % (Size / 1e9),
		print " %6.3f sec" % dT,
		print " %10.6f Gbps" % (Bps / 1e9)

#-------------------------------------------------------------------------------------------------------------
#  rsync the stream capture files
def StreamFetch(Split, Prefix, FilterArg, Suffix = ""):

	FileName =  Prefix + '_' + Split["Time"] + Suffix
	print "["+FileName+"] Fetch Downloading...",
	sys.stdout.flush()
	TS0 = time.time()

	URL = Split["URL"] + "&" + FilterArg
	CURLCmd(URL, ' > "' + FileName + '"') 
	TS1 = time.time()

	Size = os.path.getsize(FileName)
	dT = TS1 - TS0
	Bps = Size * 8 / dT
	print " %6.3f GB" % (Size / 1e9),
	print " %6.3f sec" % dT,
	print " %10.6f Gbps" % (Bps / 1e9)

#-------------------------------------------------------------------------------------------------------------
#  fetch the specific capture as a single file 
def StreamSingle(StreamName, Prefix, Suffix, StartTime = None, StopTime = None, FilterArg = None):

	FileName =  Prefix + StreamName + Suffix 
	print "["+StreamName+"] Single Downloading...\n",
	sys.stdout.flush()
	TS0 = time.time()

	#http://192.168.11.75/pcap/splittime?StreamName=check1_20160124_1019&Start=1453598396176270592ULL&Stop=1453601996176270592ULL&&
	URL = ""

	# raw full capture 
	if (StartTime == None) and (StopTime == None):
		URL = "/pcap/single?StreamName="+StreamName+"&"
	else:
		URL = "/pcap/splittime?StreamName=" + StreamName + "&"
		URL += "Start=%dULL&" % StartTime
		URL += "Stop=%dULL&" % StopTime 

	if (Suffix == ".pcap.gz"):
		URL = URL + "Compression=fast&"

	if (FilterArg != None):
		URL = URL + FilterArg

	# use os.system so stderr outputs the progress bar
	Cmd 	= CURL + ' -u ' + USERNAME + ':' + PASSWORD + ' "'+PROTOCOL+'://'+HOSTNAME+'/'+URL+'"' + ' > "' + FileName + '"' 
	if (VERBOSE == True):
		print(Cmd)

	os.system(Cmd)

	TS1 = time.time()

	Size = os.path.getsize(FileName)
	dT = TS1 - TS0
	Bps = Size * 8 / dT
	print " %6.3f GB" % (Size / 1e9),
	print " %6.3f sec" % dT,
	print " %10.6f Gbps" % (Bps / 1e9)

#-------------------------------------------------------------------------------------------------------------
# parse time string  (HH:MM:SS -> dic
def ParseTimeStr(TimeStr):

	s = TimeStr.split(":")

	Hour = float(s[0]);
	Min  = float(s[1]);
	Sec  = float(s[2]);

	return (Hour * 60 + Min) * 60 + Sec 

#-------------------------------------------------------------------------------------------------------------
# checks if Time is within the specified range 
# string like this 20151013_07:04:51.992.334.336
def ParseTimeStrSec(TimeStr):

	s = TimeStr.split("_")
	D = int(s[0])				
	p = s[1].split(".")
	T = p[0].split(":")

	Hour = float(T[0]);
	Min  = float(T[1]);
	Sec  = float(T[2]);

	#Time = (D * 24 + (Hour * 60 + Min))*60 + Sec 
	Time = (Hour * 60 + Min)*60 + Sec 

	return Time

#######################################################################################################################
#######################################################################################################################

# main program

#-------------------------------------------------------------------------------------------------------------
# system defaults from config file
try:
	Config = ConfigParser.ConfigParser()
	Config.read(os.path.expanduser('~/.fmadio.conf'))

	General = Config.options("General")
	Map = {}
	for Option in General:
		Value 		= Config.get("General", Option)
		Map[Option] = Value

	# set defaults

	USERNAME = Map.get("username", USERNAME)
	PASSWORD = Map.get("password", PASSWORD)
	HOSTNAME = Map.get("hostname", HOSTNAME)
	PROTOCOL = Map.get("protocol", PROTOCOL)

except:
	pass

#-------------------------------------------------------------------------------------------------------------
# parse args 
i = 1
while (i < len(sys.argv)):
	arg = sys.argv[i]
	i = i + 1
	if (arg == sys.argv[0]): continue 
	
	if (arg == "-v"):
		VERBOSE = True

	if (arg == "--follow"):
		print("Follow Mode")
		IsFollow = True

	if (arg == "--https"):
		PROTOCOL = "https"	
		CURL     = CURL + " --insecure"			# fmadio certficiate is self signed

	if (arg == "--host"):
		HOSTNAME = sys.argv[ sys.argv.index(arg) + 1]
		i = i + 1

	if (arg == "--user"):
		USERNAME = sys.argv[ sys.argv.index(arg) + 1]
		i = i + 1

	if (arg == "--pass"):
		PASSWORD = sys.argv[ sys.argv.index(arg) + 1]
		i = i + 1

	if (arg == "--output"):
		OUT 		= sys.argv[ sys.argv.index(arg) + 1] 
		OUTNAME 	= ""
		OUTDIR 		= ""
		if (OUT[-1] == "/"):
			OUTDIR = OUT
		else:
			Index = 0
			for j in range(1,len(OUT)): 
				Index = len(OUT) - j
				if (OUT[Index] == "/"):
					break

			OUTDIR 	= OUT[0:Index] + "/"
			OUTNAME = OUT[Index+1:] + "_"

		i = i + 1

	if (arg == "--split"):
		SPLIT_MODE = sys.argv[ sys.argv.index(arg) + 1]
		i = i + 1

	if (arg == "--splitlist"):
		ShowSplitList = True

	if (arg == "--single"):
		IsSingleFile = True

	if (arg == "--list"):
		ShowCaptureList = True

	if (arg == "--filter"):
		IsFilter = True
		FilterArg += sys.argv[ sys.argv.index(arg) + 1] + "&"
		i = i + 1

	if (arg == "--compress"):
		IsCompressFast = True;

	if (arg == "--compress-xz"):
		IsCompressClient7z = True;
		CompressClient		= " | " + ZIP7_CMD;

	if (arg == "--start"):
		StartTimeStr = sys.argv[ sys.argv.index(arg) + 1]
		StartTime = ParseTimeStr( StartTimeStr ) 
		i = i + 1
		IsStartTime = True;

	if (arg == "--stop"):
		StopTimeStr = sys.argv[ sys.argv.index(arg) + 1]
		StopTime = ParseTimeStr(StopTimeStr)
		i = i + 1
		IsStopTime = True;

	if (arg == "--vlan-ignore"):
		IsVLANIgnore = True
		FilterArg += "VLANIgnore=true&"

	if (arg == "--vlan-strip"):
		IsVLANStrip = True
		FilterArg += "VLANStrip=true&"

	# japanese style dates YYYYMMDD
	if (arg == "--date-jp"):
		IsDate 		= True
		DateStr 	= sys.argv[ sys.argv.index(arg) + 1]
		DateFormat	= "%Y%m%d"
		i = i + 1

	# us style dates MMDDYYYY
	if (arg == "--date-us"):
		IsDate 		= True
		DateStr 	= sys.argv[ sys.argv.index(arg) + 1]
		DateFormat	= "%m%d%Y"
		i = i + 1

	# normal style dates DDMMYYYY
	if (arg == "--date"):
		IsDate 		= True
		DateStr 	= sys.argv[ sys.argv.index(arg) + 1]
		DateFormat	= "%d%m%Y"
		i = i + 1

	if (arg == "--noproxy"):
		IsNoProxy = True;

	if (arg == "--help"):
		Help()

	if (arg[0] != "-"):
		CaptureName = arg
		print("RSync Capture Named ["+CaptureName+"]")

#-------------------------------------------------------------------------------------------------------------

# get list of streams
CaptureList 		= StreamList()
if (len(CaptureList) == 0):
	print("No captures or bad username/password/hostname/etc")
	sys.exit(0)

if (ShowCaptureList == True):

	print("Capture List")
	for Capture in CaptureList:
		dTS = Capture["TSEnd"] - Capture["TSStart"]
		print("%-60s %s %8.2f min " % (Capture["Name"], Capture["Date"], dTS / 60e9) )	
	sys.exit(0)

Entry = None; 

# searching for a specific date / time		
if (IsDate == True):
	if (IsStartTime != True) or (IsStopTime != True):
		print("Must specifict start/stop time with --start HH:MM:SS --stop HH:MM:SS")
		sys.exit(0)

	StartTS	= time.mktime( time.strptime(DateStr+" "+StartTimeStr, DateFormat+" %H:%M:%S")) * 1e9
	StopTS  = time.mktime( time.strptime(DateStr+" "+StopTimeStr , DateFormat+" %H:%M:%S")) * 1e9

	# search capture list for start/stop times
	print("Searching %s [%s]-[%s]\n" % (DateStr, StartTimeStr, StopTimeStr) )
	for Capture in CaptureList:

		# TSStart/End is in UTC
		if (Capture["TSStart"] < StartTS) and (Capture["TSEnd"] > StopTS):
			print("found capture: " + Capture["Name"])	
			Entry 		= Capture
			CaptureName = Capture["Name"]
			break

	if (Entry == None):
		print("Failed to find capture on [%s] between [%s]->[%s]\n" % ( DateStr, StartTimeStr, StopTimeStr) )
		sys.exit(0)	

# use a specific capture name  
elif (CaptureName != None):
	Entry = None
	for Capture in CaptureList:
		#print(Capture["Name"])	
		if (Capture["Name"] == CaptureName):
			Entry = Capture
			break
	if (Entry == None):
		print("Failed to find capture ["+CaptureName+"]")
		sys.exit(0)	

# use the latest capture file
else:
	Entry 		= CaptureList[0]
	for Capture in CaptureList:
		# search for newer capture
		if (Capture["TSStart"] > Entry["TSEnd"]):
			Entry 		= Capture
			print("new capture")

# get capture info 
View 		= StreamView( Entry["Name"] )
if (ShowSplitList == True):
	print("Split Modes:")
	for Mode in View:
		print("   "+Mode["Mode"])

	sys.exit(0)

# download as single file
if (IsSingleFile == True):
	Suffix = ".pcap"
	if (IsCompressFast == True):
		print("Single PCAP Compressed")
		Suffix = ".pcap.gz"
	else:
		print("Single PCAP")

	# calculte timezone with minium number of external deps
	# local time == (utc time + utc offset)
	millis 		= 1288483950000
	ts 			= millis * 1e-3
	utc_offset 	= datetime.datetime.fromtimestamp(ts) - datetime.datetime.utcfromtimestamp(ts)
	print("TZ Offset %d Sec" % utc_offset.seconds)

	# convert time into epoch ns 
	# NOTE: be areful with the timezone as it crosses midnight 
	TSBase = math.floor((Entry["TSEnd"] + utc_offset.seconds * 1e9 ) / (24*60*60*1e9)) * 24*60*60*1e9
	if (StartTime != None):
		StartTime = TSBase  + StartTime * 1e9  - utc_offset.seconds*1e9 

	if (StopTime != None):
		StopTime = TSBase + StopTime * 1e9 - utc_offset.seconds * 1e9 

	# download single pcap 
	StreamSingle(CaptureName, OUTDIR + "/" + OUTNAME, Suffix, StartTime, StopTime, FilterArg)
	sys.exit(0);

# find the split mode 
SplitView = None
for Mode in View:
	if (Mode["Mode"].strip() == SPLIT_MODE):
		SplitView = Mode 
		break

if (SplitView == None):
	print("Invalid SplitMode ["+SPLIT_MODE+"]. Use --splitlist to show options")
	sys.exit(0)

# make the output directory
OutputDir = OUTDIR
if (OUTDIR[-1] != "/"):
	OutputDir += + "_"
OutputDir += Entry["Name"] + "_" + SPLIT_MODE

try:
	os.makedirs(OutputDir)
except:
	pass

# regressions use this line
print("OutputDir: %s" % OutputDir)

# decide on filename suffix 
URLArg = ""
Suffix = ".pcap"
if (IsCompressFast == True):
	Suffix = ".pcap.gz"
	URLArg = "&Compression=fast"

#if (IsCompressMax == True):
#	Suffix = ".pcap.gz"
#	URLArg = "&Compression=max"

if (IsCompressClient7z == True):
	Suffix = ".pcap.xz"
	URLArg = ""

#-------------------------------------------------------------------------------------------------------------

def StreamDownload(EntryName, SplitMode, ShowGood, FetchLast):

	# get current split list
	SplitList 	= StreamSplit(EntryName, SplitMode) 

	# generate numeric time 
	for Split in SplitList:
		Split["TimeSec"] = ParseTimeStrSec(Split["Time"])

	for idx,Split in enumerate(SplitList):

		Prefix = OutputDir+ "/" + EntryName + "_"

		#  filter based on time range (if specified)
		if (StopTime != None) and (Split["TimeSec"] > StopTime):
			print "["+Prefix + "_" + Split["Time"] + Suffix + "] Skip (StopTime)"
			continue;

		if (StartTime != None) and (SplitList[idx+1] != None):
			if (SplitList[idx+1]["TimeSec"] < StartTime):
				print "["+Prefix + "_" + Split["Time"] + Suffix + "] Skip (StartTime)"
				continue;

		# in follow mode wait for the entry to finish before downloading 
		# e.g. not the currently capturing file (occours when capture speed < download speed)
		if (FetchLast == False) and (Split == SplitList[-1]):
			print "["+Prefix + "_" + Split["Time"] + Suffix + "] Skip (Follow tail)"
			continue;

		# rsync stream list to the output dir
		StreamRSync(	Split, 
						Prefix,	
						ShowGood, 
						Suffix,
						URLArg)


#-------------------------------------------------------------------------------------------------------------
# intelligent rsync mode  (no filters)
if (IsFilter == False):

	ShowGood = True 

	# grab everythingat one time and done
	if (IsFollow == False):
		StreamDownload(Entry["Name"], SplitView["Mode"], ShowGood, True)	

	# follow mode
	if (IsFollow == True):
		while True:

			# grab everything except the latest split 
			StreamDownload(Entry["Name"], SplitView["Mode"], ShowGood, False)	

			# ensure we`re grabbing the last capture when in follow mode
			# e.g. during midnight roll in follow mode 
			if (CaptureName == None):	
				CaptureList 	= StreamList()

				# midnight roll occoured
				if (Entry["Name"] != CaptureList[0]["Name"]):

					print("Capture Name changed")
					print(Entry)
					print(CaptureList[0])

					# grab everything including the last entry
					StreamDownload(Entry["Name"], SplitView["Mode"], ShowGood, True)	

					# switch to new stream 
					Entry 			= CaptureList[0]

			# user requested exit. in follow mode it needs to
			# download the final pcap
			if (IsExit == True):
				print("Follow Ctrl-C")
				# grab everything including the last entry
				StreamDownload(Entry["Name"], SplitView["Mode"], ShowGood, True)	
				break

			print("["+time.strftime("%y-%m-%d %H:%M")+"] Follow Mode Sleeping...")
			time.sleep(10)
			ShowGood = False

	print("RSync complete")


#-------------------------------------------------------------------------------------------------------------
# filters have been applied
else:
	# follow mode with filtering requires different code path
	# it requires 
	# 1) to not download the last item 
	# 2) keep a list of already downloaded splits
	if (IsFollow == True):

		DownloadList = {} 
		LastDownload = None
		while True:

			# get current split list
			SplitList 	= StreamSplit( Entry["Name"], SplitView["Mode"])

			# dont download last item	
			LastIndex 	 = len(SplitList) - 1
			LastDownload = SplitList[ LastIndex ] 
			SplitList.pop( LastIndex ) 

			# build list of new splits
			NewList = []	
			for Split in SplitList:
				Key = Split["Time"]
				if (DownloadList.get(Key) == None):
					DownloadList[Key] = True 
					NewList.append(Split)

			# fetch each new stream 
			for idx,Split in enumerate(NewList):
				StreamFetch(Split, OutputDir + "/" + Entry["Name"] + "_", FilterArg, Suffix) 

			print("Sleeping...")
			sys.stdout.flush()
			time.sleep(5)

	# without follow mode  
	else:

		# get current split list
		SplitList 	= StreamSplit( Entry["Name"], SplitView["Mode"])

		# generate numeric time 
		for Split in SplitList:
			Split["TimeSec"] = ParseTimeStrSec(Split["Time"])

		for idx,Split in enumerate(SplitList):

			Prefix = OutputDir+ "/" + Entry["Name"] + "_"

			#  filter based on time range (if specified)
			if (StopTime != None) and (Split["TimeSec"] > StopTime):
				print "["+Prefix + "_" + Split["Time"] + Suffix + "] Skip (StopTime)"
				continue;

			if (StartTime != None) and (len(SplitList) > idx + 1) and (SplitList[idx+1] != None):
				if (SplitList[idx+1]["TimeSec"] < StartTime):
					print "["+Prefix + "_" + Split["Time"] + Suffix + "] Skip (StartTime)"
					continue;

			# download 
			StreamFetch(Split, OutputDir + "/" + Entry["Name"] + "_", FilterArg, Suffix) 

	print("FilterSync complete")
