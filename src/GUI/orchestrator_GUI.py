"""
orchestrator_GUI.py

This module provides a graphical user interface (GUI) for the Orchestrator application.
It allows users to configure and execute scans for single IPs, subnets, or multiple subnets/IPs.
The GUI is built using the customtkinter library and includes features such as dynamic tabs,
logging, and manual instructions.

Classes:
    App: The main application class that initializes and manages the GUI.

Functions:
    change_appearance_event(new_appearance_mode): Changes the appearance mode of the GUI.
    change_scaling_event(new_scaling): Adjusts the scaling of the GUI.
    get_dynamic_frame(): Displays the dynamic frame for Orchestrator execution.
    open_how_to(): Displays the "How To" manual in the GUI.
    stop_scan(): Stops the currently running scan.
    close(): Closes the application safely.
    start_single_ip_scan(): Starts a scan for a single IP address.
    start_single_subnet_scan(): Starts a scan for a single subnet.
    start_multiple_subnets_scan(): Starts a scan for multiple subnets/IPs.
"""

import tkinter
import tkinter.messagebox
import threading
import os
import subprocess
import signal
import customtkinter
import GUI_library as lib

# Set the appearance mode and default color theme for the customtkinter library: "System", "Dark" o "Light"
customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"

# Set the default color theme for customtkinter: "blue", "green" o "dark-blue"
customtkinter.set_default_color_theme("dark-blue")

