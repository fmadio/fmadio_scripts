# fmadio_scripts

![Alt text](http://fmad.io/analytics/logo_scripts.png "fmadio scripts logo")

### stream_rsync.py

Python script for rsync like capture downloading. Can download from the FMADIO packet capture device in multiple split modes. 

Command line Options

```
$ ./capture_rsync.py  --help
capture_rsync <capture name> : RSync`s a capture to the local machine

Options:
 --follow                    : run in follow/poll mode. (default false)
 --https                     : use HTTPS (defaults HTTP)
 --host <hostname>           : specify host name
 --user <username>           : HTTP(s) username
 --pass <password>           : HTTP(s) password
 --output <dir>              : output directory (default ./)
 --single                    : downloads capture as a single PCAP)
 --splitmode <splitmode>     : select split mode (default 1GB)
 --splitlist                 : show split options
 --start <HH:MM:SS>          : start time
 --stop  <HH:MM:SS>          : stop time
 --list                      : show all captures on the remote machine
 --compress                  : compress at the source (~1Gbps throughput)
 --filter <filterop>         : filter option
                             : FilterIPHost=1.2.3.4
                             : FilterIPHost=1.2.3.4/32
                             : FilterIPSrc=1.2.3.0/24
                             : FilterIPDst=1.2.3.0/24
                             : FilterTCPPort=1234
                             : FilterTCPPort=1000-2000
                             : FilterUDPPort=1234
                             : FilterUDPPort=1000-2000
                             : FilterTCP=true
                             : FilterUDP=true
                             : FilterDNS=true
                             : FilterHTTP=true
                             : FilterHTTPS=true
                             : FilterICMP=true
                             : FilterIGMP=true
 --vlan-ignore               : ignore vlan header
 --vlan-strip                : strips vlan header (will loose FCS)
 --date-jp                   : specify a Japanese date YYYYMMDD (also requires start/stop time)
 --date-us                   : specify a US date       MMDDYYYY (also requires start/stop time)
 --date                      : specify a normal date   DDYMMYYY (also requires start/stop time)
 -v                          : verbose output

```

### Config File

It can be painful and a security risk including the FMADIO hostname + username + password on the command line every time. The scripts load a configuration file located in the home directory named .fmadio.conf 

An example file looks like this:

```
$ cat ~/.fmadio.conf
[General]
username=fmadio
password=secret
hostname=192.168.1.1

```

### Examples

#### 1) Continously download the currently active capture in 1 second PCAP splits

```
$ ./capture_rsync.py  --follow  --host 192.168.11.95 --split split_1sec
Follow Mode
[./py4_20160105_1618_split_1sec/py4_20160105_1618_20160105_16:12:20.211.165.440 ] Downloading...   0.000 GB   0.877 sec    0.000000 Gbps
[./py4_20160105_1618_split_1sec/py4_20160105_1618_20160105_16:18:50.749.243.904 ] Downloading...   0.343 GB  29.817 sec    0.091988 Gbps
[./py4_20160105_1618_split_1sec/py4_20160105_1618_20160105_16:18:51.749.243.904 ] Downloading...   0.415 GB  38.029 sec    0.087294 Gbps
[./py4_20160105_1618_split_1sec/py4_20160105_1618_20160105_16:18:52.749.243.904 ] Downloading...   0.488 GB  42.962 sec    0.090792 Gbps
[./py4_20160105_1618_split_1sec/py4_20160105_1618_20160105_16:18:53.749.243.904 ] Downloading...   0.436 GB  43.522 sec    0.080117 Gbps
[./py4_20160105_1618_split_1sec/py4_20160105_1618_20160105_16:18:54.749.243.904 ] Downloading...   0.110 GB   0.949 sec    0.931275 Gbps
[./py4_20160105_1618_split_1sec/py4_20160105_1618_20160105_16:18:55.749.243.904 ] Downloading...   0.100 GB   0.860 sec    0.928788 Gbps
[./py4_20160105_1618_split_1sec/py4_20160105_1618_20160105_16:18:56.749.243.904 ] Downloading...   0.109 GB   0.941 sec    0.930891 Gbps
[./py4_20160105_1618_split_1sec/py4_20160105_1618_20160105_16:18:57.749.243.904 ] Downloading...   0.099 GB   2.317 sec    0.341684 Gbps
[./py4_20160105_1618_split_1sec/py4_20160105_1618_20160105_16:18:58.749.243.904 ] Downloading...   0.078 GB   0.760 sec    0.820824 Gbps
[./py4_20160105_1618_split_1sec/py4_20160105_1618_20160105_16:18:59.749.243.904 ] Downloading...   0.064 GB   0.784 sec    0.648858 Gbps
[./py4_20160105_1618_split_1sec/py4_20160105_1618_20160105_16:19:00.749.243.904 ] Downloading...   0.099 GB   3.152 sec    0.250963 Gbps
[./py4_20160105_1618_split_1sec/py4_20160105_1618_20160105_16:19:01.749.243.904 ] Downloading...   0.108 GB   1.268 sec    0.678948 Gbps
[./py4_20160105_1618_split_1sec/py4_20160105_1618_20160105_16:19:02.749.243.904 ] Downloading...   0.113 GB   1.512 sec    0.596313 Gbps

