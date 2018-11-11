import click
import json
import os
import types
import multiprocessing
from buildcommand import BuildCommand
from buildpipeline import BuildPipeline
from commandpreprocessor import CommandPreprocessor
from colorama import init
from termcolor import colored

init() # colorama to work on all platforms

default_builds_configuration = {
    'build-settings' : {
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
    },
    'targets': {
        'debug' : {
            'debug' : True,
            'arguments' : ["-g","-std=c++11"]
        },
        'release' : {
            'debug' : False,
            'arguments' : ["-std=c++11"]
        }
    },
    'projects' : {
        'default' : {
            'pipeline' : 'C++',
            'build-settings' : {
                'library-paths' : [],
                'libraries' : [],
            }
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
    click.echo(colored(json.dumps(settings, sort_keys=True, indent=2), 'green'))

def process_command_string(string, current_project, current_file = ''):
    string = string.replace("$PROJECTNAME", current_project)
    string = string.replace("$FILE", current_file)
    return string

runCommandErrors = False

@click.group()
@click.version_option()
def builds():
    """Builds project build management tool.\n\n
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
    """Add file(s) to the build."""
    default_project = active_configuration.setdefault('default_project', 'default')
    projects = active_configuration.setdefault('projects', {'default':{}})
    project = projects.get(default_project)
    projectfiles = project.setdefault('files', [])
    added_files = 0
    for filename in files:
        if filename not in projectfiles:
            projectfiles.append(filename)
            click.echo(colored('+ ', 'green') + filename)
            added_files += 1
        else:
            click.echo(colored('# ', 'yellow') + filename + colored(" already in project", 'yellow'))
    click.echo("Added " + str(added_files) + " files ")
    save_configuration(active_configuration)

@builds.command('remove')
@click.argument('files', nargs=-1, type=str)
def remove(files):
    """Remove file(s) from the build."""
    default_project = active_configuration.setdefault('default_project', 'default')
    projects = active_configuration.setdefault('projects', {'default':{}})
    project = projects.get(default_project)
    project_files = project.setdefault('files', [])
    removed_files = 0
    for filename in files:
        if filename in project_files:
            project_files.remove(filename)
            click.echo(colored('- ', 'red') + filename)
            removed_files += 1
        else:
            click.echo(colored('# ', 'yellow') + filename + colored(" not in project", 'yellow'))
    click.echo("Removed " + str(removed_files) + " files")
    save_configuration(active_configuration)


@builds.command('build')
@click.argument('project', default=active_configuration.get('default_project', 'default'))
@click.option('target', '--target', default='debug', help='Select target to build (debug/release)')
@click.option('verbose', '--verbose', flag_value=True, help='Verbose command output')
@click.option('jobs', '--jobs', default=multiprocessing.cpu_count(), help='Run commands in parallel with x amount of jobs')
def build(project, target, verbose, jobs):
    """This builds the selected project with the current settings in builds.json file. 
    Selected project defaults to the currently active project set in the builds.json file."""
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
    build_settings = active_configuration.get('build-settings')
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
    pipeline_settings = pipelines.get(project_pipeline)
    pipeline_configuration = {
        'jobs' : jobs,
        'verbose' : verbose
    }
    pipeline = BuildPipeline(active_project, project_pipeline, pipeline_settings, CommandPreprocessor(active_project), pipeline_configuration)
    if pipeline is None:
        click.echo('No pipeline configuration for pipeline ' + project_pipeline)
    stepsFinished = pipeline.Run(projectfiles)
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