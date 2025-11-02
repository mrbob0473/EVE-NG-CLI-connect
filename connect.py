#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import pickle
import getopt
import os
import sys
import uritools
import urllib
import getpass

apiGateway='127.0.0.1'
apiUserName=None
apiPassword=None
cacheFileDir='~'

def eprint(msg):
	sys.stderr.write(msg)
	sys.stderr.write('\n')

def Print_Usage():
	print("Usage: connect.py [-a] [-b <lab>] [-c] [-g <gateway>] [-h] [-i] [-l] [-n] [-u <username>] [-t <node>]")
	print("This command line tool can help EVE-NG users list nodes for a lab; and connect to those running lab devices.\n")
	print("Parameters:")
	print("Note: Mandatory arguments to long options are mandatory for short options too.")
	print("-a, --all\t\t\tConnect all running nodes in the lab specified by -b or --lab parameter.  When using this paramter, the command is required to run inside a tmux session.")
	print("-b, --lab=<lab>\t\t\tSpecify the name of the lab the command is targeting for.")
	print("-c, --cache\t\t\tTo get the information about the lab nodes (devices) from the cache file instead of calling API.  (Calling API will log the user out of the WebGUI session.)")
	print("-g, --gateway=<gateway>\t\tTo specify the IP address of the API gateway.  The default value is 127.0.0.1.")
	print("-h, --help\t\t\tShowing this usage information.")
	print("-i, --inactive\t\t\tWhen listing nodes, list those inactive nodes as well.")
	print("-l, --list\t\t\tTo list nodes (devices) belonging to the lab whose name is specified by -b or --lab parameter.")
	print("-n, --no-tmux\t\t\tDo not open a new tmux window if running the command inside a tmux session.")
	print("-t, --telnet=<node>\t\tTo telnet to the console port of the node (device).")
	print("-u, --user=<username>\t\tUsername for the EVE-NG API connection.")

def API_Login(apiSession, apiURL, apiUserName, apiPassword):
	url=apiURL + '/auth/login'
	data = {"username":apiUserName,"password":apiPassword, "html5":"-1"}
	response = apiSession.post(url, json=data)
	return response.status_code

def API_Logout(apiSession, apiURL):
	url=apiURL + '/auth/logout'
	response = apiSession.get(url)
	return response.status_code

def API_GetLabDevicePorts(apiSession, apiURL, labName):
	labName = urllib.parse.quote(labName)
	url=apiURL + '/labs/{}/nodes'.format(labName)
	response = apiSession.get(url)
	return response.json()

def Update_Cache(apiURL, apiUserName, apiPassword, labName, cacheFile):
	error = False
	apiSession = requests.Session()
	apiSession.verify = False
	apiCallStatusCode=API_Login(apiSession, apiURL, apiUserName, apiPassword)
	if apiCallStatusCode != 200:
		eprint("Error: Failed to login to the API")
		error = True
		return False

	nodes=API_GetLabDevicePorts(apiSession, apiURL, labName)
	if nodes['status'] == 'success':
		cache={}
		for key in nodes['data']:
			cache[nodes['data'][key]['name']] = {'status': nodes['data'][key]['status'], 'url':nodes['data'][key]['url']}
		with open(cacheFile, 'w+b') as f:
			pickle.dump(cache, f)

	else:
		eprint("Error: Failed to query nodes via the API.\n{}".format(nodes['message']))
		error = True

	apiCallStatusCode=API_Logout(apiSession, apiURL)
	if apiCallStatusCode != 200:
		eprint("Error: Failed to logout from the API")
		error = True

	return not error

def Load_From_Cache(cacheFile):
	if not os.path.isfile(cacheFile):
		eprint("Error: {} is not a file!".format(cacheFile))
		return {}
	else:
		with open(cacheFile, 'rb') as f:
			return pickle.load(f)

def List_Nodes(nodes, listInactiveNodes):
	keys = sorted(nodes)
	for key in keys:
		if not listInactiveNodes and nodes[key]["status"] != 2:
			continue
		print("Name: {}\tStatus: {}\tURL: {}".format(key, nodes[key]["status"], nodes[key]["url"]))

def Is_TMUX():
	if os.getenv("TMUX") is not None:
		return True
	else:
		return False

def Telnet_Host(nodeName, hostname, port, noTmux=False):
	if not noTmux and Is_TMUX():
		os.system("tmux new-window -ad -n {} -t {{end}} telnet {} {}".format(nodeName, hostname, port))
	else:
		os.system("telnet {} {}".format(hostname, port))

def Connect_All_Nodes(nodes, noTmux=False):
	keys = sorted(nodes)
	for key in keys:
		if nodes[key]["status"] == 2:
			Connect_Node(nodes, key)

def Connect_Node(nodes, name, noTmux=False):
	for key in nodes:
		if nodes[key]["status"] != '2' and key == name:
			url = uritools.urisplit(nodes[key]["url"])
			Telnet_Host(name, url.host, url.port, noTmux)

if __name__ == '__main__':
	skipCache = False
	listNodes = False
	listInactiveNodes = False
	labName = None
	connectNode = False
	connectAllNodes = False
	connectHostname = ''
	noTmux = False


	if (len(sys.argv)<2):
		Print_Usage()
		sys.exit(2)

	try:
		opts,args = getopt.getopt(sys.argv[1:], '-a-b:-c-g:-h-l-n-i-u:-t:', ['cache','lab=','list','help','inactive','all','telnet=','no-tmux','user=','gateway='])
	except getopt.GetoptError:
		Print_Usage()
		sys.exit(2)

	for optName,optValue in opts:
		if optName in ('-c', '--cache'):
			skipCache = True
		if optName in ('-l', '--list'):
			listNodes = True
		if optName in ('-i', '--inactive'):
			listInactiveNodes = True
		if optName in ('-a', '--all'):
			connectNode = True
			connectAllNodes = True
		if optName in ('-t', '--telnet'):
			connectNode = True
			connectHostname = optValue
		if optName in ('-n', '--no-tmux'):
			noTmux = True
		if optName in ('-b', '--lab'):
			labName = optValue
		if optName in ('-u', '--user'):
			apiUserName = optValue
		if optName in ('-g', '--gateway'):
			apiGateway = optValue
		if optName in ('-h', '--help'):
			Print_Usage()
			exit()

	if labName is None:
		eprint("Error: name of the lab is required!\n")
		sys.exit(2)
	else:
		if not labName.endswith('.unl'):
			labName += ".unl"

	cacheFile = cacheFileDir + '/.connect.py.' + labName + '.cache'
	cacheFile = os.path.expanduser(cacheFile)

	if not skipCache:
		if apiUserName is None:
			eprint("Error: Please provide the username and password for the EVE-NG API connection!")
			sys.exit(2)
		else:
			apiPassword = getpass.getpass()
		apiURL='http://{}/api'.format(apiGateway)
		if not Update_Cache(apiURL, apiUserName, apiPassword, labName, cacheFile):
			eprint("Error: Failed to update the cache!")
			sys.exit(3)

	nodes = Load_From_Cache(cacheFile)

	if listNodes:
		List_Nodes(nodes, listInactiveNodes)
		exit()

	if connectNode:
		if connectAllNodes:
			if Is_TMUX():
				Connect_All_Nodes(nodes, noTmux)
			else:
				print("Error: To connect to all nodes, please run the command inside a tmux session!")
				sys.exit(4)
		else:
			Connect_Node(nodes, connectHostname, noTmux)
