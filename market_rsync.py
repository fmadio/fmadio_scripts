#!/usr/bin/python
#
# fmadio capture rsync example 
#
#-------------------------------------------------------------------------------------------------------------

import os
import sys 
import time 
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
SPLIT_MODE			= "split_15min"

CaptureName			= None
ShowSplitList		= False				# show the split options for the specified capture
ShowCaptureList 	= False 			# show the list of captures on the device
IsFollow			= False				# poll / follow mode
IsCompress			= True				# default enable compression 

#-------------------------------------------------------------------------------------------------------------

MarketDataGroup = {
"NASDAQ" : 
{
	# market data splits
	"MD" : [		
		{ "MCGroup" : "223.54.12.111", "Port": 26477, "VLAN" : 1273, "Prefix": "ITCH5"     },			# itch 5
		{ "MCGroup" : "223.54.12.45",  "Port": 26477, "VLAN" : 1273, "Prefix": "ITCH5_PAX" },			# ichh pax5
		{ "MCGroup" : "223.54.12.40",  "Port": 26475, "VLAN" : 1273, "Prefix": "ITCH5_BX"  }			# itch bx5
	],
	# include order/entry ip`s
    "OE" : [
	]
}
,
"NYSE" : 
{
	# market data splits
	"MD" : [		
		{ "MCGroup" : "233.125.69.24", "Port": 11064, "VLAN" : 2273, "Prefix": "NYSE_XDP_CH1" },	# nyse XDP channel 1
		{ "MCGroup" : "233.125.69.25", "Port": 11065, "VLAN" : 2273, "Prefix": "NYSE_XDP_CH2" },	# nyse XDP channel 2
		{ "MCGroup" : "233.125.69.26", "Port": 11066, "VLAN" : 2273, "Prefix": "NYSE_XDP_CH3" },	# nyse XDP channel 3
		{ "MCGroup" : "233.125.69.27", "Port": 11067, "VLAN" : 2273, "Prefix": "NYSE_XDP_CH4" }		# nyse XDP channel 4
	],
	# include order/entry ip`s
    "OE" : [
	]
}
,
"ARCA" : 
{
	# market data splits
	"MD" : [		
		{ "MCGroup" : "224.0.59.64", "Port": 11064, "VLAN" : 2273, "Prefix": "ARCA_XDP_CH1" },		# arca XDP channel 1
		{ "MCGroup" : "224.0.59.65", "Port": 11064, "VLAN" : 2273, "Prefix": "ARCA_XDP_CH2" },		# arca XDP channel 2
		{ "MCGroup" : "224.0.59.66", "Port": 11064, "VLAN" : 2273, "Prefix": "ARCA_XDP_CH3" },		# arca XDP channel 3
		{ "MCGroup" : "224.0.59.67", "Port": 11064, "VLAN" : 2273, "Prefix": "ARCA_XDP_CH4" },		# arcaXDP channel 4
	],
	# include order/entry ip`s
    "OE" : [
	]
}
,
"BATS" : 
{
	# market data splits
	"MD" : [		
		{ "MCGroup" : "224.0.130.128", "Port": 30000, "VLAN" : 1273, "Prefix": "BATS_BZX_CH01" },	# bats bzx channel 1 
		{ "MCGroup" : "224.0.130.129", "Port": 30005, "VLAN" : 1273, "Prefix": "BATS_BZX_CH05" },	# bats bzx channel 5 
		{ "MCGroup" : "224.0.130.130", "Port": 30009, "VLAN" : 1273, "Prefix": "BATS_BZX_CH09" },	# bats bzx channel 9 
		{ "MCGroup" : "224.0.130.131", "Port": 30013, "VLAN" : 1273, "Prefix": "BATS_BZX_CH13" },	# bats bzx channel 13 
		{ "MCGroup" : "224.0.130.132", "Port": 30017, "VLAN" : 1273, "Prefix": "BATS_BZX_CH17" },	# bats bzx channel 17
		{ "MCGroup" : "224.0.130.133", "Port": 30021, "VLAN" : 1273, "Prefix": "BATS_BZX_CH21" },	# bats bzx channel 21
		{ "MCGroup" : "224.0.130.134", "Port": 30025, "VLAN" : 1273, "Prefix": "BATS_BZX_CH25" },	# bats bzx channel 25
		{ "MCGroup" : "224.0.130.135", "Port": 30029, "VLAN" : 1273, "Prefix": "BATS_BZX_CH29" },	# bats bzx channel 29
		{ "MCGroup" : "224.0.130.136", "Port": 30032, "VLAN" : 1273, "Prefix": "BATS_BZX_CH33" },	# bats bzx channel 33

		{ "MCGroup" : "224.0.130.192", "Port": 30201, "VLAN" : 1273, "Prefix": "BATS_BYX_CH01" },	# bats byx channel 1
		{ "MCGroup" : "224.0.130.193", "Port": 30205, "VLAN" : 1273, "Prefix": "BATS_BYX_CH05" },	# bats byx channel 5
		{ "MCGroup" : "224.0.130.194", "Port": 30209, "VLAN" : 1273, "Prefix": "BATS_BYX_CH09" },	# bats byx channel 9
		{ "MCGroup" : "224.0.130.195", "Port": 30213, "VLAN" : 1273, "Prefix": "BATS_BYX_CH13" },	# bats byx channel 13
		{ "MCGroup" : "224.0.130.196", "Port": 30217, "VLAN" : 1273, "Prefix": "BATS_BYX_CH17" },	# bats byx channel 17
		{ "MCGroup" : "224.0.130.197", "Port": 30221, "VLAN" : 1273, "Prefix": "BATS_BYX_CH21" },	# bats byx channel 21 
		{ "MCGroup" : "224.0.130.198", "Port": 30225, "VLAN" : 1273, "Prefix": "BATS_BYX_CH25" },	# bats byx channel 25 
		{ "MCGroup" : "224.0.130.199", "Port": 30229, "VLAN" : 1273, "Prefix": "BATS_BYX_CH29" },	# bats byx channel 29 

		{ "MCGroup" : "224.0.130.0",   "Port": 30301, "VLAN" : 1273, "Prefix": "BATS_EDGEA_CH01" },	# bats edge A channel 1 
		{ "MCGroup" : "224.0.130.1",   "Port": 30305, "VLAN" : 1273, "Prefix": "BATS_EDGEA_CH05" },	# bats edge A channel 5 
		{ "MCGroup" : "224.0.130.2",   "Port": 30309, "VLAN" : 1273, "Prefix": "BATS_EDGEA_CH09" },	# bats edge A channel 9 
		{ "MCGroup" : "224.0.130.3",   "Port": 30313, "VLAN" : 1273, "Prefix": "BATS_EDGEA_CH13" },	# bats edge A channel 13 
		{ "MCGroup" : "224.0.130.4",   "Port": 30317, "VLAN" : 1273, "Prefix": "BATS_EDGEA_CH17" },	# bats edge A channel 17
		{ "MCGroup" : "224.0.130.5",   "Port": 30321, "VLAN" : 1273, "Prefix": "BATS_EDGEA_CH21" },	# bats edge A channel 21
		{ "MCGroup" : "224.0.130.6",   "Port": 30325, "VLAN" : 1273, "Prefix": "BATS_EDGEA_CH25" },	# bats edge A channel 25
		{ "MCGroup" : "224.0.130.7",   "Port": 30329, "VLAN" : 1273, "Prefix": "BATS_EDGEA_CH29" },	# bats edge A channel 29

		{ "MCGroup" : "224.0.130.64",  "Port": 30401, "VLAN" : 1273, "Prefix": "BATS_EDGEX_CH01" },	# bats edge X channel 1 
		{ "MCGroup" : "224.0.130.65",  "Port": 30405, "VLAN" : 1273, "Prefix": "BATS_EDGEX_CH05" },	# bats edge X channel 5 
		{ "MCGroup" : "224.0.130.66",  "Port": 30409, "VLAN" : 1273, "Prefix": "BATS_EDGEX_CH09" },	# bats edge X channel 9 
		{ "MCGroup" : "224.0.130.67",  "Port": 30413, "VLAN" : 1273, "Prefix": "BATS_EDGEX_CH13" },	# bats edge X channel 13 
		{ "MCGroup" : "224.0.130.68",  "Port": 30417, "VLAN" : 1273, "Prefix": "BATS_EDGEX_CH17" },	# bats edge X channel 17
		{ "MCGroup" : "224.0.130.69",  "Port": 30421, "VLAN" : 1273, "Prefix": "BATS_EDGEX_CH21" },	# bats edge X channel 21
		{ "MCGroup" : "224.0.130.70",  "Port": 30425, "VLAN" : 1273, "Prefix": "BATS_EDGEX_CH25" },	# bats edge X channel 25
		{ "MCGroup" : "224.0.130.71",  "Port": 30429, "VLAN" : 1273, "Prefix": "BATS_EDGEX_CH29" }	# bats edge X channel 29
	],
	# include order/entry ip`s
    "OE" : [
	]
}
,
"TSE" : 
{
	# market data splits
	"MD" : [		
		{ "MCGroup" : "239.194.1.1", "Port": 51050, "VLAN" : None, "Prefix" : "TSE_FLEXFULL_FeedA" },	# japan tse flex FULL feed A channel 0 
		{ "MCGroup" : "239.194.2.1", "Port": 52050, "VLAN" : None, "Prefix" : "TSE_FLEXFULL_FeedB" },	# japan tse flex FULL feed B channel 0 
		{ "MCGroup" : "239.194.3.1", "Port": 51550, "VLAN" : None, "Prefix" : "TSE_FLEXFULL_FeedA" },	# japan tse flex WB   feed A channel 0 
		{ "MCGroup" : "239.194.4.1", "Port": 52550, "VLAN" : None, "Prefix" : "TSE_FLEXFULL_FeedB" },	# japan tse flex WB   feed B channel 0 
	],
	# include order/entry ip`s
    "OE" : [
	]
}
,
"JNX" : 
{
	# market data splits
	"MD" : [		
		{ "MCGroup" : "232.65.1.1", "Port": 11002, "VLAN" : None, "Prefix" : "JNX_DAYU_FeedA" },	# sbi japan next U market Feed A
		{ "MCGroup" : "232.65.2.1", "Port": 11002, "VLAN" : None, "Prefix" : "JNX_DAYU_FeedB" },	# sbi japan next U market Feed B

		{ "MCGroup" : "232.65.1.2", "Port": 11002, "VLAN" : None, "Prefix" : "JNX_DAY_FeedA" },		# sbi japan next market Feed A
		{ "MCGroup" : "232.65.2.2", "Port": 11002, "VLAN" : None, "Prefix" : "JNX_DAY_FeedB" },		# sbi japan next market Feed B

		{ "MCGroup" : "232.65.1.3", "Port": 11002, "VLAN" : None, "Prefix" : "JNX_DAYX_FeedA" },	# sbi japan next X market Feed A
		{ "MCGroup" : "232.65.2.3", "Port": 11002, "VLAN" : None, "Prefix" : "JNX_DAYX_FeedB" }		# sbi japan next X market Feed B
	],
	# include order/entry ip`s
    "OE" : [
	]
}
}

