import os

from buildcommand import BuildCommand


class CPP:
    """This is the C++ pipeline step functionality for builds"""

    def __init__(self, command_processor):
        self.command_processor = command_processor

    def compile(self, project_name, settings, files):
        commands = []
        step_files = []
        for project_file in files:
            command, outfile = self.compile_step(project_name, settings, project_file)
            if outfile in step_files:
                continue
            commands.append(BuildCommand(command, 'compile', project_file, project_file, outfile))
            step_files.append(outfile)
        return commands, step_files

    def compile_step(self, project_name, settings, project_file):
        include_paths = ['-I' + inc for inc in settings['include-paths']]
        command = settings.get('tool') + " " + " ".join(
            str(x) for x in settings.get('arguments')
        ) + " " + " ".join(include_paths)
        command = self.command_processor.Process(command, project_file)
        outfile = project_file + ".o"
        return command, outfile

    def build(self, project_name, settings, files):
        oFiles = []
        newestOFile = ''
        newestOFileTime = 0
        for currentFile in files:
            currentFile = currentFile + '.o'
            if currentFile not in oFiles:
                oFiles.append(currentFile)
                fileTime = os.path.getmtime(currentFile)
                if fileTime > newestOFileTime:
                    newestOFile = currentFile
                    newestOFileTime = fileTime
        libraries = ['-l' + lib for lib in settings['libraries']]
        library_paths = ['-L' + lib for lib in settings['library-paths']]
        shared_library_paths = ['-Wl,-rpath,' + slib for slib in settings['shared-library-paths']]
        command = settings.get('tool') + " " + " ".join(library_paths) + " " + " ".join(shared_library_paths) + " " + " ".join(libraries) + " " + " ".join(str(x) for x in settings.get('arguments')) + " " + " ".join(str(x) for x in oFiles)
        command = self.command_processor.Process(command, project_name)
        commands = [BuildCommand(command, 'build', project_name, newestOFile, project_name)]
        step_files = [project_name]
        return commands, step_files

    def get_default_pipeline(self):
        return [
            {
                "arguments": [
                    "-Wall",
                    "-c $FILE -o $FILE.o"
                ],
                "input": "files",
                "output": "compiled-files",
                "tool": "g++",
                "type": "compile"
            },
            {
                "arguments": [
                    "-o $PROJECTNAME"
                ],
                "input": "compiled-files",
                "output": "$PROJECTNAME-files",
                "tool": "g++",
                "type": "build"
            }
        ]