```
#### 2) Show the Split options for the currently active capture 

```
aaron@fpga:~/lln/github/fmadio_scripts$ ./capture_rsync.py  --splitlist
Split Modes:
  split_1sec
  split_10sec
  split_1min
  split_10min
  split_15min
  split_1hour
  split_1MB
  split_10MB
  split_100MB
  split_1GB
  split_10GB
  split_100GB
  split_1TB

```
#### 3) List all captures on the FMADIO device

```
$ ./capture_rsync.py  --list --host 192.168.1.1 --user fmadio --pass secret 
Capture List
  py4_20160105_1618
  py3_20160105_1611
  py2_20160105_1603

```

#### 4) Download all packets between 13:35:45 and 13:35:46 with compression 


```
$ ./capture_rsync.py  --compress --single --start 13:35:45 --stop 13:35:46 --output /tmp/test remote_basic_1453696518952593920_20160125_1335
RSync Capture Named [remote_basic_1453696518952593920_20160125_1335]
Single PCAP Compressed
TZ Offset 32400 Sec
[remote_basic_1453696518952593920_20160125_1335] Downloading...
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  831M    0  831M    0     0  24.3M      0 --:--:--  0:00:34 --:--:-- 19.1M

$ ls -al /tmp
total 1601972
drwxrwxrwt  5 root  root      20480  1月 25 14:57 .
drwxr-xr-x 22 root  root       4096 12月 10 00:21 ..
-rw-rw-r--  1 aaron aaron 871830615  1月 25 14:57 test_remote_basic_1453696518952593920_20160125_1335.pcap.gz
$
```

#### 5) Split and Apply Filtering


Note: When filters are applied, downloaded files are always overwritten. 

```

$ ./capture_rsync.py  --host 192.168.12.10 --output fmadio20 --filter FilterIPHost=192.168.1.0/24 --follow
Follow Mode
[fmadio20_landata_20160105_2145_split_1GB/landata_20160105_2145__20160105_21:46:14.660.095.232 ] Downloading...   0.264 GB   3.971 sec    0.532612 Gbps
[fmadio20_landata_20160105_2145_split_1GB/landata_20160105_2145__20160105_21:46:54.697.121.792 ] Downloading...   0.380 GB   7.556 sec    0.402748 Gbps
[fmadio20_landata_20160105_2145_split_1GB/landata_20160105_2145__20160105_21:47:43.308.749.568 ] Downloading...   0.072 GB   1.186 sec    0.484051 Gbps
Sleeping...
[fmadio20_landata_20160105_2145_split_1GB/landata_20160105_2145__20160105_21:48:05.748.449.280 ] Downloading...   0.000 GB   1.226 sec    0.000267 Gbps
[fmadio20_landata_20160105_2145_split_1GB/landata_20160105_2145__20160105_21:48:24.473.020.672 ] Downloading...   0.000 GB   1.933 sec    0.000176 Gbps
[fmadio20_landata_20160105_2145_split_1GB/landata_20160105_2145__20160105_21:48:50.867.348.736 ] Downloading...   0.000 GB   1.851 sec    0.000077 Gbps
[fmadio20_landata_20160105_2145_split_1GB/landata_20160105_2145__20160105_21:49:10.676.263.424 ] Downloading...   0.010 GB   2.225 sec    0.037457 Gbps
Sleeping...

