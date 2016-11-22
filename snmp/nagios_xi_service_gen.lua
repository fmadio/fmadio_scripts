#!/usr/bin/lua
-- 
--  generates nagios_xi services generation file 
--
--
function trace(Message, ...)
	io.stdout:write( string.format(Message, unpack({...})))
end

function ctrace(C, Message, ...)
	C:write( string.format(Message, unpack({...})))
end

DeviceTarget = nil						-- which fmad system to generate for
Host		= nil						-- monitoring hostname

local Help = function()

	trace("nagios_xi_service_gen.lua:\n")	
	trace(" --help                           : show help info\n")
	trace(" --host <ipaddress>               : set the host IP address\n")
	trace(" --fmad20-1u-16t                  : generate for fmad20 1U 16TB system\n")
end

local a = 1
while a <= #arg do 
	local b = arg[a]

	if (b == "--fmadio20-1u-16t") 	then DeviceTarget = "fmadio20" end
	if (b == "--host") 				then Host = arg[a+1]; a = a + 1; end 
	if (b == "--help") 				then Help(); return end 

	a = a + 1
end

if (DeviceTarget == nil) then 
	trace("ERROR: Invalid Device (e.g. specify --fmadio20-16t)\n");
	Help(); 
	return 
end
if (Host == nil) then 
	trace("ERROR: Invalid Host(e.g. specify --host 192.168.1.1)\n");
	Help(); 
	return 
end


trace("Generating for [%s] at host [%s]\n", DeviceTarget, Host)



local Config = io.open(Host..".cfg", "w")
assert(Config ~= nil)

ctrace(Config, "# Generated on "..os.date().." by nagios_xi_service_gen.lua\n")


local DeviceServiceGen = function(Desc, Use, CheckCmd)

	ctrace(Config, "define service {\n")
	ctrace(Config, "    host_name               "..Host.."\n")
	ctrace(Config, "    service_description     "..Desc.."\n")	
	ctrace(Config, "    use                     "..Use.."\n")
	ctrace(Config, "    check_command           "..CheckCmd.."\n")
	ctrace(Config, "    max_check_attempts      5\n")
	ctrace(Config, "    check_interval          1\n")
	ctrace(Config, "    retry_interval          1\n")
	ctrace(Config, "    check_period            xi_timeperiod_24x7\n")
	ctrace(Config, "    notification_interval   60\n")
	ctrace(Config, "    notification_period     xi_timeperiod_24x7\n")
	ctrace(Config, "    contacts                nagiosadmin\n")
	ctrace(Config, "    _xiwizard               linuxsnmp\n")
	ctrace(Config, "    register                1\n")
	ctrace(Config, "}\n")
end

-- common stats
DeviceServiceGen("System CPU Usage",				"xiwizard_linuxsnmp_load", 					"check_xi_service_snmp_linux_load! -C public --v2c -w 80 -c 90 -f")
DeviceServiceGen("System Ping",						"xiwizard_switch_ping_service",				"check-host-alive")	
DeviceServiceGen("System Uptime",					"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.2.1.1.3.0 -C public -P 2c")
DeviceServiceGen("System Name",						"xiwizard_linuxsnmp_load",					"check_xi_service_snmp! -o .1.3.6.1.2.1.1.5.0  -C public -P 2c")

-- port status

DeviceServiceGen("System Bandwidth Management 1G",	"xiwizard_switch_port_bandwidth_service",	"check_xi_service_mrtgtraf!192.168.1.75_5.rrd!500.00,500.00!800.00,800.00!M")
DeviceServiceGen("System Link Management 1G",		"xiwizard_switch_port_status_service",		"check_xi_service_ifoperstatus!public!5!-v 2 -p 161")

DeviceServiceGen("System Bandwidth Management 10G",	"xiwizard_switch_port_bandwidth_service",	"check_xi_service_mrtgtraf!192.168.1.75_17.rrd!5.00,5.00!8.00,8.00!G")
DeviceServiceGen("System Link Management 10G",		"xiwizard_switch_port_status_service",		"check_xi_service_ifoperstatus!public!17!-v 2 -p 161")

DeviceServiceGen("System Bandwidth Aux 10G",		"xiwizard_switch_port_bandwidth_service",	"check_xi_service_mrtgtraf!192.168.1.75_17.rrd!5.00,5.00!8.00,8.00!G")
DeviceServiceGen("System Link Aux 10G",				"xiwizard_switch_port_status_service",		"check_xi_service_ifoperstatus!public!17!-v 2 -p 161")

