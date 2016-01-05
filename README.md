# fmadio_scripts

**stream_rsync.py**

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
--splitmode <splitmode>     : select split mode (default 1min)
--splitlist                 : show split options
--list                      : show all captures on the remote machine

```

## Examples


1) Continously download the currently active capture in 1 second PCAP splits

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
2) Show the Split options for the currently active capture 

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
3) Show List of captures on the FMADIO device at 192.168.1.1 with Username "fmadio" and Password "secret"

```
$ ./capture_rsync.py  --list --host 192.168.1.1 --user fmadio --pass secret 
Capture List
  py4_20160105_1618
  py3_20160105_1611
  py2_20160105_1603

```
