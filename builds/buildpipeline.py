import sys
import os
from buildcommand import BuildCommand
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing

class CPP:
    '''This is the C++ pipeline step functionality for builds'''

    def __init__(self, command_processor):
        self.command_processor = command_processor

    def compile(self, project_name, settings, files):
        commands = []
        step_files = []
        include_paths = ['-I' + inc for inc in settings['include-paths']]
        for project_file in files:
            command = settings.get('tool') + " " + " ".join(str(x) for x in settings.get('arguments')) + " " + " ".join(include_paths);
            command = self.command_processor.Process(command, project_file)
            outfile = project_file + ".o"
            if outfile in step_files:
                continue
            commands.append(BuildCommand(command, 'compile', project_file))
            step_files.append(outfile)
        return (commands, step_files)

    def build(self, project_name, settings, files):
        oFiles = []
        for file in files:
            file = file + '.o'
            if file not in oFiles:
                oFiles.append(file)
        libraries = ['-l' + lib for lib in settings['libraries']]
        library_paths = ['-L' + lib for lib in settings['library-paths']]
        shared_library_paths = ['-Wl,-rpath,' + slib for slib in settings['shared-library-paths']]
        command = settings.get('tool') + " " + " ".join(library_paths) + " " + " ".join(shared_library_paths) + " " + " ".join(libraries) + " " + " ".join(str(x) for x in settings.get('arguments')) + " " + " ".join(str(x) for x in oFiles)
        command = self.command_processor.Process(command, project_name)
        commands = [BuildCommand(command, 'build', project_name)]
        step_files = [project_name]
        return (commands, step_files)
    
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


class BuildPipeline:
    '''This will determine the pipeline required for the project and will call correct methods'''

    def __init__(self, projectname, pipeline, command_processor, pipeline_configuration):
        try:
            stepobj = getattr(sys.modules[__name__], pipeline)
            self.step = stepobj(command_processor)
        except AttributeError:
            print('No pipeline ' + pipeline + ' found for project ' + projectname + '.')
            sys.exit(os.EX_CONFIG)
        self.projectname = projectname
        self.settings = self.step.get_default_pipeline()
        self.run_command_errors = False
        self.pipeline_configuration = pipeline_configuration
        self.libraries = pipeline_configuration['libraries']
        self.library_paths = pipeline_configuration['library-paths']
        self.shared_library_paths = pipeline_configuration['shared-library-paths']
        self.include_paths = pipeline_configuration['include-paths']
        self.arguments = pipeline_configuration['arguments']
    
    def GenerateStep(self, step, settings, files):
        func = getattr(self.step, step)
        settings['libraries'] = self.libraries
        settings['library-paths'] = self.library_paths
        settings['shared-library-paths'] = self.shared_library_paths
        settings['include-paths'] = self.include_paths
        settings['arguments'] += self.arguments
        return func(self.projectname, settings, files)

    def RunCommand(self, command):
        if not command.Run(self.pipeline_configuration):
            self.run_command_errors = True
        return self.run_command_errors

    def RunCommands(self, build_commands):
        pool = ThreadPool(self.pipeline_configuration.get('jobs', 1))
        pool.map(self.RunCommand, build_commands)
        pool.close()
        pool.join()
        return not self.run_command_errors

    def Run(self, files):
        build_steps = self.settings
        stepsFinished = 0
        for step in build_steps:
            steptype = step.get('type')
            (step_commands, step_files) = self.GenerateStep(steptype, step, files)
            success = self.RunCommands(step_commands)
            if success:
                stepsFinished += 1
                continue
            break
        return stepsFinished
    
    