```

Filter options are

```
FilterIPSrc=1.2.3.4/32
FilterIPDst=1.2.3.4/32
FilterIPHost=1.2.3.4/32
FilterTCP=true
FilterUDP=true
FilterTCPPort=1234
FilterUDPPort=1234

FilterHTTP=true
FilterHTTPS=true
FilterDNS=true
FilterICMP=true
FilterIGMP=true
```

#### 6) Sync capture with 1GB split with GZip compression 

Note: Compression is perfomred on the capture device. This is best for rsync captures across a low bandwidth WAN connection

```
$ ./capture_rsync.py  --compress --output /tmp/test remote_basic_1453696518952593920_20160125_1335
RSync Capture Named [remote_basic_1453696518952593920_20160125_1335]
[/tmp/remote_basic_1453696518952593920_20160125_1335_split_1GB/remote_basic_1453696518952593920_20160125_1335__20160125_13:35:41.907.941.120.pcap.gz] Downloading...   0.349 GB  13.464 sec    0.207326 Gbps
[/tmp/remote_basic_1453696518952593920_20160125_1335_split_1GB/remote_basic_1453696518952593920_20160125_1335__20160125_13:35:42.308.264.960.pcap.gz] Downloading...   0.349 GB  14.454 sec    0.193131 Gbps
[/tmp/remote_basic_1453696518952593920_20160125_1335_split_1GB/remote_basic_1453696518952593920_20160125_1335__20160125_13:35:42.708.495.872.pcap.gz] Downloading...   0.349 GB  13.541 sec    0.206155 Gbps
[/tmp/remote_basic_1453696518952593920_20160125_1335_split_1GB/remote_basic_1453696518952593920_20160125_1335__20160125_13:35:43.108.719.616.pcap.gz] Downloading...   0.349 GB  12.461 sec    0.224032 Gbps
[/tmp/remote_basic_1453696518952593920_20160125_1335_split_1GB/remote_basic_1453696518952593920_20160125_1335__20160125_13:35:43.508.950.528.pcap.gz] Downloading...   0.349 GB  13.465 sec    0.207315 Gbps
[/tmp/remote_basic_1453696518952593920_20160125_1335_split_1GB/remote_basic_1453696518952593920_20160125_1335__20160125_13:35:43.909.181.440.pcap.gz] Downloading...   0.349 GB  14.008 sec    0.199286 Gbps
[/tmp/remote_basic_1453696518952593920_20160125_1335_split_1GB/remote_basic_1453696518952593920_20160125_1335__20160125_13:35:44.309.412.608.pcap.gz] Downloading...   0.349 GB  13.401 sec    0.208301 Gbps
```

#### 7) search captures for a specific date/start time/stop time into a single compressed pcap 

Note: Compression is perfomred on the capture device. When used with 24/7 capture provides a convient way to extract data from the system 

```
$ ./capture_rsync.py  --date-jp 20160213 --start 11:10:00 --stop 11:11:00 --compress --single --output ./20160213_1110to1111.pcap.gz
Searching 20160213 [11:10:00]-[11:11:00]

found capture: capture247_20160213_1109
Single PCAP Compressed
TZ Offset 32400 Sec
[capture247_20160213_1109] Downloading...
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                   Dload  Upload   Total   Spent    Left  Speed
100 11.7G    0 11.7G    0     0  31.2M      0 --:--:--  0:06:23 --:--:-- 31.6M
 12.585 GB  383.604 sec    0.262451 Gbps
$
```

