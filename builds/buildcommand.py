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

    def process_message(self, message, pipeline_configuration):
        tag_error = 'error:'
        tag_warning = 'warning:'
        tag_hint = 'required from here'
        if pipeline_configuration.get('machine-readable', False):
            lines = message.split("\n")
            output = []
            for line in lines:
                out = False
                for tag in [tag_error, tag_warning]:
                    tag_pos = line.find(tag)
                    if tag_pos == -1:
                        continue
                    message_pos = tag_pos + len(tag)
                    while line[message_pos].isspace():
                        message_pos = message_pos + 1
                    faux_tag_pos = tag_pos
                    while True:
                        if faux_tag_pos < 0:
                            break
                        c = line[faux_tag_pos]
                        if c == ':':
                            tag_pos = faux_tag_pos
                            break
                        if c.isdigit():
                            tag_pos = faux_tag_pos + 1
                            break
                        faux_tag_pos = faux_tag_pos - 1
                    if tag == tag_error:
                        out = "error"
                    if tag == tag_warning:
                        out = "warning"
                    out = out + " " + line[0:tag_pos] + " " + line[message_pos:len(line)]
                    break
                if out != False:
                    output.append(out)
            message = "\n".join(output)
        elif pipeline_configuration.get('verbose', False):
            message = message.replace('error', colored('error', 'red'))
        else:
            lines = message.split("\n")
            output = []
            for line in lines:
                tag_error_pos = line.find(tag_error)
                if tag_error_pos == -1:
                    tag_error_pos = line.find(tag_warning)
                if tag_error_pos == -1:
                    tag_error_pos = line.find(tag_hint)
                if tag_error_pos == -1:
                    continue
                output.append(line)
            message = "\n".join(output)
            message = message.replace('error', colored('error', 'red'))
            message = message.replace('warning', colored('warning', 'yellow'))
        return message

    def run(self, pipeline_configuration):
        verbose = pipeline_configuration.get('verbose', False)
        rebuild = pipeline_configuration.get('rebuild', False)
        machine_readable = pipeline_configuration.get('machine-readable', False)

        if self.infile != self.outfile and not rebuild and os.path.isfile(self.infile) and os.path.isfile(self.outfile):
            in_mtime = os.path.getmtime(self.infile)
            out_mtime = os.path.getmtime(self.outfile)
            if out_mtime > in_mtime:
                self.success = True
                return True

        if machine_readable:
            print(self.commandtype + ' ' + self.displayName)
        else:
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
            if machine_readable:
                print(self.commandtype + '-failed')
            else:
                print(colored(self.commandtype + ' failed', 'red'))
            message = e.stderr.decode("utf-8")
        if message:
            message = self.process_message(message, pipeline_configuration)
            print(message)
        return self.success
