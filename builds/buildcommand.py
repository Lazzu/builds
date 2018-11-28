import os
import subprocess

from termcolor import colored


class BuildCommand:
    def __init__(self, command, commandtype, displayName, infile, outfile):
        self.command = command
        self.commandtype = commandtype
        self.infile = infile
        self.outfile = outfile
        self.displayName = displayName
        self.success = False
    
    def run(self, pipeline_configuration):
        verbose = pipeline_configuration.get('verbose', False)
        rebuild = pipeline_configuration.get('rebuild', False)

        if self.infile != self.outfile and not rebuild and os.path.isfile(self.infile) and os.path.isfile(self.outfile):
            in_mtime = os.path.getmtime(self.infile)
            out_mtime = os.path.getmtime(self.outfile)
            if out_mtime > in_mtime:
                self.success = True
                return True

        print(colored(self.commandtype, 'green') + ' ' + self.displayName)

        try:
            if verbose:
                print(self.command)

            message = subprocess.run(
                [self.command],
                shell=True,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                check=True
            ).stdout.decode("utf-8")

            self.success = True

        except subprocess.CalledProcessError as e:
            print(colored(self.commandtype + ' failed', 'red'))
            message = e.stderr.decode("utf-8")
        if message:
            message = message.replace('error', colored('error', 'red'))
            print(message)
        return self.success
