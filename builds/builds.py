import click
import json
import os
import types
from buildcommand import BuildCommand
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing

default_builds_configuration = {
    'build-settings' : {
        'pipelines' : {
            'C++' : {
                'steps' : [{
                    'type' : 'compile',
                    'input' : 'files',
                    'output' : 'compiled-files',
                    'tool' : 'g++',
                    'arguments' : ['-Wall', '-c $FILE -o $FILE.o']
                },{
                    'type' : 'build',
                    'input' : 'compiled-files',
                    'output' : '$PROJECTNAME-files',
                    'tool' : 'g++',
                    'arguments' : ['-o $PROJECTNAME']
                }]
            }
        }
    },
    'targets': {
        'debug' : {
            'debug' : True,
            'build-arguments' : ["-g","-std=c++11"]
        },
        'release' : {
            'debug' : False,
            'build-arguments' : ["-std=c++11"]
        }
    },
    'projects' : {
        'default' : {
            'library-paths' : [],
            'libraries' : [],
            'pipeline' : 'C++'
        }
    }
}

builds_configuration = {}
active_configuration = {}

def save_configuration(config):
    with open('builds.json', 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4)

if os.path.exists('builds.json'):
    with open('builds.json', mode='r', encoding='utf-8') as file:
        builds_configuration = json.load(file)
else:
    save_configuration(default_builds_configuration)

active_configuration = {**default_builds_configuration, **builds_configuration}

def output_settings(settings):
    click.echo(json.dumps(settings, sort_keys=True, indent=2))

def process_command_string(string, current_project, current_file = ''):
    string = string.replace("$PROJECTNAME", current_project)
    string = string.replace("$FILE", current_file)
    return string

runCommandErrors = False

def RunCommand(command):
    global runCommandErrors
    if not runCommandErrors:
        if not command.Run():
            runCommandErrors = True
    return runCommandErrors

def RunCommands(build_commands):
    pool = ThreadPool(multiprocessing.cpu_count())
    pool.map(RunCommand, build_commands)
    pool.close()
    pool.join()
    return not runCommandErrors

@click.group()
@click.version_option()
def builds():
    """Builds project build management tool.
    This tool manages the project building files.
    """

@builds.group('settings')
def settings():
    """Settings related commands"""

@settings.command('print')
def print_settings():
    """Displays the currently active settings."""
    output_settings(active_configuration)

@builds.command('add')
@click.argument('files', nargs=-1, type=click.Path())
def add(files):
    """Add a file to the build."""
    default_project = active_configuration.setdefault('default_project', 'default')
    projects = active_configuration.setdefault('projects', {'default':{}})
    project = projects.get(default_project)
    projectfiles = project.setdefault('files', [])
    added_files = 0
    for filename in files:
        if filename not in projectfiles:
            projectfiles.append(filename)
            click.echo('+ ' + filename)
            added_files += 1
        else:
            click.echo('# ' + filename + " already in project")
    click.echo("Added " + str(added_files) + " files ")
    save_configuration(active_configuration)


@builds.command('build')
@click.argument('project', default=active_configuration.get('default_project', 'default'))
@click.option('target', '--target', default='debug', help='Select target to build (debug/release)')
def build(project, target):
    """Build the project.
    This builds the project with the current settings in builds.json file.
    """
    active_project = active_configuration.setdefault('default_project', 'default')
    projects = active_configuration.setdefault('projects', {'default':{}})
    if projects is None:
        click.echo("No projects configured")
        return
    project = projects.get(active_project)
    if project is None:
        click.echo("No project found with name " + active_project)
        return
    projectfiles = project.setdefault('files', [])
    build_settings = active_configuration.get('build-settings');
    if build_settings is None:
        click.echo("Build settings is not configured")
        return
    pipelines = build_settings.get('pipelines')
    if pipelines is None:
        click.echo("No pipelines in build settings configured")
        return
    project_pipeline = project.get('pipeline')
    if project_pipeline is None:
        click.echo('No pipeline set for project ' + active_project)
        return
    pipeline = pipelines.get(project_pipeline)
    if pipeline is None:
        click.echo('No pipeline configuration for pipeline ' + project_pipeline)
    build_steps = pipeline.get('steps')
    out_files = {}
    stepsFinished = 0
    for step in build_steps:
        steptype = step.get('type')
        buildCommands = []
        #click.echo('Step ' + steptype)
        if steptype == 'compile':
            for project_file in projectfiles:
                command = step.get('tool') + " " + " ".join(str(x) for x in step.get('arguments'))
                command = process_command_string(command, active_project, project_file)
                buildCommands.append(BuildCommand(command, steptype, project_file))
                step_files = out_files.setdefault(step.get('output'), [])
                outfile = project_file + ".o"
                if outfile in step_files:
                    continue
                step_files.append(outfile)
        if steptype == 'build':
            command = step.get('tool') + " " + " ".join(str(x) for x in step.get('arguments')) + " " + " ".join(str(x) for x in out_files[step.get('input')])
            command = process_command_string(command, active_project)
            buildCommands.append(BuildCommand(command, steptype, active_project))
        success = RunCommands(buildCommands)
        if success:
            stepsFinished += 1
            continue
        break
    click.echo('Finished ' + str(stepsFinished) + ' steps')
        


@builds.group('set')
def set():
    """Manages settings."""


@set.command('default_project')
@click.argument('project', type=str)
def set_default_project(project):
    """Sets the default project."""
    click.echo('Set %s as the default project' % (project))

#@set.command('default_project')
#@click.argument('x', type=float)
#@click.argument('y', type=float)
#@click.option('ty', '--moored', flag_value='moored',
#              default=True,
#              help='Moored (anchored) mine. Default.')
#@click.option('ty', '--drifting', flag_value='drifting',
#              help='Drifting mine.')
#def set_default_project(x, y, ty):
#    """Sets a mine at a specific coordinate."""
#    click.echo('Set %s mine at %s,%s' % (ty, x, y))



if __name__ == '__main__':
    builds()