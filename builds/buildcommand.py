import os
import subprocess
from termcolor import colored

class BuildCommand:

    def __init__(self, command, commandtype, commandfile):
        self.command = command
        self.commandtype = commandtype
        self.commandfile = commandfile
    
    def Run(self, pipeline_configuration):
        verbose = pipeline_configuration.get('verbose', False);
        rebuild = pipeline_configuration.get('rebuild', False);
        if not rebuild and os.path.isfile(self.commandfile + ".o"):
            in_mtime = os.path.getmtime(self.commandfile)
            out_mtime = os.path.getmtime(self.commandfile + ".o")
            if out_mtime > in_mtime:
                return True

        print(colored(self.commandtype, 'green') + ' ' + self.commandfile)
        self.success = False
        try:
            if verbose:
                print(self.command)
            message = subprocess.run([self.command], shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True).stdout.decode("utf-8")
            self.success = True
        except subprocess.CalledProcessError as e:
            print(colored(self.commandtype + ' failed', 'red'))
            message = e.stderr.decode("utf-8")
        if message:
            message = message.replace('error', colored('error', 'red'))
            print(message)
        return self.success
