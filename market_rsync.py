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
SPLIT_MODE			= "split_1min"

CaptureName			= None
ShowSplitList		= False				# show the split options for the specified capture
ShowCaptureList 	= False 			# show the list of captures on the device
IsFollow			= False				# poll / follow mode
IsCompress			= True				# default enable compression 
IsVLANIgnore		= False				# ignore vlan information
IsVLANStrip			= False				# strip vlan header (will loose FCS)

#-------------------------------------------------------------------------------------------------------------

MarketDataGroup = {
"NASDAQ" : 
{
	# market data splits
	"MD" : [		
		{ "MCGroup" : "233.54.12.111", "Port": 26477, "VLAN" : 1273, "Prefix": "itch5"    },		# itch 5
		{ "MCGroup" : "233.54.12.45",  "Port": 26477, "VLAN" : 1273, "Prefix": "itch5psx" },		# ichh psx 
		{ "MCGroup" : "233.54.12.40",  "Port": 26475, "VLAN" : 1273, "Prefix": "itch5bx"  }			# itch bx5
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
		{ "MCGroup" : "233.125.89.24", "Port": 11064, "VLAN" : 2273, "Prefix": "nysexdp" },		# nyse XDP channel 1
		{ "MCGroup" : "233.125.89.25", "Port": 11065, "VLAN" : 2273, "Prefix": "nysexdp" },		# nyse XDP channel 2
		{ "MCGroup" : "233.125.89.26", "Port": 11066, "VLAN" : 2273, "Prefix": "nysexdp" },		# nyse XDP channel 3
		{ "MCGroup" : "233.125.89.27", "Port": 11067, "VLAN" : 2273, "Prefix": "nysexdp" }		# nyse XDP channel 4
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
		{ "MCGroup" : "224.0.59.64", "Port": 11064, "VLAN" : 2273, "Prefix": "arcaxdp" },		# arca XDP channel 1
		{ "MCGroup" : "224.0.59.65", "Port": 11065, "VLAN" : 2273, "Prefix": "arcaxdp" },		# arca XDP channel 2
		{ "MCGroup" : "224.0.59.66", "Port": 11066, "VLAN" : 2273, "Prefix": "arcaxdp" },		# arca XDP channel 3
		{ "MCGroup" : "224.0.59.67", "Port": 11067, "VLAN" : 2273, "Prefix": "arcaxdp" },		# arcaXDP channel 4
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
		{ "MCGroup" : "224.0.130.128", "Port": 30001, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 1 
		{ "MCGroup" : "224.0.130.128", "Port": 30002, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 2 
		{ "MCGroup" : "224.0.130.128", "Port": 30003, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 3 
		{ "MCGroup" : "224.0.130.128", "Port": 30004, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 4 

		{ "MCGroup" : "224.0.130.129", "Port": 30005, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 5 
		{ "MCGroup" : "224.0.130.129", "Port": 30006, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 6 
		{ "MCGroup" : "224.0.130.129", "Port": 30007, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 7 
		{ "MCGroup" : "224.0.130.129", "Port": 30008, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 8 

		{ "MCGroup" : "224.0.130.130", "Port": 30009, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 9 
		{ "MCGroup" : "224.0.130.130", "Port": 30010, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 10 
		{ "MCGroup" : "224.0.130.130", "Port": 30011, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 11
		{ "MCGroup" : "224.0.130.130", "Port": 30012, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 12 

		{ "MCGroup" : "224.0.130.131", "Port": 30013, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 13 
		{ "MCGroup" : "224.0.130.131", "Port": 30014, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 14 
		{ "MCGroup" : "224.0.130.131", "Port": 30015, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 15 
		{ "MCGroup" : "224.0.130.131", "Port": 30016, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 16 

		{ "MCGroup" : "224.0.130.132", "Port": 30017, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 17
		{ "MCGroup" : "224.0.130.132", "Port": 30018, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 18
		{ "MCGroup" : "224.0.130.132", "Port": 30019, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 19
		{ "MCGroup" : "224.0.130.132", "Port": 30020, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 20

		{ "MCGroup" : "224.0.130.133", "Port": 30021, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 21
		{ "MCGroup" : "224.0.130.133", "Port": 30022, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 22
		{ "MCGroup" : "224.0.130.133", "Port": 30023, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 23
		{ "MCGroup" : "224.0.130.133", "Port": 30024, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 24

		{ "MCGroup" : "224.0.130.134", "Port": 30025, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 25
		{ "MCGroup" : "224.0.130.134", "Port": 30026, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 26
		{ "MCGroup" : "224.0.130.134", "Port": 30027, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 27
		{ "MCGroup" : "224.0.130.134", "Port": 30028, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 28

		{ "MCGroup" : "224.0.130.135", "Port": 30029, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 29
		{ "MCGroup" : "224.0.130.135", "Port": 30030, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 30
		{ "MCGroup" : "224.0.130.135", "Port": 30031, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 31

		{ "MCGroup" : "224.0.130.136", "Port": 30032, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 32
		{ "MCGroup" : "224.0.130.136", "Port": 30033, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 33
		{ "MCGroup" : "224.0.130.136", "Port": 30034, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 34
		{ "MCGroup" : "224.0.130.136", "Port": 30035, "VLAN" : 1273, "Prefix": "batsbzx" },	# bats bzx channel 35

		# BYX

		{ "MCGroup" : "224.0.130.192", "Port": 30201, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 1
		{ "MCGroup" : "224.0.130.192", "Port": 30202, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 2
		{ "MCGroup" : "224.0.130.192", "Port": 30203, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 3
		{ "MCGroup" : "224.0.130.192", "Port": 30204, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 4

		{ "MCGroup" : "224.0.130.193", "Port": 30205, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 5
		{ "MCGroup" : "224.0.130.193", "Port": 30206, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 6
		{ "MCGroup" : "224.0.130.193", "Port": 30207, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 7
		{ "MCGroup" : "224.0.130.193", "Port": 30208, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 8

		{ "MCGroup" : "224.0.130.194", "Port": 30209, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 9
		{ "MCGroup" : "224.0.130.194", "Port": 30210, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 10
		{ "MCGroup" : "224.0.130.194", "Port": 30211, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 11
		{ "MCGroup" : "224.0.130.194", "Port": 30212, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 12

		{ "MCGroup" : "224.0.130.195", "Port": 30213, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 13
		{ "MCGroup" : "224.0.130.195", "Port": 30214, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 14
		{ "MCGroup" : "224.0.130.195", "Port": 30215, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 15
		{ "MCGroup" : "224.0.130.195", "Port": 30216, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 16

		{ "MCGroup" : "224.0.130.196", "Port": 30217, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 17
		{ "MCGroup" : "224.0.130.196", "Port": 30218, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 18
		{ "MCGroup" : "224.0.130.196", "Port": 30219, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 19
		{ "MCGroup" : "224.0.130.196", "Port": 30220, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 20

		{ "MCGroup" : "224.0.130.197", "Port": 30221, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 21 
		{ "MCGroup" : "224.0.130.197", "Port": 30222, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 22 
		{ "MCGroup" : "224.0.130.197", "Port": 30223, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 23 
		{ "MCGroup" : "224.0.130.197", "Port": 30224, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 24 

		{ "MCGroup" : "224.0.130.198", "Port": 30225, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 25 
		{ "MCGroup" : "224.0.130.198", "Port": 30226, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 26 
		{ "MCGroup" : "224.0.130.198", "Port": 30227, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 27 
		{ "MCGroup" : "224.0.130.198", "Port": 30228, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 28 

		{ "MCGroup" : "224.0.130.199", "Port": 30229, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 29 
		{ "MCGroup" : "224.0.130.199", "Port": 30230, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 30 
		{ "MCGroup" : "224.0.130.199", "Port": 30231, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 31 
		{ "MCGroup" : "224.0.130.199", "Port": 30232, "VLAN" : 1273, "Prefix": "batsbyx" },	# bats byx channel 32 

		# EDGEA

		{ "MCGroup" : "224.0.130.0",   "Port": 30301, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 1 
		{ "MCGroup" : "224.0.130.0",   "Port": 30302, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 2 
		{ "MCGroup" : "224.0.130.0",   "Port": 30303, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 3 
		{ "MCGroup" : "224.0.130.0",   "Port": 30304, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 4 

		{ "MCGroup" : "224.0.130.1",   "Port": 30305, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 5 
		{ "MCGroup" : "224.0.130.1",   "Port": 30306, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 6 
		{ "MCGroup" : "224.0.130.1",   "Port": 30307, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 7 
		{ "MCGroup" : "224.0.130.1",   "Port": 30308, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 8 

		{ "MCGroup" : "224.0.130.2",   "Port": 30309, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 9 
		{ "MCGroup" : "224.0.130.2",   "Port": 30310, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 10 
		{ "MCGroup" : "224.0.130.2",   "Port": 30311, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 11  
		{ "MCGroup" : "224.0.130.2",   "Port": 30312, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 12 

		{ "MCGroup" : "224.0.130.3",   "Port": 30313, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 13 
		{ "MCGroup" : "224.0.130.3",   "Port": 30314, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 14 
		{ "MCGroup" : "224.0.130.3",   "Port": 30315, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 15 
		{ "MCGroup" : "224.0.130.3",   "Port": 30316, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 16 

		{ "MCGroup" : "224.0.130.4",   "Port": 30317, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 17
		{ "MCGroup" : "224.0.130.4",   "Port": 30318, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 18
		{ "MCGroup" : "224.0.130.4",   "Port": 30319, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 19
		{ "MCGroup" : "224.0.130.4",   "Port": 30320, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 20

		{ "MCGroup" : "224.0.130.5",   "Port": 30321, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 21
		{ "MCGroup" : "224.0.130.5",   "Port": 30322, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 22
		{ "MCGroup" : "224.0.130.5",   "Port": 30323, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 23
		{ "MCGroup" : "224.0.130.5",   "Port": 30324, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 24

		{ "MCGroup" : "224.0.130.6",   "Port": 30325, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 25
		{ "MCGroup" : "224.0.130.6",   "Port": 30326, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 25
		{ "MCGroup" : "224.0.130.6",   "Port": 30327, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 25
		{ "MCGroup" : "224.0.130.6",   "Port": 30328, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 25

		{ "MCGroup" : "224.0.130.7",   "Port": 30329, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 29
		{ "MCGroup" : "224.0.130.7",   "Port": 30330, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 30
		{ "MCGroup" : "224.0.130.7",   "Port": 30331, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 31
		{ "MCGroup" : "224.0.130.7",   "Port": 30332, "VLAN" : 1273, "Prefix": "batsedga" },	# bats edge A channel 32

		# EDGEX

		{ "MCGroup" : "224.0.130.64",  "Port": 30401, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 1 
		{ "MCGroup" : "224.0.130.64",  "Port": 30402, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 1 
		{ "MCGroup" : "224.0.130.64",  "Port": 30403, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 1 
		{ "MCGroup" : "224.0.130.64",  "Port": 30404, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 1 

		{ "MCGroup" : "224.0.130.65",  "Port": 30405, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 5 
		{ "MCGroup" : "224.0.130.65",  "Port": 30406, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 5 
		{ "MCGroup" : "224.0.130.65",  "Port": 30407, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 5 
		{ "MCGroup" : "224.0.130.65",  "Port": 30408, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 5 

		{ "MCGroup" : "224.0.130.66",  "Port": 30409, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 9 
		{ "MCGroup" : "224.0.130.66",  "Port": 30410, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 9 
		{ "MCGroup" : "224.0.130.66",  "Port": 30411, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 9 
		{ "MCGroup" : "224.0.130.66",  "Port": 30412, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 9 

		{ "MCGroup" : "224.0.130.67",  "Port": 30413, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 13 
		{ "MCGroup" : "224.0.130.67",  "Port": 30414, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 13 
		{ "MCGroup" : "224.0.130.67",  "Port": 30415, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 13 
		{ "MCGroup" : "224.0.130.67",  "Port": 30416, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 13 

		{ "MCGroup" : "224.0.130.68",  "Port": 30417, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 17
		{ "MCGroup" : "224.0.130.68",  "Port": 30418, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 17
		{ "MCGroup" : "224.0.130.68",  "Port": 30419, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 17
		{ "MCGroup" : "224.0.130.68",  "Port": 30420, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 17

		{ "MCGroup" : "224.0.130.69",  "Port": 30421, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 21
		{ "MCGroup" : "224.0.130.69",  "Port": 30422, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 21
		{ "MCGroup" : "224.0.130.69",  "Port": 30423, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 21
		{ "MCGroup" : "224.0.130.69",  "Port": 30424, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 21

		{ "MCGroup" : "224.0.130.70",  "Port": 30425, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 25
		{ "MCGroup" : "224.0.130.70",  "Port": 30426, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 25
		{ "MCGroup" : "224.0.130.70",  "Port": 30427, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 25
		{ "MCGroup" : "224.0.130.70",  "Port": 30428, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 25

		{ "MCGroup" : "224.0.130.71",  "Port": 30429, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 29
		{ "MCGroup" : "224.0.130.71",  "Port": 30430, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 29
		{ "MCGroup" : "224.0.130.71",  "Port": 30431, "VLAN" : 1273, "Prefix": "batsedgx" },	# bats edge X channel 29
		{ "MCGroup" : "224.0.130.71",  "Port": 30432, "VLAN" : 1273, "Prefix": "batsedgx" }		# bats edge X channel 29
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

	print("market_rsync <capture name> : RSync`s market data from various exchanges")
	print("")
	print("Options:")
	print(" --https                     : use HTTPS (defaults HTTP)") 
	print(" --host <hostname>           : specify host name") 
	print(" --user <username>           : HTTP(s) username") 
	print(" --pass <password>           : HTTP(s) password") 
	print(" --output <dir>              : output directory (default ./)") 
	print(" --compress                  : compress at the source (~1Gbps throughput)") 
	print(" --list                      : list captures on the system") 
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

	SplitHMS = Split["Time"][9:17]

	FileName =  Prefix + '_' + SplitHMS + Suffix
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

	if (arg == "--splitmode"):
		SPLIT_MODE = sys.argv[ sys.argv.index(arg) + 1] ;
		i = i + 1

	if (arg == "--market"):
		MarketName = sys.argv[ sys.argv.index(arg) + 1] 
		i = i + 1

	if (arg == "--vlan-ignore"):
		IsVLANIgnore = True

	if (arg == "--vlan-strip"):
		IsVLANStrip = True

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

		FilterArg = ""
		FilterArg += "&FilterMCGroupPort=%s-%i" % (MDGroup["MCGroup"], MDGroup["Port"])

		if (IsVLANIgnore == True) :
			FilterArg += "&VLANIgnore=true"

		if (IsVLANStrip == True) :
			FilterArg += "&VLANStrip=true"

		OutputFile = "%s_%i" % (MDGroup["Prefix"], MDGroup["Port"])
		StreamFetch(Split, OutputDir + "/" + OutputFile, URLArg +  FilterArg, Suffix) 