#-------------------------------------------------------------------------------------------------------------

def Help():

	print("capture_rsync <capture name> : RSync`s a capture to the local machine")
	print("")
	print("Options:")
	print(" --                    : run in follow/poll mode. (default false)")
	print(" --https                     : use HTTPS (defaults HTTP)") 
	print(" --host <hostname>           : specify host name") 
	print(" --user <username>           : HTTP(s) username") 
	print(" --pass <password>           : HTTP(s) password") 
	print(" --output <dir>              : output directory (default ./)") 
	print(" --compress                  : compress at the source (~1Gbps throughput)") 
	print(" --vlan-ignore               : ignore vlan header") 
	print(" --vlan-strip                : strips vlan header (will loose FCS)") 
	print(" --market <name>             : specify market to extract") 
	print("                             : NASDAQ") 
	print("                             : NYSE") 
	print("                             : ARCA") 
	print("                             : BATS") 
	print("                             : TSE") 
	print("                             : JNX") 
	print("                             : JCHIX") 
	print(" -v                          : verbose output") 

	sys.exit(0)

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
def CURLCmd( URL, Silent = "-s", Suffix = "" ):

	Cmd 	= CURL + ' ' + Silent + ' -u ' + USERNAME + ':' + PASSWORD + ' "'+PROTOCOL+'://'+HOSTNAME+'/'+URL+'"' + Suffix
	if (VERBOSE == True):
		print("\r[%s]\n" % Cmd)

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

			TSStart		= default_int(L[6], 0)
			TSEnd		= default_int(L[7], TSStart)

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

		#print FileName

	return List

