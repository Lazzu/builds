
class CommandPreprocessor:
    def __init__(self, current_project):
        self.current_project = current_project

    def Process(self, string, current_file):
        string = string.replace("$PROJECTNAME", self.current_project)
        string = string.replace("$FILE", current_file)
        return string