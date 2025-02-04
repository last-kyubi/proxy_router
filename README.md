# proxy_router

<b>#Requirements</b></br>
requests and psutils (pip3)</br>
proxychains</br>
Neo-reGeorg (installed in project's root directory)</br>
</br></br>
<b>#What is the purpose of this project?</b></br>
proxy_router is a project that wants to centralize all the Neo_Regeorg (https://github.com/L-codes/Neo-reGeorg) backdoors into a single json file.
</br></br>
<b>#Key Features</b>
</br>
~List all proxies from JSON file;</br>
~Select a proxy by it's ID;</br>
~Specify a port to spawn tunnel;</br>
~Edit/Clean the proxychain routing table according to needings;</br>
~Kill running tunnels;</br>
</br></br>
<h1><b>#Usage</b></h1>
List Proxies
</br>
python3 router.py --list</br>
</br>
Select a Proxy and Start a Tunnel</br>
python3 router.py --proxy-id <ID> --port <PORT>
</br>
</br>
Add Proxy to Proxychains</br>
python3 router.py --proxy-id <ID> --port <PORT> --proxychain
</br>
</br>
Kill All Running Neo-reGeorg Processes</br>
python3 router.py --killall
</br>
</br>
Clean Proxychains Configuration</br>
python3 router.py --clean

