#!/usr/bin/python3

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
    'projects' : {
        'default' : {
            'pipeline' : 'CPP',
            'build-settings' : {
                'include-paths' : [],
                'library-paths' : [],
                'libraries' : [],
            },
            "targets": {
                "debug": {
                    "arguments": [
                        "-g",
                        "-std=c++11"
                    ],
                    "debug": True
                },
                "release": {
                    "arguments": [
                        "-std=c++11"
                    ],
                    "debug": False
                }
            }
        }
    }
}

builds_configuration = {}
active_configuration = {}

def search_config_path(current_path=''):
    while True:
        file_path = current_path + '.builds/builds.json'
        if not os.path.exists(file_path):
            next_path = '../' + current_path
            if not os.path.exists(next_path):
                return '.builds/builds.json'
            current_path = next_path
            continue
        return file_path
    

builds_file = search_config_path()

def save_configuration(config):
    with open(builds_file, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4)

if os.path.exists(builds_file):
    with open(builds_file, mode='r', encoding='utf-8') as file:
        builds_configuration = json.load(file)
else:
    if input(colored('Builds not initialized.', 'red') + ' Do you want to initialize a new builds file in the current directory? (y/N) ') == 'y':
        os.makedirs('.builds', exist_ok=True)
        save_configuration(default_builds_configuration)

active_configuration = {**default_builds_configuration, **builds_configuration}

def output_settings(settings):
    click.echo(colored(json.dumps(settings, sort_keys=True, indent=2), 'green'))

def process_command_string(string, current_project, current_file = ''):
    string = string.replace("$PROJECTNAME", current_project)
    string = string.replace("$FILE", current_file)
    return string

def add_file(file_list, filename):
    filename = filename.replace('./', '')
    if os.path.isdir(filename):
        print('Dir')
    file_list.append(filename)
    click.echo(colored('+ ', 'green') + filename)

def add_interactive_dir(file_list, dirname):
    files = [dirname + '/' + f for f in os.listdir(dirname) if os.path.isfile(dirname + '/' + f)]
    dirs = [dirname + '/' + d for d in os.listdir(dirname) if os.path.isdir(dirname + '/' + d) and len(os.listdir(dirname + '/' + d)) > 0]
    added = 0
    for f in files:
        if not os.path.isfile(f):
            continue
        f = f.replace('./', '')
        if f in file_list:
            continue
        if input('Add ' + f + ' ? (y/N) ') == 'y':
            add_file(file_list, f)
            added += 1
    if len(dirs) > 0:
        if input('Add files from subdirectories? (y/N) ') == 'y':
            for d in dirs:
                if input('Add files from dir ' + d + '? (y/N) ') == 'y':
                    add_interactive_dir(file_list, d)
    return added

def add_interactive(file_list):
    added = 0
    added += add_interactive_dir(file_list, '.')
    return added


@click.group()
@click.version_option()
def builds():
    """Builds project build management tool.\n\n
    This tool manages the project building files.
    """

@builds.group('project')
def project():
    """Displays the currently active settings."""


@project.command('show')
def project_show():
    """Show the currently active project name"""
    default_project = active_configuration.get('default_project', 'default')
    print(default_project)

@project.command('rename')
@click.argument('newname', nargs=1, type=str)
@click.option('target', '-p', default=active_configuration.get('default_project', 'default'), help='Rename the given project instead of the currently active project')
def project_rename(newname, target):
    """Rename the currently active project"""
    default_project = active_configuration.get('default_project', 'default')
    projects = active_configuration.get('projects', {'default':{}})
    project = projects.get(target)
    projects.pop(target, None)
    projects[newname] = project
    if default_project == target:
        active_configuration['default_project'] = newname
    save_configuration(active_configuration)

@builds.group('settings')
def settings():
    """Settings related commands"""


@settings.command('print')
def print_settings():
    """Displays the currently active settings."""
    output_settings(active_configuration)



@builds.command('add-library')
@click.argument('args', nargs=-1, type=str)
@click.option('path', '-p', default='', help='Add library path along with the library')
def add_library(args, path):

    # Figure out correct variables
    default_project = active_configuration.setdefault('default_project', 'default')
    projects = active_configuration.setdefault('projects', {'default':{}})
    project = projects.get(default_project)
    build_settings = project.get("build-settings")
    libs = build_settings.get('libraries')
    lib_paths = build_settings.get('library-paths')

    # Add path if it is valid
    if path and os.path.isdir('./' + path):
        if path not in lib_paths:
            lib_paths.append(path)
            print(colored('+ path ', 'green') + path)
        else:
            print(colored('# path ', 'yellow') + path + colored(' Already configured', 'yellow'))
        

    # Add libraries from the argument list
    if libs == None: libs = []
    for lib in args:
        if lib not in libs:
            libs.append(lib)
            print(colored('+ ', 'green') + lib)
        else:
            print(colored('# ', 'yellow') + lib + colored(' Already configured', 'yellow'))
    
    save_configuration(active_configuration)

@builds.command('add-include')
@click.argument('args', nargs=-1, type=str)
def add_include(args):

    # Figure out correct variables
    default_project = active_configuration.setdefault('default_project', 'default')
    projects = active_configuration.setdefault('projects', {'default':{}})
    project = projects.get(default_project)
    build_settings = project.get("build-settings")
    inc_paths = build_settings.get('include-paths')

    # Add path if it is valid
    for path in args:
        if path and os.path.isdir('./' + path):
            if path not in inc_paths:
                inc_paths.append(path)
                print(colored('+ path ', 'green') + path)
            else:
                print(colored('# path ', 'yellow') + path + colored(' Already configured', 'yellow'))
    
    save_configuration(active_configuration)


@builds.command('add')
@click.argument('files', nargs=-1, type=str)
@click.option('interactive', '-i', flag_value=True, help='Add files interactively. Lists all files not yet in the project in the current directory, and asks if you want to add them or not.')
def add(files, interactive):
    """Add file(s) to the build."""
    default_project = active_configuration.setdefault('default_project', 'default')
    projects = active_configuration.setdefault('projects', {'default':{}})
    project = projects.get(default_project)
    projectfiles = project.setdefault('files', [])
    added_files = 0
    if(not interactive):
        for filename in files:
            if not os.path.isfile(filename):
                continue
            if filename not in projectfiles:
                add_file(projectfiles, filename)
                added_files += 1
            else:
                click.echo(colored('# ', 'yellow') + filename + colored(" already in project", 'yellow'))
    else:
        added_files = add_interactive(projectfiles)
    click.echo("Added " + str(added_files) + " files")
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
@click.option('rebuild', '--rebuild', flag_value=True, help='Clean and re-build .o files')
@click.option('jobs', '--jobs', default=multiprocessing.cpu_count(), help='Run commands in parallel with x amount of jobs')
def build(project, target, verbose, rebuild, jobs):
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
    project_libraries = project.get('libraries', [])
    project_library_paths = project.get('library-paths', [])
    project_include_paths = project.get('include-paths', [])
    targets = project.get('targets')
    project_target = targets.get(target)
    target_arguments = project_target.get('arguments')
    project_pipeline = project.get('pipeline')

    if project_pipeline is None:
        click.echo('No pipeline set for project ' + active_project)
        return

    pipeline_configuration = {
        'jobs' : jobs,
        'verbose' : verbose,
        'rebuild' : rebuild,
        'libraries' : project_libraries,
        'library-paths' : project_library_paths,
        'include-paths' : project_include_paths,
        'arguments' : target_arguments
    }

    pipeline = BuildPipeline(active_project, project_pipeline, CommandPreprocessor(active_project), pipeline_configuration)

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