class App(customtkinter.CTk):
    """
    The main application class for the Orchestrator GUI.

    This class initializes the GUI, manages user interactions, and handles scan operations
    for single IPs, subnets, and multiple subnets/IPs.

    Methods:
        __init__(): Initializes the application and its components.
        change_appearance_event(new_appearance_mode): Changes the appearance mode of the GUI.
        change_scaling_event(new_scaling): Adjusts the scaling of the GUI.
        get_dynamic_frame(): Displays the dynamic frame for Orchestrator execution.
        open_how_to(): Displays the "How To" manual in the GUI.
        stop_scan(): Stops the currently running scan.
        close(): Closes the application safely.
        start_single_ip_scan(): Starts a scan for a single IP address.
        start_single_subnet_scan(): Starts a scan for a single subnet.
        start_multiple_subnets_scan(): Starts a scan for multiple subnets/IPs.
    """

    def __init__(self):
        """
        Initializes the application and its components.

        Configures the main window, sidebar, dynamic tabs, and other GUI elements.
        Sets up default appearance and scaling options.
        """
        super().__init__()
        # Reference to the current running process
        self.current_process = None  

        # Configure the main window title
        self.title("Orchestrator Interface")  

        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Center the window on the screen
        window_width = 1200
        window_height = 600
        position_x = int((screen_width - window_width) / 2)
        position_y = int((screen_height - window_height) / 2)

        # Set the geometry of the main window
        self.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

        # Set the window to be always on top
        self.lift()
        self.attributes('-topmost', True)  
        # Remove the "always on top" attribute after a short delay
        self.after(100, lambda: self.attributes('-topmost', False)) 

        # Configure the main grid layout (4 columns)
        self.grid_columnconfigure(0, weight=0)  # Column 0: Sidebar (not expanding)
        self.grid_columnconfigure(1, weight=1)  # Column 1: Log frame (expands)
        self.grid_columnconfigure(2, weight=1)  # Column 2: Manual frame (expands)
        self.grid_columnconfigure(3, weight=1)  # Column 3: Dynamic frame (expands)
        self.grid_rowconfigure(0, weight=1)  # Row 0: Main content (expands)

        # Create a main frame that will hold the sidebar and other widgets
        self.left_sidebar_frame = customtkinter.CTkFrame(self) 
        self.left_sidebar_frame.grid(row=0, column=0, rowspan=4, padx=(10, 0), pady=(10, 10), sticky="nsew")  
        self.left_sidebar_frame.grid_rowconfigure(3, weight=1)  
        self.left_sidebar_frame.grid_rowconfigure(6, weight=1)

        # Add a label to the sidebar frame
        self.side_label = customtkinter.CTkLabel(
            self.left_sidebar_frame, text="Commands:", font=customtkinter.CTkFont(size=20, weight="bold")
        )
        self.side_label.grid(row=0, column=0, padx=20, pady=(20, 10)) 

        # Create buttons for the sidebar
        self.man_btn = customtkinter.CTkButton(self.left_sidebar_frame, text="How To", command=self.open_how_to)
        self.man_btn.grid(row=1, column=0, padx=20, pady=10)
        self.dyn_mode_btn = customtkinter.CTkButton(self.left_sidebar_frame, text="Start Orchestrator", command=self.get_dynamic_frame)
        self.dyn_mode_btn.grid(row=2, column=0, padx=20, pady=10)
        
        # Create buttons for starting and stopping scans
        self.stop_btn = customtkinter.CTkButton(self.left_sidebar_frame, text="Stop", command=self.stop_scan)
        self.stop_btn.grid(row=4, column=0, padx=20, pady=10) 
        self.stop_btn.configure(state="disabled")  

        self.exit_btn = customtkinter.CTkButton(self.left_sidebar_frame, text="Exit", command=self.close)
        self.exit_btn.grid(row=5, column=0, padx=20, pady=10) 

        # Add an appearance mode label and option menu
        self.appearance_mode_label = customtkinter.CTkLabel(self.left_sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.left_sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_event
        )
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 10))

        # Add a label and dropdown menu to change the UI scaling
        self.scaling_label = customtkinter.CTkLabel(self.left_sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(
            self.left_sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event
        )
        self.scaling_optionemenu.grid(row=10, column=0, padx=20, pady=(10, 20))

        # Configure the frame for the textbox and buttons
        self.log_frame = customtkinter.CTkFrame(self)
        self.log_frame.grid(row=0, column=1, columnspan=2, sticky="nsew", padx=(10, 10), pady=(10, 10))

        # Configure the grid of the log frame
        self.log_frame.grid_columnconfigure(0, weight=1)  # Column 0 expands
        self.log_frame.grid_columnconfigure(1, weight=0)  # Column 1 does not expand
        self.log_frame.grid_columnconfigure(2, weight=0)  # Column 2 does not expand
        self.log_frame.grid_columnconfigure(3, weight=1)  # Column 3 expands
        self.log_frame.grid_rowconfigure(0, weight=1)  # Row 0 (textbox) expands
        self.log_frame.grid_rowconfigure(1, weight=0)  # Row 1 (buttons) does not expand

        # Create the textbox to view Orchestrator logs
        self.log_txtbox = customtkinter.CTkTextbox(self.log_frame, width=250)
        self.log_txtbox.grid(row=0, column=0, columnspan=4, padx=(20, 20), pady=(20, 10), sticky="nsew")  # The textbox expands

        # Configure the frame for the manual
        self.man_frame = customtkinter.CTkFrame(self)

        # Configure the grid of the frame to expand
        self.man_frame.grid_columnconfigure(0, weight=1)  # Allows column 0 to expand
        self.man_frame.grid_rowconfigure(0, weight=0)  # Allows row 0 to expand
        self.man_frame.grid_rowconfigure(1, weight=1)  # Allows row 1 to expand
        
        self.man_label = customtkinter.CTkLabel(
            self.man_frame, text="Instructions:", font=customtkinter.CTkFont(size=20, weight="bold")
        )

        # Configure the textbox to occupy all available space
        self.man_txtbox = customtkinter.CTkTextbox(self.man_frame)

        # Create a tab view for dynamic execution of Orchestrator
        self.dynamic_frame = customtkinter.CTkFrame(self)
        
        # Configure the internal grid of the frame for the tab view
        self.dynamic_frame.grid_columnconfigure(0, weight=1)  # Allows column 0 of the frame to expand
        self.dynamic_frame.grid_rowconfigure(0, weight=1)  # Allows row 0 of the frame to expand

        # Add the tab view to the frame
        self.dyn_tabview = customtkinter.CTkTabview(self.dynamic_frame)
        self.dyn_tabview.grid(row=0, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew")  # The dyn_tabview expands

        self.dyn_tabview.add("Single IP")  # Adds a tab
        self.dyn_tabview.add("Single Subnet")  # Adds a second tab
        self.dyn_tabview.add("Multiple Subnets/IPs")  # Adds a third tab
        
        self.dyn_tabview.tab("Single IP").grid_columnconfigure(0, weight=1)  # Configures the grid of the tab
        self.dyn_tabview.tab("Single Subnet").grid_columnconfigure(0, weight=1)
        self.dyn_tabview.tab("Multiple Subnets/IPs").grid_columnconfigure(0, weight=1)

        # Add a label, a textbox, and a "Start" button to the first tab
        self.lbl_sing_ip = customtkinter.CTkLabel(self.dyn_tabview.tab("Single IP"), text="Enter IP Address:")
        self.lbl_sing_ip.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        self.txt_sing_ip = customtkinter.CTkEntry(self.dyn_tabview.tab("Single IP"), placeholder_text="e.g., 192.168.1.1")
        self.txt_sing_ip.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")

        # Add a label and 4 checkboxes to the "Single IP" tab
        self.lbl_info_ip = customtkinter.CTkLabel(
            self.dyn_tabview.tab("Single IP"), 
            text="Select which volumes to add (for more information, read the wiki)"
        )
        self.lbl_info_ip.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")

        self.cbox_1_ip = customtkinter.CTkCheckBox(self.dyn_tabview.tab("Single IP"), text="Save tsunami outputs")
        self.cbox_1_ip.grid(row=3, column=0, padx=20, pady=(5, 5), sticky="w")
        self.cbox_1_ip.select()  # Selects the checkbox by default

        self.btn_sing_ip = customtkinter.CTkButton(self.dyn_tabview.tab("Single IP"), text="Start", command=self.start_single_ip_scan)
        self.btn_sing_ip.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="ew")

        # Add 4 checkboxes and a "Start" button to the "Single Subnet" tab
        self.lbl_sing_sub = customtkinter.CTkLabel(self.dyn_tabview.tab("Single Subnet"), text="Enter Subnet:")
        self.lbl_sing_sub.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        self.txt_sing_sub = customtkinter.CTkEntry(self.dyn_tabview.tab("Single Subnet"), placeholder_text="e.g., 192.168.1.0/24")
        self.txt_sing_sub.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")

        # Add a label and 4 checkboxes to the "Single Subnet" tab
        self.lbl_info_ip = customtkinter.CTkLabel(
            self.dyn_tabview.tab("Single Subnet"), 
            text="Select which volumes to add (for more information, read the wiki)"
        )
        self.lbl_info_ip.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")

        self.cbox_1_sub = customtkinter.CTkCheckBox(self.dyn_tabview.tab("Single Subnet"), text="Save tsunami outputs")
        self.cbox_1_sub.grid(row=3, column=0, padx=20, pady=(5, 5), sticky="w")
        self.cbox_1_sub.select()  # Selects this checkbox by default
        
        self.lbl_cont_sub = customtkinter.CTkLabel(self.dyn_tabview.tab("Single Subnet"), text="Insert the number of the container to scan:")
        self.lbl_cont_sub.grid(row=4, column=0, padx=20, pady=(20, 5), sticky="w")
        self.txt_cont_sub = customtkinter.CTkEntry(self.dyn_tabview.tab("Single Subnet"), placeholder_text="e.g., 1")
        self.txt_cont_sub.grid(row=5, column=0, padx=20, pady=(5, 10), sticky="ew")

        self.btn_sing_sub = customtkinter.CTkButton(self.dyn_tabview.tab("Single Subnet"), text="Start", command=self.start_single_subnet_scan)
        self.btn_sing_sub.grid(row=6, column=0, padx=20, pady=(10, 20), sticky="ew")

        # Add 4 checkboxes and a "Start" button to the "Multiple Subnets/IPs" tab
        self.lbl_m_sub = customtkinter.CTkLabel(self.dyn_tabview.tab("Multiple Subnets/IPs"), text="Enter the name of the file containing the list of subnets/IPs:")
        self.lbl_m_sub.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        self.txt_m_sub = customtkinter.CTkEntry(self.dyn_tabview.tab("Multiple Subnets/IPs"), placeholder_text="e.g., subnets.txt")
        self.txt_m_sub.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
        
        # Add a label and 4 checkboxes to the "Multiple Subnets/IPs" tab
        self.lbl_info_ip = customtkinter.CTkLabel(
            self.dyn_tabview.tab("Multiple Subnets/IPs"), 
            text="Select which volumes to add (for more information, read the wiki)"
        )
        self.lbl_info_ip.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")

        self.cbox_1_msub = customtkinter.CTkCheckBox(self.dyn_tabview.tab("Multiple Subnets/IPs"), text="Save tsunami outputs")
        self.cbox_1_msub.grid(row=3, column=0, padx=20, pady=(5, 5), sticky="w")
        self.cbox_1_msub.select()  # Selects this checkbox by default
        
        self.lbl_cont_msub = customtkinter.CTkLabel(self.dyn_tabview.tab("Multiple Subnets/IPs"), text="Insert the number of the container to scan:")
        self.lbl_cont_msub.grid(row=4, column=0, padx=20, pady=(20, 5), sticky="w")
        self.txt_cont_msub = customtkinter.CTkEntry(self.dyn_tabview.tab("Multiple Subnets/IPs"), placeholder_text="e.g., 1")
        self.txt_cont_msub.grid(row=5, column=0, padx=20, pady=(5, 10), sticky="ew")

        self.btn_m_sub = customtkinter.CTkButton(self.dyn_tabview.tab("Multiple Subnets/IPs"), text="Start", command=self.start_multiple_subnets_scan)
        self.btn_m_sub.grid(row=6, column=0, padx=20, pady=(10, 20), sticky="ew")

        # Set default values for various widgets
        self.appearance_mode_optionemenu.set("System")
        self.scaling_optionemenu.set("100%")
        self.log_txtbox.insert(
            "0.0",
             "Waiting for the Orchestrator to start...\n"
             "Please select the Orchestrator mode from the sidebar.\n"
             "If you want to exit the application, please click on the Exit button.\n"
        )
        self.log_txtbox.configure(state="disabled")  # Disable editing of the textbox
        self.open_how_to()

    def change_appearance_event(self, new_appearance_mode: str):
        """
        Changes the appearance mode of the GUI.

        Args:
            new_appearance_mode (str): The new appearance mode ("Light", "Dark", or "System").
        """
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        """
        Adjusts the scaling of the GUI.

        Args:
            new_scaling (str): The new scaling percentage (e.g., "100%").
        """
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def get_dynamic_frame(self):
        """
        Displays the dynamic frame for Orchestrator execution.

        Hides the manual frame and shows the dynamic frame with tabs for scan configuration.
        """
        self.dyn_mode_btn.configure(state="disabled")
        self.man_btn.configure(state="enabled")
        self.man_btn.update()
        self.man_frame.grid_remove()
        self.dynamic_frame.grid(row=0, column=3, sticky="nsew", padx=(0, 10), pady=(10, 10))

    def open_how_to(self):
        """
        Displays the "How To" manual in the GUI.

        Reads the manual content from the `man.txt` file and displays it in a textbox.
        """
        self.man_btn.configure(state="disabled")
        self.dyn_mode_btn.configure(state="enabled")
        self.man_btn.update()
        self.dynamic_frame.grid_remove()  # Hides the tab view
        self.man_frame.grid(row=0, column=3, sticky="nsew", padx=(0, 10), pady=(10, 10))
        self.man_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")  # Positions the label in the grid
        self.man_txtbox.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")  # Expands the textbox
        self.man_txtbox.configure(state="normal")  # Enables editing of the textbox
        self.man_txtbox.delete("1.0", "end")  # Clears the textbox
        
        current_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the current directory
        man_file_path = os.path.join(current_dir, "man.txt")  # Relative path to man.txt
        
        try:
            with open(man_file_path, "r", encoding="utf-8") as file:
                manual_content = file.read()
                self.man_txtbox.insert("1.0", manual_content)  # Inserts the content into the textbox
        except FileNotFoundError:
            self.man_txtbox.insert("1.0", "Error: 'man.txt' file not found.")
        except Exception as e:
            self.man_txtbox.insert("1.0", f"Error reading 'man.txt': {e}")
        
        self.man_txtbox.configure(state="disabled")  # Makes the textbox read-only

    def stop_scan(self):
        """
        Stops the currently running scan and all its child processes (including Docker containers).
        """
        if self.current_process:
            try:
                os.killpg(os.getpgid(self.current_process.pid), signal.SIGTERM)
                # Stops all containers with prefix orchestrator_
                subprocess.run("sudo docker ps -q --filter 'name=orchestrator_' | xargs -r sudo docker rm -f", shell=True, check=True)
                self.log_txtbox.insert("end", "\nScan forcibly stopped by user.\n")
            except Exception as e:
                self.log_txtbox.insert("end", f"\nError stopping process: {e}\n")
            finally:
                self.stop_btn.configure(state="disabled")
                self.btn_sing_ip.configure(state="enabled")
                self.btn_sing_sub.configure(state="enabled")
                self.btn_m_sub.configure(state="enabled")
                self.dyn_tabview.configure(state="normal")
                self.log_txtbox.configure(state="disabled")
                self.current_process = None
        else:
            self.log_txtbox.insert("end", "\nNo process is currently running.\n")

    def close(self):
        """
        Closes the application safely.

        If a scan is running, prompts the user to stop it before exiting.
        """
        if self.current_process:
            tkinter.messagebox.showwarning("Warning", "A process is still running. Please stop it before exiting.")
        else:
            self.destroy()

    def start_single_ip_scan(self):
        """
        Starts a scan for a single IP address.

        Retrieves the IP address from the input field and initiates the scan in a separate thread.
        """
        ip = self.txt_sing_ip.get()

        if ip != "":
            self.log_txtbox.delete("1.0", "end")  # Clears the textbox
            self.log_txtbox.configure(state="normal")  # Enables editing of the textbox

            self.stop_btn.configure(state="enabled")  # Enables the stop button
            self.stop_btn.update()
            self.dynamic_frame.grid_remove()  # Hides the tab view
            self.log_frame.grid_configure(row=0, column=1, columnspan=3, sticky="nsew", padx=(10, 10), pady=(10, 10))  # Expands the log frame
            self.man_btn.configure(state="disabled")  # Disables the start button
            
            # Gets the values of the checkboxes
            volumes = [
                self.cbox_1_ip.get()
            ]
            
            # Callback function to update the textbox
            def log_callback(line):
                print(f"Log callback received: {line}")  # Debug: prints the output to the console
                self.log_txtbox.insert("end", line)
                self.log_txtbox.see("end")

            # Callback function for thread completion
            def on_thread_complete():
                # Restores the state of the widgets
                self.man_btn.configure(state="enabled")
                self.man_btn.update()
                self.dyn_tabview.configure(state="normal")
                # Restores the log_frame to its original size
                self.log_frame.grid_configure(row=0, column=1, columnspan=2, sticky="nsew", padx=(10, 10), pady=(10, 10))
                # Makes the dynamic_frame visible again
                self.dynamic_frame.grid(row=0, column=3, sticky="nsew", padx=(0, 10), pady=(10, 10))
                self.stop_btn.configure(state="disabled")
                self.log_txtbox.see("end")  # Scrolls down
                self.log_txtbox.configure(state="disabled")
                self.current_process = None  # Resets the process reference

            # Function to execute in the thread
            def thread_function():
                try:
                    self.current_process = lib.scan_single_ip(ip, volumes, log_callback)  # Saves the process reference
                    if self.current_process:
                        self.current_process.wait()  # Waits for the process to finish
                    else:
                        self.log_txtbox.insert("end", "Error: Process could not be started.\n")
                except Exception as e:
                    self.log_txtbox.insert("end", f"Error during scan: {e}\n")
                finally:
                    self.after(0, on_thread_complete)  # Executes the callback in the main thread

            # Starts the scan function in a separate thread
            threading.Thread(target=thread_function).start()
        else:
            tkinter.messagebox.showerror("Error", "Please enter a valid IP address.")

    def start_single_subnet_scan(self):
        """
        Starts a scan for a single subnet.

        Retrieves the subnet and container number from the input fields and initiates the scan
        in a separate thread.
        """
        subnet = self.txt_sing_sub.get()
        
        # Gets the values of the checkboxes
        volumes = [
            self.cbox_1_sub.get()
        ]
        
        cont = self.txt_cont_sub.get()  # Gets the container number
        if cont == "" or cont == "0" or not cont.isdigit(): 
            tkinter.messagebox.showerror("Error", "Please enter a valid container number (>0).")
        else:
            if subnet != "":
                self.log_txtbox.delete("1.0", "end")  # Clears the textbox
                self.log_txtbox.configure(state="normal")  # Enables editing of the textbox

                self.stop_btn.configure(state="enabled")  # Enables the stop button
                self.stop_btn.update()
                self.dynamic_frame.grid_remove()  # Hides the tab view
                self.log_frame.grid_configure(row=0, column=1, columnspan=3, sticky="nsew", padx=(10, 10), pady=(10, 10))  # Expands the log frame
                self.man_btn.configure(state="disabled")  # Disables the start button 

                # Callback function to update the textbox
                def log_callback(line):
                    print(f"Log callback received: {line}")  # Debug: prints the output to the console
                    self.log_txtbox.insert("end", line)
                    self.log_txtbox.see("end")

                # Callback function for thread completion
                def on_thread_complete():
                    # Restores the state of the widgets
                    self.man_btn.configure(state="enabled")
                    self.man_btn.update()
                    self.dyn_tabview.configure(state="normal")
                    # Restores the log_frame to its original size
                    self.log_frame.grid_configure(row=0, column=1, columnspan=2, sticky="nsew", padx=(10, 10), pady=(10, 10))
                    # Makes the dynamic_frame visible again
                    self.dynamic_frame.grid(row=0, column=3, sticky="nsew", padx=(0, 10), pady=(10, 10))
                    self.stop_btn.configure(state="disabled")
                    self.log_txtbox.see("end")  # Scrolls down
                    self.log_txtbox.configure(state="disabled")  # Makes the textbox read-only
                    self.current_process = None  # Resets the process reference

                # Function to execute in the thread
                def thread_function():
                    try:
                        self.current_process = lib.scan_single_subnet(subnet, volumes, int(cont), log_callback)  # Saves the process reference
                        if self.current_process:
                            self.current_process.wait()  # Waits for the process to finish
                        else:
                            self.log_txtbox.insert("end", "Error: Process could not be started.\n")
                    except Exception as e:
                        self.log_txtbox.insert("end", f"Error during scan: {e}\n")
                    finally:
                        self.after(0, on_thread_complete)  # Executes the callback in the main thread

                # Starts the scan function in a separate thread
                threading.Thread(target=thread_function).start()
            else:
                tkinter.messagebox.showerror("Error", "Please enter a valid Subnet.")

    def start_multiple_subnets_scan(self):
        """
        Starts a scan for multiple subnets/IPs.

        Retrieves the file name and container number from the input fields and initiates the scan
        in a separate thread.
        """
        file_name = self.txt_m_sub.get()  # Gets the file name
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Moves up two levels
        input_dir = os.path.join(base_dir, "input_files/")  # Path to the input_files folder
        file_path = os.path.join(input_dir + file_name)  # Constructs the full path
        cont = self.txt_cont_msub.get()  # Gets the container number

        # Gets the values of the checkboxes
        volumes = [
            self.cbox_1_msub.get()
        ]
        
        commonpath = os.path.commonpath([input_dir, os.path.abspath(file_path)])  # Calculates the common path
        commonpath = commonpath + "/"  # Adds the trailing slash for comparison

        if file_name == "":
            tkinter.messagebox.showerror("Error", "Please enter a valid file name.")
        elif cont == "" or cont == "0" or not cont.isdigit(): 
            tkinter.messagebox.showerror("Error", "Please enter a valid container number (>0).")
        elif commonpath != input_dir:
            tkinter.messagebox.showerror("Error", "Please enter a valid file name in the input_files folder.")
        elif not os.path.exists(file_path) or not os.path.isfile(file_path):
            tkinter.messagebox.showerror("Error", f"File '{file_name}' does not exist in the input_files folder.")
        else:
            self.log_txtbox.delete("1.0", "end")  # Clears the textbox
            self.log_txtbox.configure(state="normal")  # Enables editing of the textbox

            self.stop_btn.configure(state="enabled")  # Enables the stop button
            self.stop_btn.update()
            self.dynamic_frame.grid_remove()  # Hides the tab view
            self.log_frame.grid_configure(row=0, column=1, columnspan=3, sticky="nsew", padx=(10, 10), pady=(10, 10))  # Expands the log frame
            self.man_btn.configure(state="disabled")  # Disables the start button

            # Callback function to update the textbox
            def log_callback(line):
                print(f"Log callback received: {line}")  # Debug: prints the output to the console
                self.log_txtbox.insert("end", line)
                self.log_txtbox.see("end")

            # Callback function for thread completion
            def on_thread_complete():
                # Restores the state of the widgets
                self.man_btn.configure(state="enabled")
                self.man_btn.update()
                self.dyn_tabview.configure(state="normal")
                # Restores the log_frame to its original size
                self.log_frame.grid_configure(row=0, column=1, columnspan=2, sticky="nsew", padx=(10, 10), pady=(10, 10))
                # Makes the dynamic_frame visible again
                self.dynamic_frame.grid(row=0, column=3, sticky="nsew", padx=(0, 10), pady=(10, 10))
                self.stop_btn.configure(state="disabled")
                self.log_txtbox.see("end")  # Scrolls down
                self.log_txtbox.configure(state="disabled")
                self.current_process = None  # Resets the process reference

            # Function to execute in the thread
            def thread_function():
                try:
                    self.current_process = lib.scan_multiple_subnets(file_name, volumes, int(cont), log_callback)  # Saves the process reference
                    if self.current_process:
                        self.current_process.wait()  # Waits for the process to finish
                    else:
                        self.log_txtbox.insert("end", "Error: Process could not be started.\n")
                except Exception as e:
                    self.log_txtbox.insert("end", f"Error during scan: {e}\n")
                finally:
                    self.after(0, on_thread_complete)  # Executes the callback in the main thread

            # Starts the scan function in a separate thread
            threading.Thread(target=thread_function).start()

# Punto di ingresso principale dell'applicazione
if __name__ == "__main__":
    # Entry point of the application.
    # Creates an instance of the App class and starts the main event loop.
    app = App()
    app.mainloop()
