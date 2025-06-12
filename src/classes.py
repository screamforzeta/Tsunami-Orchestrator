"""
Module `entry.py`

This module defines the `Entry` class, which represents an entity with an IP address, a port, and an associated service.
It includes methods to convert the object into JSON format and to represent it as a string.

Usage:
    The `Entry` class can be used to manage and serialize information related to IP addresses,
    ports, and services in the context of network scanning or analysis.

Classes:
    - Entry: Represents an entity with an IP address, port, and service.

Functions:
    - main: Entry point of the module (currently empty).
"""

import json

class Entry:
    """
    Class `Entry`

    Represents an entity with an IP address, a port, and an associated service.

    Attributes:
        ip_address (str): The IP address of the entity.
        port (int | str): The port associated with the IP address. Default: "Unknown".
        transportprotocol (str): The transport protocol used (e.g., TCP, UDP). Default: "Unknown".
        servicename (str): The name of the service associated with the port. Default: "Unknown".
        softwarename (str): The name of the software associated with the service. Default: "Unknown".
        softwareversion (str): The version of the software associated with the service. Default: "Unknown".
        cpes (str): The Common Platform Enumerations (CPEs) associated with the service. Default: "Unknown".
        banner (str): The service banner, if available. Default: "None".

    Methods:
        to_json: Converts the `Entry` object into a JSON representation.
        __str__: Represents the `Entry` object as a string.
    """

    def __init__(self, ip_address, port, tp, service, softwarename, softwareversion, cpes, banner):
        """
        Initializes an instance of the `Entry` class.

        Parameters:
            ip_address (str): The IP address of the entity.
            port (int, optional): The port associated with the IP address. Default: 0.
            service (str, optional): The service associated with the port. Default: "Unknown".
        """
        self.ip_address = ip_address
        self.port = port if port is not None else "Unknown"
        self.transportprotocol = tp if tp is not None else "Unknown"
        self.servicename = service if service is not None else "Unknown"
        self.softwarename = softwarename if softwarename is not None else "Unknown"
        self.softwareversion = softwareversion if softwareversion is not None else "Unknown"
        self.cpes = cpes if cpes is not None else "Unknown"
        self.banner = banner if banner is not None else "None"
        
    def to_json(self):
        """
        Converts the `Entry` object into a JSON representation.

        Returns:
            str: A JSON string representing the `Entry` object.
        """
        x = {
            "ip_address": self.ip_address,
            "port": self.port,
            "service": self.servicename,
            "transportprotocol": self.transportprotocol,
            "softwarename": self.softwarename,
            "softwareversion": self.softwareversion,
            "cpes": self.cpes,
            "banner": self.banner
        }
        return json.dumps(x, indent=4)
    
    def __str__(self):
        """
        Represents the `Entry` object as a string.

        Returns:
            str: A string describing the `Entry` object with IP address, port, and service.
        """
        return (
            f"IP: {self.ip_address}, "
            f"Port: {self.port}, "
            f"Service: {self.servicename}, "
            f"Transport Protocol: {self.transportprotocol}, "
            f"Software Name: {self.softwarename}, "
            f"Software Version: {self.softwareversion}, "
            f"CPEs: {self.cpes}"
        )
        
class Vuln_entry:
    """
    Class `Vuln_entry`

    Represents an entity with information related to a vulnerability associated with an IP address and a port.

    Attributes:
        ip (str): The IP address of the entity.
        port (int | str): The port associated with the IP address. Default: "Unknown".
        vuln_name (str): The name of the vulnerability. Default: "Unknown".
        publisher (str): The publisher of the vulnerability. Default: "Unknown".
        severity (str): The severity level of the vulnerability. Default: "Unknown".
        descr (str): The description of the vulnerability. Default: "Unknown".
        rec (str): The recommendation to mitigate the vulnerability. Default: "Unknown".

    Methods:
        to_json: Converts the `Vuln_entry` object into a JSON representation.
        __str__: Represents the `Vuln_entry` object as a string.
    """
    
    def __init__(self, ip_address, port, vuln_name, publisher, severity, descr, rec):
        """
        Initializes an instance of the `Vuln_entry` class.

        Parameters:
            ip_address (str): The IP address of the entity.
            port (int, optional): The port associated with the IP address. Default: 0.
            service (str, optional): The service associated with the port. Default: "Unknown".
        """
        self.ip = ip_address
        self.port = port if port is not None else "Unknown"
        self.vuln_name = vuln_name if vuln_name is not None else "Unknown"
        self.publisher = publisher if publisher is not None else "Unknown"
        self.severity = severity if severity is not None else "Unknown"
        self.descr = descr if descr is not None else "Unknown"
        self.rec = rec if rec is not None else "Unknown"
        
    def to_json(self):
        """
        Converts the `Vuln_entry` object into a JSON representation.

        Returns:
            str: A JSON string representing the `Vuln_entry` object.
        """
        x = {
            "ip_address": self.ip,
            "port": self.port,
            "vuln_name": self.vuln_name,
            "publisher": self.publisher,
            "severity": self.severity,
            "descr": self.descr,
            "rec": self.rec
        }
        return json.dumps(x, indent=4)
    
    def __str__(self):
        """
        Represents the `Vuln_entry` object as a string.

        Returns:
            str: A string describing the `Vuln_entry` object with IP address, port, and vulnerability details.
        """
        return (
            f"IP: {self.ip}, "
            f"Port: {self.port}, "
            f"Vuln Name: {self.vuln_name}, "
            f"Publisher: {self.publisher}, "
            f"Severity: {self.severity}, "
            f"Descr: {self.descr}, "
            f"Rec: {self.rec}"
        )
    
def main():
    """
    Entry point of the module.

    Currently does not perform any operations.
    """
    return