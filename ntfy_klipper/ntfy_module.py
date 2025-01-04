# Klipper extension for Ntfy.sh notification
#
# Copyright (C) 2024 Matthew Debbink <matthew@debb.ink>
#
# This file may be distributed under the terms of the GNU AGPLv3 license.

import http.client

class NtfyClass:

    def __init__(self, config):
        self.name = config.get_name().split()[-1]
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')

        # configuration from [ntfy_module] section in printer.cfg
        self.server = config.get('server', 'ntfy.sh')
        self.port = config.get('port', 443)
        self.token = config.get('token', None)
        self.topic = config.get('topic')
        self.title = config.get('title', 'Klipper Notification')
        self.verbose = config.getboolean('verbose', False)
        
        # register gcode commands
        self.gcode.register_command(
            "NTFY",
            self.cmd_NTFY,
            desc=self.cmd_NTFY_help)

    cmd_NTFY_help = "Sending message to Ntfy.sh server"

    def cmd_NTFY(self, params):
        message = params.get('MSG', '')
        title = params.get('TITLE', self.title)

        if message == '':
            self.gcode.respond_info('Ntfy notification for Klipper.\nUSAGE: NTFY MSG="message" [TITLE="title"]\nTITLE parameter is optional')
            return

        # send message
        if self.verbose:
            self.gcode.respond_info(f"Sending Ntfy message: {title} - {message}")

        url = f"https://{self.server}/{self.topic}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Title": title
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            # Parse the URL to get the hostname and path
            parsed_url = http.client.urlsplit(url)
            connection = http.client.HTTPSConnection(parsed_url.hostname, parsed_url.port or 443, timeout=5)
            
            # Send the POST request
            connection.request("POST", parsed_url.path, body=message, headers=headers)
            response = connection.getresponse()
            
            # Read and print the response
            response_data = response.read().decode()
            if self.verbose: 
                self.gcode.respond_info(f"Status: {response.status} {response.reason}")
                self.gcode.respond_info(f"Response: {response_data}")

        except Exception as e:
            if self.verbose:
                self.gcode.respond_info(f"Request failed: {e}")

        finally:
            connection.close()

def load_config(config):
    return NtfyClass(config)