#-------------------------------------------------------------------------------------------------------------
#  rsync the stream capture files
def StreamFetch(Split, Prefix, FilterArg, Suffix = ""):

	FileName =  Prefix + '_' + Split["Time"] + Suffix
	FileName = FileName.replace(":", "_")

	FileNameStr = "%-90s" % FileName 
	print "["+FileNameStr+"] Downloading...",
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
MarketName = None;
while (i < len(sys.argv)):
	arg = sys.argv[i]
	i = i + 1
	if (arg == sys.argv[0]): continue 
	
	if (arg == "-v"):
		VERBOSE = True

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
		OUTDIR 		= sys.argv[ sys.argv.index(arg) + 1] 
		i = i + 1

	if (arg == "--list"):
		ShowCaptureList = True;

	if (arg == "--compress"):
		IsCompressFast = True;

	if (arg == "--market"):
		MarketName = sys.argv[ sys.argv.index(arg) + 1] 

	if (arg == "--help"):
		Help()




	if (arg[0] != "-"):
		CaptureName = arg
		print("RSync Capture Named ["+CaptureName+"]")

#-------------------------------------------------------------------------------------------------------------
# check market was specified 
if (MarketName == None):
	print("Missing Market Name\n")
	Help()
	sys.exit(0)

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

# find the capture name
Entry 	= None; 
for Capture in CaptureList:
	if (Capture["Name"] == CaptureName):
		print("Found ["+CaptureName+"]")
		Entry 	= Capture 

