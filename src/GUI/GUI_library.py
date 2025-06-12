"""
GUI_library.py

This module provides functions to perform scans of IP addresses, subnets, and lists of subnets/IPs using Docker.
Scans are executed in Docker containers, and results are dynamically handled through log callbacks.

Main Features:
- Scan of a single IP address.
- Scan of a single subnet.
- Scan of multiple subnets/IPs from a file.
- Real-time log management via callback.
- Support for configurable Docker volumes.

Dependencies:
- Python standard library: os, subprocess, threading, uuid, ipaddress.
- Docker must be properly installed and configured.

Handled Exceptions:
- FileNotFoundError: Docker not found or input file missing.
- ValueError: Invalid IP or subnet format.
- Exception: Generic errors during execution.

Functions:
- scan_single_ip(ip: str, volumes: list[int], log_callback=None) -> subprocess.Popen:
    Scans a single IP address for open ports and services.

- scan_single_subnet(subnet: str, volumes: list[int], cont: int, log_callback=None) -> subprocess.Popen:
    Scans a single subnet for open ports and services.

- scan_multiple_subnets(file_name: str, volumes: list[int], cont: int, log_callback=None) -> subprocess.Popen:
    Scans a list of subnets/IPs from a file.

Usage:
The functions in this module can be integrated into a GUI or used directly to perform scans and manage results.

"""


import os
import subprocess
import threading
import uuid
import ipaddress

def scan_single_ip(ip: str, volumes: list[int], log_callback=None) -> subprocess.Popen:
    """
    Scans a single IP address for open ports and services, updating the log dynamically.

    Args:
        ip (str): The IP address to scan.
        volumes (list[int]): A list of selected volume options (1 for selected, 0 for not selected).
        log_callback (function, optional): A callback function to update the logs dynamically.

    Returns:
        subprocess.Popen: The process object to allow further management (e.g., stopping the process).
    """

    try:
        ip = ipaddress.ip_address(ip)  # Validate the IP address
        container_name = f"orchestrator_{uuid.uuid4().hex[:8]}"
        command = f"sudo docker run --name {container_name} --network=host --rm -v $(pwd)/Parsed_report:/usr/Orchestrator/Parsed_report"
        
        # Add selected volumes
        if volumes[0] == 1:
            command += " -v $(pwd)/Tsunami_outputs:/usr/Orchestrator/logs"
        
        command += f" orch:latest -ip {ip} -s"

        process = subprocess.Popen(
            command,
            shell=True, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            preexec_fn=os.setsid 
        )

        # Read the output line by line
        def stream_output():
            try:
                # Read both stdout and stderr in real-time
                for line in process.stdout:
                    if log_callback:
                        log_callback(line)
                for err in process.stderr:
                    if log_callback:
                        log_callback(err)
                process.wait()
            except Exception as e:
                if log_callback:
                    log_callback(f"Error: {str(e)}\n")

        # Start streaming the output in a separate thread
        threading.Thread(target=stream_output, daemon=True).start()

        # Save the container name as a custom attribute
        process.container_name = container_name

        return process  # Return the process object

    except FileNotFoundError:
        if log_callback:
            log_callback("Error: Docker is not installed or not found in PATH.\n")
    except ValueError:
        if log_callback:
            log_callback("Error: Invalid IP address format.\n")
    except Exception as e:
        if log_callback:
            log_callback(f"Unexpected error: {str(e)}\n")


def scan_single_subnet(subnet: str, volumes: list[int], cont: int, log_callback=None) -> subprocess.Popen:
    """
    Scans a single subnet for open ports and services, updating the log dynamically.

    Args:
        subnet (str): The subnet to scan.
        volumes (list[int]): A list of selected volume options (1 for selected, 0 for not selected).
        cont (int): The maximum number of containers to run simultaneously.
        log_callback (function, optional): A callback function to update the logs dynamically.

    Returns:
        subprocess.Popen: The process object to allow further management (e.g., stopping the process).
    """
    try:
        subnet = ipaddress.ip_network(subnet, strict=False)  # Validate the subnet
        container_name = f"orchestrator_{uuid.uuid4().hex[:8]}"
        command = f"sudo docker run --name {container_name} --network=host --rm -v $(pwd)/Parsed_report:/usr/Orchestrator/Parsed_report"
        
        # Add selected volumes
        if volumes[0] == 1:
            command += " -v $(pwd)/Tsunami_outputs:/usr/Orchestrator/logs"
            
        command += f" orch:latest -sub {subnet} -c {cont} -s"

        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            preexec_fn=os.setsid 
        )

        def stream_output():
            try:
                for line in process.stdout:
                    if log_callback:
                        log_callback(line)
                for err in process.stderr:
                    if log_callback:
                        log_callback(err)
                process.wait()
            except Exception as e:
                if log_callback:
                    log_callback(f"Error: {str(e)}\n")

        threading.Thread(target=stream_output, daemon=True).start()
        process.container_name = container_name 
        return process

    except FileNotFoundError:
        if log_callback:
            log_callback("Error: Docker is not installed or not found in PATH.\n")
    except ValueError:
        if log_callback:
            log_callback("Error: Invalid subnet format.\n")
    except Exception as e:
        if log_callback:
            log_callback(f"Unexpected error: {str(e)}\n")


def scan_multiple_subnets(file_name: str, volumes: list[int], cont: int, log_callback=None) -> subprocess.Popen:
    """
    Scans a list of subnets/IPs from a file and manages the results.

    Args:
        file_name (str): The name of the file containing the subnets/IPs.
        volumes (list[int]): A list of selected volume options (1 for selected, 0 for not selected).
        cont (int): The maximum number of containers to run simultaneously.
        log_callback (function, optional): A callback function to update the logs dynamically.

    Returns:
        subprocess.Popen: The process object to allow further management (e.g., stopping the process).
    """
    try:
        container_name = f"orchestrator_{uuid.uuid4().hex[:8]}"
        command = f"sudo docker run --name {container_name} --network=host --rm -v $(pwd)/Parsed_report:/usr/Orchestrator/Parsed_report -v $(pwd)/input_files:/usr/Orchestrator/input_files"
        
        # Add selected volumes
        if volumes[0] == 1:
            command += " -v $(pwd)/Tsunami_outputs:/usr/Orchestrator/logs"
            
        command += f" orch:latest -snl {file_name} -c {cont} -s"

        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            preexec_fn=os.setsid 
        )

        def stream_output():
            try:
                for line in process.stdout:
                    if log_callback:
                        log_callback(line)
                for err in process.stderr:
                    if log_callback:
                        log_callback(err)
                process.wait()
            except Exception as e:
                if log_callback:
                    log_callback(f"Error: {str(e)}\n")

        threading.Thread(target=stream_output, daemon=True).start()
        process.container_name = container_name 
        return process

    except FileNotFoundError:
        if log_callback:
            log_callback("Error: Docker is not installed or not found in PATH.\n")
    except Exception as e:
        if log_callback:
            log_callback(f"Unexpected error: {str(e)}\n")