-- capture status 
DeviceServiceGen("Total Packets Recevied",			"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.1.0 -C public -P 2c")
DeviceServiceGen("Total Packets Dropped",			"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.2.0 -C public -P 2c")
DeviceServiceGen("Total Packets Errors",			"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.3.0 -C public -P 2c")
DeviceServiceGen("Total Packets Captured",			"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.4.0 -C public -P 2c")

DeviceServiceGen("Bytes Cached",					"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.5.0 -C public -P 2c")
DeviceServiceGen("Total Bytes to RAID",				"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.6.0 -C public -P 2c")
DeviceServiceGen("Total Bytes Captured",			"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.7.0 -C public -P 2c")
DeviceServiceGen("Total Bytes Overflow",			"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.8.0 -C public -P 2c")
DeviceServiceGen("Total SMART Errors",				"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.9.0 -C public -P 2c")
DeviceServiceGen("RAID Status",						"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.10.0 -C public -P 2c")

DeviceServiceGen("Capture Status",					"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.14.0 -C public -P 2c")
DeviceServiceGen("Capture Name",					"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.15.0 -C public -P 2c")
DeviceServiceGen("Capture Bps",						"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.16.0 -C public -P 2c")
DeviceServiceGen("Capture Pps",						"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.17.0 -C public -P 2c")
DeviceServiceGen("Capture TCP Bps",					"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.18.0 -C public -P 2c")
DeviceServiceGen("Capture UDP Bps",					"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.19.0 -C public -P 2c")

-- macro for drive stats. note it gets sorted alphabetically by name
-- want it list order to be all drives for a single attribute (e.g. temperature)
-- makes viewing the graphs easier
local DiskService = function(DriveNo, Index)

	DeviceServiceGen("Drive SerialNo "            ..DriveNo,	"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.3.1.1.1."..Index.." -C public -P 2c")
	DeviceServiceGen("Drive Temperature "         ..DriveNo,	"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.3.1.1.8."..Index.." -C public -P 2c")
	DeviceServiceGen("Drive SMART Errors "        ..DriveNo,	"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.3.1.1.4."..Index.." -C public -P 2c")
	DeviceServiceGen("Drive SMART Read Errors "   ..DriveNo,	"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.3.1.1.5."..Index.." -C public -P 2c")
	DeviceServiceGen("Drive SMART DMA Errors "    ..DriveNo,	"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.3.1.1.6."..Index.." -C public -P 2c")
	DeviceServiceGen("Drive SMART Realloc Errors "..DriveNo,	"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.3.1.1.7."..Index.." -C public -P 2c")
end

if (DeviceTarget == "fmadio20") then

	-- temp monitoring
	DeviceServiceGen("System Temperature CPU0",				"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.30.0 -C public -P 2c")
	DeviceServiceGen("System Temperature PCH",				"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.32.0 -C public -P 2c")
	DeviceServiceGen("System Temperature Ambient",			"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.33.0 -C public -P 2c")
	DeviceServiceGen("System Temperature HBA",				"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.37.0 -C public -P 2c")
	DeviceServiceGen("System Temperature NIC",				"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.41.0 -C public -P 2c")

	-- fan monitoring
	DeviceServiceGen("System Fan RPM CPU0",					"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.20.0 -C public -P 2c")
	DeviceServiceGen("System Fan RPM SYS0",					"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.22.0 -C public -P 2c")
	DeviceServiceGen("System Fan RPM SYS1",					"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.23.0 -C public -P 2c")
	DeviceServiceGen("System Fan RPM SYS2",					"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.1.1.24.0 -C public -P 2c")

	-- capture port info
	for p=0,1 do
		DeviceServiceGen("Capture Link Port "..p,			"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.2.1.1.20."..p.." -C public -P 2c")
		DeviceServiceGen("Capture SFP Mode Port "..p,		"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.2.1.1.21."..p.." -C public -P 2c")
		DeviceServiceGen("Capture SFP Vendor Port "..p,		"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.2.1.1.23."..p.." -C public -P 2c")
		DeviceServiceGen("Capture SFP PartNo Port "..p,		"xiwizard_snmp_service",					"check_xi_service_snmp! -o .1.3.6.1.4.1.46891.2.1.1.24."..p.." -C public -P 2c")
	end

	DiskService("OS",	0)
	DiskService("HDD0", 1)
	DiskService("HDD1", 2)
	DiskService("HDD2", 3)
	DiskService("HDD3", 4)

	DiskService("SSD0", 5)
	DiskService("SSD1", 6)
	DiskService("SSD2", 7)
	DiskService("SSD3", 8)
	DiskService("SSD4", 9)
	DiskService("SSD5", 10)
	DiskService("SSD6", 11)
	DiskService("SSD7", 12)
end

ctrace(Config, "# configuration end\n")
Config:close()
