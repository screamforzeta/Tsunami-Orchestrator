"""
Module `orch_library.py`

This module contains a library of functions used to orchestrate network scanning operations,
IP address and subnet validation, input/output file management, and Docker container launching.

Includes functions for:
- Validating IP addresses and subnets.
- Scanning single IPs, lists of IPs, and subnets.
- Launching Docker containers to analyze scan results.
- Managing input/output files, such as removing duplicates or saving results.
- Cleaning directories and managing system resources.

Usage:
    This module is designed to be used as a support library for the `orchestrator.py` module.

Main functions:
    - `validate_ip`: Checks if an IP address is valid.
    - `validate_subnet`: Checks if a subnet is valid in CIDR format.
    - `is_ip_active`: Checks if an IP address is active using `nmap`.
    - `scan_single_ip`: Scans a single IP address and launches a Docker container if the IP is active.
    - `scan_ip_list_manager`: Manages scanning of a list of IP addresses.
    - `scan_subnet_and_save_results`: Scans a subnet and saves the results of active hosts.
    - `subnet_scan_manager`: Manages subnet scanning and launches Docker containers for active hosts.
    - `scan_multiple_subnets_manager`: Manages scanning of a list of subnets.
    - `start_docker_containers`: Launches Docker containers for a list of IP addresses.
    - `clear_directories`: Cleans specified directories by deleting all files inside.

Handled exceptions:
    The functions handle common errors such as:
    - File not found.
    - Insufficient permissions.
    - System errors.
    - Invalid input.

Dependencies:
    - `ipaddress`: For IP address and subnet validation.
    - `subprocess`: For running system commands like `nmap` and launching Docker containers.
    - `os`: For managing paths and directories.
    - `argparse`: For parsing command-line arguments.
    - `concurrent.futures`: For parallel operations.
    - `rich`: For progress bars and colored messages.

"""

import ipaddress
import subprocess
import time
import os  # Imports the os module for managing paths and directories
import argparse

from concurrent.futures import ThreadPoolExecutor, as_completed, CancelledError, TimeoutError
from typing import List
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, SpinnerColumn


def main():
    """Main function to run the program."""

