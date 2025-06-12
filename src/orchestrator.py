"""
Module `orchestrator.py`

This module coordinates network scanning operations and the launching of Docker containers to analyze scan results.
It is designed to orchestrate the entire scanning process, from input validation to result management, 
in an automated environment.

Includes functionality for:
- Validating IP addresses and subnets.
- Scanning single IPs, lists of IPs, and subnets.
- Launching Docker containers to analyze scan results.
- Managing directories and output files.
- Processing scan results using a log parser.

Usage:
    This module is designed to be executed as the main script to coordinate network scanning operations.
    It can be used both interactively (without arguments) and via command-line arguments.

Execution modes:
    - Interactive: The user can manually choose what to scan (single IP, list of IPs, single subnet, list of subnets).
    - Command-line arguments: The user can directly specify what to scan using options such as:
        - `--single_ip`: Scan a single IP address.
        - `--subnet`: Scan a subnet in CIDR format.
        - `--subnet-list`: Scan a list of subnets from a file.

Handled exceptions:
    - Missing or inaccessible directories.
    - Missing or invalid input files.
    - Errors during IP or subnet scanning.
    - Errors during result processing using the `log_parser` module.

Dependencies:
    - `orch_library`: Support library for scanning and managing results.
    - `log_parser`: Module for processing scan results.
    - `os`, `sys`: For managing paths, directories, and command-line arguments.

"""

import os  # Imports the os module for managing paths and directories
import sys

import log_parser as lp  # Imports functions from the log_parser module
import orch_library as lib  # Imports functions from the function_library module

# Main function that coordinates network scanning and Docker container launching.
def main():
    """
    Main function that coordinates network scanning and Docker container launching.
    Parameters:
        None
    Returns:
        0 on success
    Errors:
        -1: In case of an error during scanning or container launching.
        -2: In case of an error during single IP scanning.
        -3: In case of an error during scanning a list of IPs.
        -4: In case of an error during subnet scanning.
        -5: In case of an error during scanning a list of subnets.
        -6: In case of an error during Docker container execution.
        -7: In case of an error during scanning a list of subnets.
    """
    
    # Paths of directories to clean/create
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parsed_report_dir = os.path.join(base_dir, "Parsed_report")
    tsunami_outputs_dir = os.path.join(base_dir, "logs")
    input_files_dir = os.path.join(base_dir, "input_files/")
    os.makedirs(input_files_dir, exist_ok=True)

    directories = [tsunami_outputs_dir]
    # Cleans the Parsed_report and Tsunami_outputs directories
    if lib.clear_directories(directories) == -1:
        print("Error during directory cleanup.")
        return -1
    
    # Parsing arguments
    args = lib.parse_arguments()
    
    if len(sys.argv) == 1:
        # If no arguments are provided, ask the user what to scan
        print("What would you like to scan?")
        print("1. Single IP")
        print("2. List of IPs")
        print("3. Single subnet")
        print("4. List of subnets")
        # User choice
        while True:
            user_choice = input("Enter the number of your choice (1-4): ")
            if user_choice in ["1", "2", "3", "4"]:
                break
            else:
                print("Invalid choice. Try again.")
        if user_choice == "1":
            while True:
                # Scanning a single IP
                ip_input = input("Enter the IP address to scan: ")
                try:
                    ip = lib.validate_ip(ip_input)  # Validates the IP address
                    break
                except ValueError:
                    print("Error: The entered IP address is invalid.")
                    print("Try again.")
            if not lib.scan_single_ip(ip_input, False):
                return -2
        elif user_choice == "2":
            # Scanning a list of IPs
            if lib.scan_ip_list_manager() < 0:
                return -3
        elif user_choice == "3":
            # Scanning a single subnet
            while True:
                subnet_input = input("Enter the subnet address in CIDR format (e.g., 192.168.1.0/24): ")
                try:
                    sub = lib.validate_subnet(subnet_input)
                except ValueError:
                    print("Error: The provided subnet address is invalid.")
                    print("Try again.")
                    continue
                
                # Uses subnet_scan_manager to manage subnet scanning
                lib.subnet_scan_manager(subnet_input, args.containers, False)
                break

        elif user_choice == "4":
            while True:
                # Scanning a list of subnets
                file_name = input("Enter the name of the file containing subnets in CIDR format: ")
                file_path = os.path.join(input_files_dir, file_name)
                
                if not lib.check_path_validity(file_path, base_dir):
                    print("Try again")
                else:
                    break
            if lib.scan_multiple_subnets_manager(file_path, args.containers, False) < 0:
                return -5
            
    else:
        # Checking provided arguments
        if args.single_ip:
            try:
                ip = lib.validate_ip(args.single_ip)
                if args.simplify:
                    if not lib.scan_single_ip(ip, True):
                        return -2
                else:
                    if not lib.scan_single_ip(ip, False):
                        return -2
            except ValueError:
                print("Error: The provided IP address is invalid.")
                return -1

        elif args.subnet:
            try:
                sub = lib.validate_subnet(args.subnet)
                # Uses subnet_scan_manager to manage subnet scanning
                if args.simplify:
                    lib.subnet_scan_manager(sub, args.containers, True)
                else:
                    lib.subnet_scan_manager(sub, args.containers, False)
            except ValueError:
                print("Error: The provided subnet address is invalid.")

        if args.subnet_list:
            subnet_file = os.path.join(input_files_dir, args.subnet_list)
            if not lib.check_path_validity(subnet_file, base_dir):
                print("Error: The specified subnet file does not exist or is inaccessible.")
                return -1

            if args.simplify:
                if lib.scan_multiple_subnets_manager(subnet_file, args.containers, True) < 0:
                    return -5
            else:
                if lib.scan_multiple_subnets_manager(subnet_file, args.containers, False) < 0:
                    return -5

    # Launches the log_parser.py program at the end of the scan
    print("Docker execution completed.")
    print("Starting log parser...")

    if not os.listdir(tsunami_outputs_dir):
        print(f"Error: No JSON files found in the directory {tsunami_outputs_dir}.")
        return -6
    else:
        result = lp.process_all_json_in_directory(tsunami_outputs_dir, parsed_report_dir)
        if result < 0:
            print("Error during log processing. Check the error messages above for more details.")
            return result  # Propagates the log_parser error code
        else:
            print("Log processing completed successfully.")
            return 0  # Success

# Program entry point
if __name__ == "__main__":
    main()
