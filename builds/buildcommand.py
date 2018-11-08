import subprocess

class BuildCommand:

    def __init__(self, command, commandtype, commandfile):
        self.command = command
        self.commandtype = commandtype
        self.commandfile = commandfile
    
    def Run(self):
        print(self.commandtype +' ' + self.commandfile)
        self.success = False
        try:
            subprocess.run([self.command], shell=True, capture_output=True, check=True).stdout
            self.success = True
        except subprocess.CalledProcessError as e:
            print(e.stderr.decode("utf-8"))
        return self.success


        
