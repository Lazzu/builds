import sys
import os
from buildcommand import BuildCommand
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing

class CPP:
    '''This is the C++ pipeline step functionality for builds'''

    def __init__(self, settings, command_processor):
        self.settings = settings
        self.command_processor = command_processor

    def compile(self, project_name, settings, files):
        commands = []
        step_files = []
        for project_file in files:
            command = settings.get('tool') + " " + " ".join(str(x) for x in settings.get('arguments'))
            command = self.command_processor.Process(command, project_file)
            outfile = project_file + ".o"
            commands.append(BuildCommand(command, 'compile', outfile))
            if outfile in step_files:
                continue
            step_files.append(outfile)
        return (commands, step_files)

    def build(self, project_name, settings, files):
        oFiles = []
        for file in files:
            file = file + '.o'
            if file not in oFiles:
                oFiles.append(file)
        command = settings.get('tool') + " " + " ".join(str(x) for x in settings.get('arguments')) + " " + " ".join(str(x) for x in oFiles)
        command = self.command_processor.Process(command, project_name)
        commands = [BuildCommand(command, 'build', project_name)]
        step_files = [project_name]
        return (commands, step_files)


class BuildPipeline:
    '''This will determine the pipeline required for the project and will call correct methods'''

    def __init__(self, projectname, pipeline, settings, command_processor, pipeline_configuration):
        try:
            stepobj = getattr(sys.modules[__name__], pipeline)
            self.step = stepobj(settings, command_processor)
        except AttributeError:
            print('No pipeline ' + pipeline + ' found for project ' + projectname + '.')
            sys.exit(os.EX_CONFIG)
        self.projectname = projectname
        self.settings = settings
        self.run_command_errors = False
        self.pipeline_configuration = pipeline_configuration
    
    def GenerateStep(self, step, settings, files):
        func = getattr(self.step, step)
        return func(self.projectname, settings, files)

    def RunCommand(self, command):
        if not command.Run(self.pipeline_configuration.get('verbose', False)):
            self.run_command_errors = True
        return self.run_command_errors

    def RunCommands(self, build_commands):
        pool = ThreadPool(self.pipeline_configuration.get('jobs', 1))
        pool.map(self.RunCommand, build_commands)
        pool.close()
        pool.join()
        return not self.run_command_errors

    def Run(self, files):
        build_steps = self.settings.get('steps')
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
    
    