# get capture info 
View 		= StreamView( Entry["Name"] )

# find the split mode 
SplitView = None
for Mode in View:
	if (Mode["Mode"].strip() == SPLIT_MODE):
		SplitView = Mode 
		print("Found SplitMode ["+SPLIT_MODE+"]")
		break

if (SplitView == None):
	print("Invalid SplitMode ["+SPLIT_MODE+"]. Use --splitlist to show options")
	sys.exit(0)

# make the output directory
OutputDir = OUTDIR

try:
	os.makedirs(OutputDir)
except:
	pass

# decide on filename suffix 
URLArg = ""
Suffix = ".pcap"
if (IsCompress == True):
	Suffix = ".pcap.gz"
	URLArg = "&Compression=fast"

# get current split list
SplitList = StreamSplit( Entry["Name"], SplitView["Mode"])

for Split in SplitList:
	URL 		= Split				["URL"] 
	Exchange 	= MarketDataGroup	[MarketName]
	MD			= Exchange		 	["MD"] 

	for MDGroup in MD :
		FilterArg = "&FilterIPDst="+MDGroup["MCGroup"]
		OutputFile = MDGroup["Prefix"]

		StreamFetch(Split, OutputDir + "/" + OutputFile, URLArg +  FilterArg, Suffix) 

