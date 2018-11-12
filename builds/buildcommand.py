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
            message = subprocess.run([self.command], shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True).stdout.decode("utf-8")
            self.success = True
        except subprocess.CalledProcessError as e:
            print(colored(self.commandtype + ' failed', 'red'))
            message = e.stderr.decode("utf-8")
        if message:
            message = message.replace('error', colored('error', 'red'))
            print(message)
        return self.success
