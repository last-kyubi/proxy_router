import json
import argparse
import socket
import subprocess
import sys
import requests
import os
import psutil

#~.~.~.~.~.~.~.#
# Global Paths #
#~.~.~.~.~.~.~.#
regeorg_path = "Neo-reGeorg"
proxy_list = "Proxies/proxy.json"
config_path = "/etc/proxychains4.conf"

#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~#
# load_proxies will list the proxies, loaded as a JSON file #
#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~#
def load_proxies():
    try:
        with open(proxy_list, "r", encoding="utf-8") as file:
            data = json.load(file)

        for item in data:
            print(f"ID: {item['id']}, Type: {item['type']}, Country: {item['country']}")

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to load proxy list: {e}")
        sys.exit(1)  # Exit with error status

#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~#
# select_proxy allows to select the right proxy by ID #
#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~#
def select_proxy(selection_id):
    try:
        with open(proxy_list, "r", encoding="utf-8") as file:
            data = json.load(file)
            selected_proxy = next((item for item in data if str(item.get("id")) == str(selection_id)), None)
            if selected_proxy:
                print(f"Selected Proxy: ID={selected_proxy['id']}, Type={selected_proxy['type']}, Country={selected_proxy['country']}")
                return selected_proxy
            else:
                print("Error: Proxy ID is not in file.")
                return None
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file: {e}")
        return None

#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~#
# select_port allows to check if a port is available  #
#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~#
def select_port(selected_port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('127.0.0.1', selected_port))  # Bind immediately to reserve the port
            return selected_port
    except OSError:
        print(f"Error: Port {selected_port} is already in use.")
        return None

#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~#
# neoregeorg_run executes Neo-reGeorg with parameters #
#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~#
def neoregeorg_run(selected_proxy, selected_port):
    if not selected_proxy:  #check for proxy availability
        print("Error: No valid proxy selected.")
        return
    if not selected_port:   #check for port available
        print("Error: No valid port available.")
        return

    password = selected_proxy.get("psw") #get psw from selected proxy
    url = selected_proxy.get("url") #get url from selected proxy

    if not password or not url:
        print("Error in proxy config")
        return

    # build the command
    command = [
        "python3",
        f"{regeorg_path}/neoreg.py",
        "-k", password,
        "-u", url,
        "-p", str(selected_port),
        "--skip"
    ]

    print(f"Executing: {' '.join(command)}")

    try:
        with open(os.devnull, 'w') as devnull:
            subprocess.Popen(command, stdout=devnull, stderr=devnull, close_fds=True)    
    except subprocess.CalledProcessError as e:
        print(f"Error running Neo-reGeorg: {e}")

#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~#
# proxy_test tests for proxy reachability #
#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~#
def proxy_test(proxy):
    try:
        response = requests.get(proxy['url'], timeout=10) #for slower connections or to use slower proxies, increase the timeout
        return response.status_code == 200
    except requests.RequestException:
        return False
    
#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~#
# proxy_kill kills all running neoreg processes #
#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~#
def proxy_kill():
    try:
        killed = 0
        for process in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
            cmdline = process.info.get("cmdline", [])
            if cmdline and "neoreg.py" in " ".join(cmdline): 
                process.terminate()
                killed += 1
        if killed > 0:
            print(f"[INFO] Terminated {killed} Neo-reGeorg process(es).")
        else:
            print("[INFO] No running Neo-reGeorg processes found.")
    except Exception as e:
        print(f"[ERROR] Failed to terminate processes: {e}")

def proxy_chainer(selected_port):
    proxy_entry = f"socks5 127.0.0.1 {selected_port} #router_tunnel\n"
    try:
        if not os.access(config_path, os.W_OK):
            print(f"[ERROR] No write permission for {config_path}. Run as root or use sudo.")
            return
        with open(config_path, "r", encoding="utf-8") as file:
            if proxy_entry.strip() in file.read():
                print(f"[INFO] Proxy entry already exists in {config_path}.")
                return
        with open(config_path, "a", encoding="utf-8") as file:
            file.write(proxy_entry)
            print(f"[SUCCESS] Added proxy to {config_path}: {proxy_entry.strip()}")
    except Exception as e:
        print(f"[ERROR] Failed to update {config_path}: {e}")

def chain_cleaner():
    try:
        if not os.access(config_path, os.W_OK):
            print(f"[ERROR] No write permission for {config_path}. Run as root or use sudo.")
            return
        with open(config_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        new_lines = [line for line in lines if not line.strip().endswith("#router_tunnel")]
        with open(config_path, "w", encoding="utf-8") as file:
            file.writelines(new_lines)
        print("[SUCCESS] Removed all #router_tunnel entries from proxychains config.")
    except Exception as e:
        print(f"[ERROR] Failed to clean {config_path}: {e}")

if __name__ == "__main__":
    selected_proxy = None
    selected_port = None
    parser = argparse.ArgumentParser("Usage example: ./router.py -id x -p 8080")
    parser = argparse.ArgumentParser("Usage example: ./router.py -id x -p 8080 --proxychains")
    parser.add_argument("-l", "--list", action="store_true", help="Show proxies.")
    parser.add_argument("-id", "--proxy-id", help="Select the proxy ID.")
    parser.add_argument("-p", "--port", type=int, help="Specify the local port to forward the proxy.")
    parser.add_argument("-kk", "--killall", action="store_true", help="Kill all running Neo-reGeorg processes.")
    parser.add_argument("--proxychain", action="store_true", help="Add tunnel to /etc/proxychains4.conf.")
    parser.add_argument("--clean", action="store_true", help="Remove all #router_tunnel entries from proxychains config.")

    args = parser.parse_args()

    if args.killall:  
        proxy_kill()  
        exit(0)
    if args.list:  
        load_proxies()  
    if args.proxy_id:
        selected_proxy = select_proxy(args.proxy_id)
        if selected_proxy and not proxy_test(selected_proxy):
            print(f"Error: Proxy {selected_proxy['id']} is unreachable.")
            exit(1)
    if args.port:
        selected_port = select_port(args.port)
    if selected_proxy and selected_port:    
        neoregeorg_run(selected_proxy, selected_port)
        if args.proxychain:
            proxy_chainer(selected_port)
    if args.clean:
        chain_cleaner()
        exit(0)
