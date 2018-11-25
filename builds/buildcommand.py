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

    def subprocess_run(*popenargs, input=None, check=False, **kwargs):
        if input is not None:
            if 'stdin' in kwargs:
                raise ValueError('stdin and input arguments may not both be used.')
            kwargs['stdin'] = subprocess.PIPE
        if 'bufsize' in kwargs:
            kwargs['bufsize'] = Int(kwargs['bufsize'])

        process = subprocess.Popen(*popenargs, **kwargs)

        try:
            stdout, stderr = process.communicate(input)
        except:
            process.kill()
            process.wait()
            raise

        retcode = process.poll()

        if check and retcode:
            raise subprocess.CalledProcessError(
                retcode, process.args, output=stdout, stderr=stderr)

        return retcode, stdout, stderr

    
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

            retcode, stdout, stderr = self.subprocess_run(
                [self.command],
                shell=True,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                check=True
            )
            
            message = stdout.decode("utf-8")

            self.success = True

        except subprocess.CalledProcessError as e:
            print(colored(self.commandtype + ' failed', 'red'))
            message = e.stderr.decode("utf-8")
        if message:
            message = message.replace('error', colored('error', 'red'))
            print(message)
        return self.success
