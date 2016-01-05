#!/usr/bin/python
#
# fmadio utility library 
#
# Change Log:
#
# 2016/01/05 : initial version. requires FW 1983+
#
#-------------------------------------------------------------------------------------------------------------

import sys 
import os
import commands 
import time 

#SPLIT_MODE	= "1sec"
#USERNAME	= "fmadio"
#PASSWORD	= "100g"
#HOSTNAME	= "192.168.11.95"
#CURL		= "/usr/bin/curl"
#OUTDIR		= "/tmp/"

#-------------------------------------------------------------------------------------------------------------
# issue CURL command
def CURLCmd( URL, Suffix = "" ):

	Cmd 	= CURL + ' -s -u ' + USERNAME + ':' + PASSWORD + ' "'+PROTOCOL+'://'+HOSTNAME+'/'+URL+'"' + Suffix
	#print Cmd
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

		# ignreo the title header
		if (len(L) != 8): continue
		if (L[0].strip() == "Filename"): continue

		# break each line into its components

		Name	 	= L[0].strip()	
		Bytes		= L[1]
		Packets		= L[2]
		Date		= L[3]
		URL			= L[4]
		TS			= int(L[6])

		List.append( { "Name": Name, "Bytes":Bytes, "Packets":Packets, "Date":Date, "URL": URL, "TS":TS } )
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
		Time	 	= L[0]	
		Bytes		= int(L[1])
		Packets		= int(L[2])
		URL			= L[3]

		List.append({ "Time":Time, "Bytes":Bytes, "Packets":Packets, "URL":URL })

		#print FileName

	return List

#-------------------------------------------------------------------------------------------------------------
#  rsync the stream capture files
def StreamRSync(SplitList, Prefix, ShowGood=True):
	for Split in SplitList:

		FileName =  Prefix + '_' + Split["Time"]
		IsDownload = True
		try:
			Size = os.path.getsize(FileName)

			# NOTE* 2016/01/05
			#       Split byte count is is in rounded up multiples of 256KB
			#       Its in 256KB chunks so the file splitter only looks at 
			#       the metadata. It does NOT load in actual packet data 
			dSize = Split["Bytes"] - Size
			if (abs(dSize) <= 256*1024):
				#print("file good")
				IsDownload = False
				if (ShowGood == True):
					print("["+FileName+"] GOOD skipping")
		except:
				IsDownload = True 

		# file requires downloading
		if (IsDownload == True):
			print "["+FileName+"] Downloading...",
			sys.stdout.flush()
			TS0 = time.time()
			CURLCmd(Split["URL"], ' > "' + FileName + '"') 
			TS1 = time.time()

			Size = os.path.getsize(FileName)
			dT = TS1 - TS0
			Bps = Size * 8 / dT
			print " %6.3f GB" % (Size / 1e9),
			print " %6.3f sec" % dT,
			print " %10.6f Gbps" % (Bps / 1e9)


#-------------------------------------------------------------------------------------------------------------

