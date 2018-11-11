import subprocess
from termcolor import colored

class BuildCommand:

    def __init__(self, command, commandtype, commandfile):
        self.command = command
        self.commandtype = commandtype
        self.commandfile = commandfile
    
    def Run(self, verbose=False):
        print(colored(self.commandtype, 'green') + ' ' + self.commandfile)
        self.success = False
        try:
            if verbose:
                print(self.command)
            subprocess.run([self.command], shell=True, capture_output=True, check=True).stdout
            self.success = True
        except subprocess.CalledProcessError as e:
            print(colored(self.commandtype + ' failed', 'red'))
            message = e.stderr.decode("utf-8")
            message = message.replace('error', colored('error', 'red'))
            print(message)
        return self.success
