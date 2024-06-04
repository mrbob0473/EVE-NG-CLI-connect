# Summary
This is A command-line tool to connect to EVE-NG lab devices.  By running this tool, user will be able to get a list of the nodes from a given EVE-NG lab to to connect to the console port of the devcies via telnet.

When running the tool to connect to a console port inside a tmux session, the telnet session will be started in a new tmux window with the name of the window set to the name of the target device being connected to.

# Usage
```
connect.py [-a] [-b <lab>] [-c] [-g <gateway>] [-h] [-i] [-l] [-n] [-u <username>] [-t <node>]

Parameters:
Note: Mandatory arguments to long options are mandatory for short options too.
-a, --all                       Connect all running nodes in the lab specified by -b or --lab parameter. When using this paramter, the command is required to run inside a tmux session
-b, --lab=<lab>                 Specify the name of the lab the command is targeting for.
-c, --cache                     To get the information about the lab nodes (devices) from the cache file instead of calling API.  (Calling API will log the user out of the WebGUI session.)
-g, --gateway=<gateway>         To specify the IP address of the API gateway.  The default value is 127.0.0.1.
-h, --help                      Showing this usage information.
-i, --inactive                  When listing nodes, list those inactive nodes as well.
-l, --list                      To list nodes (devices) belonging to the lab whose name is specified by -b or --lab parameter.
-n, --no-tmux                   Do not open a new tmux window if running the command inside a tmux session.
-t, --telnet=<node>             To telnet to the console port of the node (device).
-u, --user=<username>           Username for the EVE-NG API connection.
```

## Sample Use Cases:
### To get a list of the devices for the lab called "Test Lab", including those stopped devices, via API call
Note: node list from the API call will be stored inside a local cache file.  Calling API will log the user out of the WebGUI session.
As running the command-line will update the cache, it can also be used as the method to update the local cache.
```
$ ./connect.py -li -b "Test Lab"  -g 192.168.2.101 -u admin
Password: 
Name: DA01      Status: 0       URL: telnet://192.168.2.101:32771
Name: DA02      Status: 0       URL: telnet://192.168.2.101:32772
Name: DA03      Status: 0       URL: telnet://192.168.2.101:32773
Name: DA04      Status: 0       URL: telnet://192.168.2.101:32777
Name: DC01      Status: 0       URL: telnet://192.168.2.101:32769
Name: DC02      Status: 0       URL: telnet://192.168.2.101:32770
Name: VPC1      Status: 2       URL: telnet://192.168.2.101:32774
Name: VPC2      Status: 2       URL: telnet://192.168.2.101:32775
Name: VPC3      Status: 2       URL: telnet://192.168.2.101:32776
```
### To get a list of the running devices from the local cache for the lab called "Test Lab"
```
$ ./connect.py -cl -b "Test Lab"
Name: VPC1      Status: 2       URL: telnet://192.168.2.101:32774
Name: VPC2      Status: 2       URL: telnet://192.168.2.101:32775
Name: VPC3      Status: 2       URL: telnet://192.168.2.101:32776
```

### To connect to all running devices in the "Test Lab" via telnet based on the cached device list
```
$ ./connect.py -ca -b "Test Lab"
```

### To connect to the device called "VPC1" via telnet based on the cached device list
```
$ ./connect.py -c -n -b "Test Lab" -t VPC1
Trying 192.168.2.101...
Connected to 192.168.2.101.
Escape character is '^]'.

VPCS>
```
