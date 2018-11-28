import sys
import os
import importer

from multiprocessing.dummy import Pool as ThreadPool


class BuildPipeline:
    """This will determine the pipeline required for the project and will call correct methods"""

    def __init__(self, projectname, pipeline, command_processor, pipeline_configuration):

        stepobj = importer.import_pipeline(pipeline)
        if stepobj:
            self.step = stepobj(command_processor)
        else:
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
    
    def generate_step(self, step, settings, files):
        func = getattr(self.step, step)
        settings['libraries'] = self.libraries
        settings['library-paths'] = self.library_paths
        settings['shared-library-paths'] = self.shared_library_paths
        settings['include-paths'] = self.include_paths
        settings['arguments'] += self.arguments
        return func(self.projectname, settings, files)

    def run_command(self, command):
        if not command.run(self.pipeline_configuration):
            self.run_command_errors = True
        return self.run_command_errors

    def run_commands(self, build_commands):
        pool = ThreadPool(self.pipeline_configuration.get('jobs', 1))
        pool.map(self.run_command, build_commands)
        pool.close()
        pool.join()
        return not self.run_command_errors

    def run(self, files):
        build_steps = self.settings
        stepsFinished = 0
        for step in build_steps:
            steptype = step.get('type')
            (step_commands, step_files) = self.generate_step(steptype, step, files)
            success = self.run_commands(step_commands)
            if success:
                stepsFinished += 1
                continue
            break
        return stepsFinished
