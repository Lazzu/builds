
class CommandPreprocessor:
    def __init__(self, current_project):
        self.current_project = current_project

    def Process_string(self, string, current_file):
        string = string.replace("$PROJECTNAME", self.current_project)
        string = string.replace("$FILE", current_file)
        return string

    def Process(self, data, current_file):
        if type(data) is list:
            for string in data:
                string = self.Process_string(string, current_file)
            return data
        return self.Process_strig(data, current_file)

