class CPPEvents:
    def __init__(self, steps, settings, pipeline_configuration):
        self.steps = steps
        self.settings = settings
        self.pipeline_configuration = pipeline_configuration

    def file_changed(self, file):
        self.steps.compile_step('', self.settings, file).run(self.pipeline_configuration)
