# proxy_router

#Requirements
requests and psutils (pip3)
proxychains
Neo-reGeorg (installed in project's root directory)

#What is the purpose of this project?
proxy_router is a project that wants to centralize all the Neo_Regeorg (https://github.com/L-codes/Neo-reGeorg) backdoors into a single json file.

#Key Features
~List all proxies from JSON file;
~Select a proxy by it's ID;
~Specify a port to spawn tunnel;
~Edit/Clean the proxychain routing table according to needings;
~Kill running tunnels;

#Usage
List Proxies
python3 router.py --list

Select a Proxy and Start a Tunnel
python3 router.py --proxy-id <ID> --port <PORT>

Add Proxy to Proxychains
python3 router.py --proxy-id <ID> --port <PORT> --proxychain

Kill All Running Neo-reGeorg Processes
python3 router.py --killall

Clean Proxychains Configuration
python3 router.py --clean