def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.
    Returns:
        A Namespace object containing the parsed arguments.
    """
    
    parser = argparse.ArgumentParser(
        prog="Tsunami Security Scanner Orchestrator",
        description="Manages network scans and Docker container launching.",
        add_help=True
    )
    parser.add_argument("-ip", "--single_ip", type=str, help="Scan a single IP address.")
    parser.add_argument("-sub", "--subnet", type=str, help="Scan a subnet in CIDR format (e.g., 192.168.1.0/24).")
    parser.add_argument("-snl", "--subnet-list", type=str, help="Name of the file containing a list of subnets.")
    parser.add_argument("-c", "--containers", default=3, type=int, help="Number of Docker containers to run simultaneously for analysis. USE ONLY WITH -sub and -snl. default = 3")
    parser.add_argument("-s", "--simplify", action="store_true", help="Simplifies the progress bar, used by the GUI. USE ONLY WITH -sub and -snl.")
    
    args = parser.parse_args()
    
    # Argument validation
    if (args.simplify) and not (args.single_ip or args.subnet or args.subnet_list):
        parser.error("Arguments -c/--containers and -s/--simplify can only be used with -ip/--single_ip, -sub/--subnet or -snl/--subnet-list.")
    # Ensure -ip/--single_ip, -sub/--subnet, and -snl/--subnet-list are not used together
    if sum(bool(arg) for arg in [args.single_ip, args.subnet, args.subnet_list]) > 1:
        parser.error("Arguments -ip/--single_ip, -sub/--subnet, and -snl/--subnet-list cannot be used together.")
    if (args.containers is not None and args.containers <= 0):
        parser.error("The -c/--containers argument must be a positive integer greater than 0.")
    
    return args

def validate_ip(ip: str) -> bool:
    """
    Checks if an IP address is valid.

    Parameters:
        ip (str): The IP address to check.

    Returns:
        bool: True if the IP address is valid, False otherwise.

    Example:
        >>> validate_ip("192.168.1.1")
        True
        >>> validate_ip("invalid_ip")
        False
    """
    return ipaddress.ip_address(ip)  # Uses ipaddress to validate the IP

def validate_subnet(subnet: str) -> bool:
    """
    Checks if a subnet is valid in CIDR format (e.g., 192.168.1.0/24).

    Parameters:
        subnet (str): The subnet to check.

    Returns:
        bool: True if the subnet is valid, False otherwise.

    Example:
        >>> validate_subnet("192.168.1.0/24")
        True
        >>> validate_subnet("invalid_subnet")
        False
    """
    return ipaddress.ip_network(subnet, strict=False)  # Uses ipaddress to validate the subnet

    
def is_ip_active(ip: str) -> bool:
    """
    Checks if an IP address is active using `nmap`.

    Parameters:
        ip (str): The IP address to check.

    Returns:
        bool: True if the IP address is active, False otherwise.

    Note:
        This function uses the `nmap -sn` command to check if the IP is reachable.
        Make sure `nmap` is installed and available in the system PATH.
    """
    
    # Scan: ICMP Echo Request (ping scan)
    command_ping = ["nmap", "-sn", str(ip)]
    try:
        # Runs the scan with the nmap -sn command
        result_ping = subprocess.run(command_ping, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True) 
        output_ping = result_ping.stdout.decode()

        # Print the scan output (DEBUG ONLY)
        #print(f"Scan output for {ip}:\n{output_ping}")

        # Check if the output indicates the IP is up
        if "Nmap done: 1 IP address (1 host up)" in output_ping:
            return True  # The IP is active
        
    except FileNotFoundError:
        print("Error: The 'nmap' command was not found. Make sure it is installed and available in the PATH.")
        return False
    except subprocess.SubprocessError as e:
        print(f"Error while scanning IP address {ip}: {e}")
        return False
    
    # If the scan does not detect the IP as active, return False
    return False

def check_path_validity(file_path: str, base_dir: str) -> bool:
    """
    Checks if the path contains path traversal attempts or if it is valid.

    Parameters:
        path (str): The path to check.

    Returns:
        bool: True if the path is safe, False otherwise.
    """
    input_dir = os.path.join(base_dir, "input_files/")
    commonpath = os.path.commonpath([input_dir, os.path.abspath(file_path)])  # Calculate the common path
    commonpath = commonpath + "/"
    if commonpath == input_dir:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return True
        else:
            print(f"Error: The file '{file_path}' does not exist or is not a valid file.")
            return False
    else:
        print("Error: Path traversal attempt not allowed.")
        return False

def get_positive_integer_input() -> int:
    """
    Requests a positive integer input from the user.
    Parameters:
        prompt: The message to show to the user.
    Returns:
        A positive integer.
    """
    print("Enter how many processes to run for network scanning simultaneously: ")
    while True:
        user_input = input()
        if user_input.isdigit() and int(user_input) > 0:
            return int(user_input)
        else:
            print("Error: Enter a positive integer greater than 0.")

def clear_directories(directories: List[str]) -> int:
    """
    Cleans the specified directories by deleting all files inside,
    except the "README.md" file if present.

    Parameters:
        directories (List[str]): List of directory paths to clean.

    Returns:
        int: 0 if cleaning was successful, -1 in case of error.
    """
    for directory_path in directories:
        try:
            # Check if the directory exists
            if os.path.exists(directory_path):
                # Delete all files in the directory except "README.md"
                for file_name in os.listdir(directory_path):
                    file_path = os.path.join(directory_path, file_name)
                    try:
                        if os.path.isfile(file_path) and file_name != "README.md":
                            os.remove(file_path)  # Remove the file
                    except FileNotFoundError:
                        print(f"Error: The file '{file_path}' no longer exists.")
                    except PermissionError:
                        print(f"Error: Insufficient permissions to delete the file '{file_path}'.")
                        return -1
                    except IsADirectoryError:
                        print(f"Error: '{file_path}' is a directory, not a file.")
                    except OSError as e:
                        print(f"System error while deleting the file '{file_path}': {e}")
                        return -1
            else:
                # Create the directory if it does not exist
                try:
                    os.makedirs(directory_path, exist_ok=True)
                except PermissionError:
                    print(f"Error: Insufficient permissions to create the directory '{directory_path}'.")
                    return -1
                except NotADirectoryError:
                    print(f"Error: The path '{directory_path}' is not a directory.")
                    return -1
                except OSError as e:
                    print(f"System error while creating the directory '{directory_path}': {e}")
                    return -1
        except Exception as e:
            print(f"Error while cleaning the directory '{directory_path}': {e}")
            return -1

    return 0  # Success

def scan_single_ip(ip: str, flag_sim: bool) -> bool:
    """
    Scans a single IP address and launches a Docker container if the IP is active.
    Parameters:
        ip: The IP address to scan.
    Returns:
        True if the IP address is active, False otherwise.
    """
    
    print(f"Starting scan of IP address {ip}...")
    
    # Uses the is_ip_active function to check if the IP is active
    if is_ip_active(ip):
        #IP is active, launch the Docker container
        start_docker_containers([ip], 1, flag_sim)
        return True  # Operation completed
    else:
        #IP is not active
        print(f"The IP address {ip} is not active.")
        return False   
    
def scan_ip_list_manager() -> int:
    """
    Scans a list of IP addresses provided by the user or from a file, saves the results to a file, and launches Docker containers for active IP addresses.
    Returns:
        int: 0 if the scan was successful, negative error code otherwise.
    """
    ip_list = []

    # Input choice
    print("Do you want to enter the IP addresses manually or via a file?")
    print("1. Manual entry")
    print("2. Load from file")
    while True:
        input_choice = input("Enter the number of your choice (1-2): ")
        if input_choice in ["1", "2"]:
            break
        else:
            print("Invalid choice. Try again.")

    # Manual entry
    if input_choice == "1":
        print("Enter the IP addresses one at a time. Type '0' to finish entering.")
        while True:
            try:
                ip_input = input("Enter an IP address (or '0' to finish): ")
                if ip_input == "0":
                    break
                try:
                    ip = validate_ip(ip_input)  # Check that the IP is valid
                    ip_list.append(ip_input)  # Add the IP to the list
                except ValueError:
                    print("Error: The entered IP address is not valid. Try again.")
                    continue
                # Add the IP to the list if it is valid
            except Exception as e:
                print(e)

    # Load from file
    elif input_choice == "2":
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        while True:
            try:
                file_name = input("Enter the name of the file containing the IP addresses: ")
                file_path = os.path.join(base_dir, "input_files/" + file_name)
            except Exception as e:
                print(e)
            
            if not check_path_validity(file_path, base_dir):
                print("Try again")
            else:
                break
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    ip = line.strip()
                    try:
                        ip = validate_ip(ip)
                        ip_list.append(ip)
                    except ValueError as e:
                        print(e)
        except Exception as e:
            print(f"Error while reading the file: {e}")
            return -3  # Generic error

    # Check if there are valid IPs
    if not ip_list:
        print("No valid IP addresses provided. Operation cancelled.")
        return -4  # No valid IP

    # Scan the IPs
    active_ips = []

    with ThreadPoolExecutor() as executor:
        future_to_ip = {executor.submit(is_ip_active, ip): ip for ip in ip_list}
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                if future.result():
                    active_ips.append(ip)
            except Exception as e:
                print(f"Error while scanning IP address {ip}: {e}")
                
    active_ips = list(set(active_ips))  # Remove duplicates
    print(f"Active IP addresses found: {len(active_ips)}")
    
    # Save the results
    if active_ips:
        max_containers = get_positive_integer_input()
        start_docker_containers(active_ips, max_containers, False)
    else:
        print("No active IP addresses found.")
        return -5  # No active IP

    return 0  # Success
    
def scan_subnet_and_save_results(subnet_input: str) -> List[str]:
    """
    Scans a subnet (in CIDR format) and saves the results (active IPs) to a file.
    Parameters:
        subnet_input: The subnet to scan in CIDR format (e.g., 192.168.1.0/24).
    Returns:
        A list of active hosts.
    """
    
    print(f"Starting scan of network {subnet_input}...")
    start_time = time.time()  # Start the timer to calculate scan time

    # Nmap command for ICMP Echo Request (ping scan)
    command = ["nmap", "-sn", str(subnet_input)]

    active_hosts = set()  # Use a set to avoid duplicates

    try:
        # Run the nmap command and capture the output
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,  # Capture standard output
            stderr=subprocess.PIPE,   # Capture error output
            check=True  # Raise an exception if the command fails
        )

        # Analyze the output to determine active hosts
        output = result.stdout.decode()
        for line in output.splitlines():
            if "Nmap scan report for" in line:
                ip = line.split()[-1]
                if "(" in ip:  
                    # Remove any DNS names
                    ip = ip.split("(")[-1].strip(")")
                # Add the IP to active hosts
                active_hosts.add(ip)  
        
        if not active_hosts:
            print(f"No active hosts found in subnet {subnet_input}.")
            return list()

        # Stop the timer and calculate the total time
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Print the scan results
        print(f"Scan completed in {elapsed_time:.2f} seconds.")
        print(f"Active hosts: {len(active_hosts)}")

        return list(active_hosts)  # Return the list of active hosts
    
    except FileNotFoundError:
        print("Error: The 'nmap' command was not found. Make sure it is installed and available in the PATH.")
        return list()
    except PermissionError:
        print("Error: Insufficient permissions to create or write to output files.")
        return list()
    except UnicodeDecodeError:
        print("Error: Unable to decode the output of the 'nmap' command.")
        return list()
    except subprocess.CalledProcessError as e:
        print(f"Error: The command returned exit code {e.returncode}")
        return list()
    except Exception as e:
        print(f"Error while scanning subnet {subnet_input}: {e}")
        return list()
    
def subnet_scan_manager(subnet_input: str, cont: int, flag_sim: bool) -> int:
    """
    Scans a subnet using nmap, saves the results, and launches Docker containers for active hosts.
    Parameters:
        subnet_input: The subnet to scan in CIDR format (e.g., 192.168.1.0/24).
    Returns:
        No return value. The function saves the scan results to files and launches Docker containers.
    """
    
    # Scan the network and get active hosts
    result = scan_subnet_and_save_results(subnet_input)
    if not result:
        #No active host or error, error message already sent by the function
        #So no need to print anything
        return -4
    else:
        start_docker_containers(result, cont, flag_sim)
    return 0

def scan_multiple_subnets_manager(file_path: str, cont: int, flag_sim: bool) -> int:
    """
    Scans a list of subnets provided in a file using nmap -iL.
    Parameters:
        file_path: Path to the file containing the subnets in CIDR format.
    Returns:
        0 if the scan was successful, -1 if an error occurred during the scan.
    """
    
    host_list = []
    
    print(f"Starting scan of subnets listed in the file: {file_path}")
    
    try:
        # Read the file and check that all subnets are valid
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                ind = line.strip()
                try:
                    candidate = validate_subnet(ind) or validate_ip(ind)  # Check that the address is valid as subnet or IP
                    host_list.append(candidate)
                except ValueError:
                    print(f"Error: The address '{ind}' is not valid and will be ignored.")
        
        host_list = list(set(host_list))  # Remove duplicates
            
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(f"{ind}\n" for ind in host_list)

        print("All valid addresses/subnets have been saved. Starting scan...")

        # Nmap command to scan subnets from the file
        command = ["nmap", "-sn", "-iL", file_path]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        output = result.stdout.decode()
        error_output = result.stderr.decode()

        if error_output:
            print(f"Error while running Nmap:\n{error_output}")
            return -3  # Error: Problem running Nmap

        # Analyze the output to determine active hosts
        active_hosts = set()
        current_ip = None

        for line in output.splitlines():
            if "Nmap scan report for" in line:
                current_ip = line.split()[-1]
                if "(" in current_ip:
                    current_ip = current_ip.split("(")[-1].strip(")")
            elif "Host is up" in line and current_ip:
                active_hosts.add(current_ip)
                current_ip = None  # Reset current IP

        print(f"Number of active hosts found: {len(active_hosts)}")
        
        # Ask the user how many Docker containers to run simultaneously
        if active_hosts:
            start_docker_containers(list(active_hosts), cont, flag_sim)
        else:
            print("No active IP addresses found.")

        return 0  # Success

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        return -3
    except PermissionError:
        print(f"Error: Insufficient permissions to read or write the file '{file_path}'.")
        return -3
    except UnicodeDecodeError:
        print(f"Error: Unable to read the file '{file_path}' due to undecodable characters.")
        return -3
    except subprocess.CalledProcessError as e:
        print(f"Error: The 'nmap' command returned exit code {e.returncode}.")
        return -3
    except Exception as e:
        print(f"Error while scanning subnets: {e}")
        return -5  # Generic error

def start_docker_containers(ip_list: List[str], max_containers: int, flag_sim: bool) -> None:
    """
    Launches Docker containers for a list of IP addresses, with a maximum of [max_containers] running simultaneously.

    Parameters:
        ip_list (List[str]): List of IP addresses to pass to the containers.
        max_containers (int): Maximum number of containers to run simultaneously.
    """
    console = Console(force_terminal=False) 

    def run_container(ip: str, flag_sim) -> int:
        """
        Function to run a Docker container for a single IP.
        Parameters:
            ip: The IP address to pass to the container.
        Returns:
            No return value.
        """
        console = Console(force_terminal=False)  if flag_sim else Console(force_terminal=True)
        
        if flag_sim:
            try:
                # Log container start
                console.print(f"Starting Docker container for IP {ip}...")
                command = [
                    "/opt/java/openjdk/bin/java",
                    "-cp", "/usr/tsunami/tsunami.jar:/usr/tsunami/plugins/*",
                    "-Dtsunami.config.location=/usr/tsunami/tsunami.yaml",
                    "com.google.tsunami.main.cli.TsunamiCli",
                    f"--ip-v4-target={ip}",
                    "--scan-results-local-output-format=JSON",
                    f"--scan-results-local-output-filename=/usr/Orchestrator/logs/{ip}_results.json"
                ]
                result = subprocess.run(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
                if result.returncode == 0:
                    console.print(f"Container for IP {ip} executed successfully.")
                else:
                    console.print(f"Error running container for IP {ip}.")
                    return -2
                return 0
            except FileNotFoundError:
                console.print("Error: The command '/opt/java/openjdk/bin/java' was not found. Make sure it is installed and available in the PATH.")
                return -3
            except PermissionError:
                console.print(f"Error: Insufficient permissions to run the command or access output files for IP {ip}.")
                return -4
            except subprocess.CalledProcessError as e:
                console.print(f"Error: The command returned exit code {e.returncode} for IP {ip}.")
                return -5
            except OSError as e:
                console.print(f"System error while running container for IP {ip}: {e}")
                return -6
            except Exception as e:
                console.print(f"Error while running Docker container for IP {ip}: {e}")
                return -2
        else:
            try:
                # Log container start
                console.print(f"Starting Docker container for IP {ip}...")
                command = [
                    "/opt/java/openjdk/bin/java",
                    "-cp", "/usr/tsunami/tsunami.jar:/usr/tsunami/plugins/*",
                    "-Dtsunami.config.location=/usr/tsunami/tsunami.yaml",
                    "com.google.tsunami.main.cli.TsunamiCli",
                    f"--ip-v4-target={ip}",
                    "--scan-results-local-output-format=JSON",
                    f"--scan-results-local-output-filename=/usr/Orchestrator/logs/{ip}_results.json"
                ]
                result = subprocess.run(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
                if result.returncode == 0:
                    console.print(f"[green]Container for IP {ip} executed successfully.[/green]")
                else:
                    console.print(f"[red]Error running container for IP {ip}.[/red]")
                    return -2
                return 0
            except FileNotFoundError:
                console.print("[red]Error: The command '/opt/java/openjdk/bin/java' was not found. Make sure it is installed and available in the PATH.[/red]")
                return -3
            except PermissionError:
                console.print(f"[red]Error: Insufficient permissions to run the command or access output files for IP {ip}.[/red]")
                return -4
            except subprocess.CalledProcessError as e:
                console.print(f"[red]Error: The command returned exit code {e.returncode} for IP {ip}.[/red]")
                return -5
            except OSError as e:
                console.print(f"[red]System error while running container for IP {ip}: {e}[/red]")
                return -6
            except Exception as e:
                console.print(f"[red]Error while running Docker container for IP {ip}: {e}[/red]")
                return -2

    if flag_sim:
        #Enable simplified progress bar mode
        with ThreadPoolExecutor(max_workers=int(max_containers)) as executor:
            future_to_ip = {executor.submit(run_container, ip, flag_sim): ip for ip in ip_list}
            completed = 0
            
            # Update the progress bar as containers finish
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    result = future.result()  # Get the task result
                    if result != 0:
                        console.print(f"Error running container for IP {ip}. Return code: {result}")
                except TimeoutError:
                    console.print(f"Error: Timeout while running container for IP {ip}.")
                except CancelledError:
                    console.print(f"Error: The task for IP {ip} was cancelled.")
                except Exception as e:
                    console.print(f"Unexpected error while running container for IP {ip}: {e}")
                finally:
                    completed += 1
                    print(f"Running containers...({completed}/{len(ip_list)}) completed")
    else:
        # Use ThreadPoolExecutor to manage the maximum number of containers
        with ThreadPoolExecutor(max_workers=int(max_containers)) as executor:
            future_to_ip = {executor.submit(run_container, ip, flag_sim): ip for ip in ip_list}

            # Initialize the rich progress bar
            with Progress(
                TextColumn("[bold magenta]{task.description}"),
                SpinnerColumn(spinner_name="dots", style="bold magenta"),
                BarColumn(complete_style="green", bar_width=200),
                "[progress.percentage]{task.percentage:>3.0f}%",
                "•",
                TextColumn("[bold blue]{task.completed}/{task.total}"),
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("Running containers", total=len(ip_list))

                # Update the progress bar as containers finish
                for future in as_completed(future_to_ip):
                    ip = future_to_ip[future]
                    try:
                        result = future.result()  # Get the task result
                        if result != 0:
                            console.print(f"[red]Error running container for IP {ip}. Return code: {result}[/red]")
                    except TimeoutError:
                        console.print(f"[red]Error: Timeout while running container for IP {ip}.[/red]")
                    except CancelledError:
                        console.print(f"[red]Error: The task for IP {ip} was cancelled.[/red]")
                    except Exception as e:
                        console.print(f"[red]Unexpected error while running container for IP {ip}: {e}[/red]")
                    finally:
                        progress.update(task, advance=1)

# Program entry point
if __name__ == "__main__":
    main()