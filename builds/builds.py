#!/usr/bin/python3

import json
import multiprocessing
import os
import click
from termcolor import colored
from buildpipeline import BuildPipeline
from commandpreprocessor import CommandPreprocessor
from watcher import Watcher
from colorama import init

init()  # colorama to work on all platforms

DEFAULT_BUILDS_CONFIGURATION = {
    'projects' : {
        'default' : {
            'pipeline' : 'CPP',
            'build-settings' : {
                'include-paths' : [],
                'shared-library-paths' : [],
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

BUILDSFILENAME = '.buildsfile'


def search_config_path():
    found_path = ""
    file_path = BUILDSFILENAME
    while not found_path:
        if not os.path.exists(file_path):
            next_path = '../' + file_path
            if not os.path.exists(next_path):
                found_path = BUILDSFILENAME
            file_path = next_path
        else:
            found_path = file_path
    return found_path


builds_file = search_config_path()


def save_configuration(config):
    with open(builds_file, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4)


if os.path.exists(builds_file):
    with open(builds_file, mode='r', encoding='utf-8') as file:
        builds_configuration = json.load(file)
else:
    if input(colored('Builds not initialized.', 'red') +
             ' Do you want to initialize a new builds file in the current directory? (y/N) ') == 'y':
        save_configuration(DEFAULT_BUILDS_CONFIGURATION)

active_configuration = {**DEFAULT_BUILDS_CONFIGURATION, **builds_configuration}


def output_settings(settings_out):
    click.echo(colored(json.dumps(settings_out, sort_keys=True, indent=2), 'green'))


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
    added = 0
    do_continue = True
    while do_continue:
        do_continue = False

        files = [
            dirname + '/' + f
            for f in os.listdir(dirname)
            if os.path.isfile(dirname + '/' + f)
        ]
        dirs = [
            dirname + '/' + d
            for d in os.listdir(dirname)
            if os.path.isdir(dirname + '/' + d) and len(os.listdir(dirname + '/' + d)) > 0
        ]

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
                        dirname = d
                        do_continue = True
        
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
@click.option('target', '-p', default=active_configuration.get('default_project', 'default'),
              help='Rename the given project instead of the currently active project')
def project_rename(newname, target):
    """Rename the currently active project"""
    default_project = active_configuration.get('default_project', 'default')
    projects = active_configuration.get('projects', {'default': {}})
    project_settings = projects.get(target)
    projects.pop(target, None)
    projects[newname] = project_settings
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
    project_settings = projects.get(default_project)
    build_settings = project_settings.get("build-settings")
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
    if libs is None:
        libs = []
    for lib in args:
        if lib not in libs:
            libs.append(lib)
            print(colored('+ ', 'green') + lib)
        else:
            print(colored('# ', 'yellow') + lib + colored(' Already configured', 'yellow'))
    
    save_configuration(active_configuration)


@builds.command('add-shared-library')
@click.argument('args', nargs=-1, type=str)
@click.option('path', '-p', default='', help='Add shared library path along with the library')
def add_library(args, path):

    # Figure out correct variables
    default_project = active_configuration.setdefault('default_project', 'default')
    projects = active_configuration.setdefault('projects', {'default':{}})
    project_settings = projects.get(default_project)
    build_settings = project_settings.get("build-settings")
    libs = build_settings.get('libraries')
    slib_paths = build_settings.get('shared-library-paths')

    # Add path if it is valid
    if path and os.path.isdir('./' + path):
        if path not in slib_paths:
            slib_paths.append(path)
            print(colored('+ path ', 'green') + path)
        else:
            print(colored('# path ', 'yellow') + path + colored(' Already configured', 'yellow'))

    # Add libraries from the argument list
    if libs is None:
        libs = []
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
    project_settings = projects.get(default_project)
    build_settings = project_settings.get("build-settings")
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
@click.option('interactive', '-i', flag_value=True,
              help='Add files interactively. Lists all files not yet in the project in the current directory, '
                   'and asks if you want to add them or not.')
def add(files, interactive):
    """Add file(s) to the build."""
    default_project = active_configuration.setdefault('default_project', 'default')
    projects = active_configuration.setdefault('projects', {'default':{}})
    project_settings = projects.get(default_project)
    project_files = project_settings.setdefault('files', [])
    added_files = 0
    if not interactive:
        for filename in files:
            if not os.path.isfile(filename):
                continue
            if filename not in project_files:
                add_file(project_files, filename)
                added_files += 1
            else:
                click.echo(colored('# ', 'yellow') + filename + colored(" already in project", 'yellow'))
    else:
        added_files = add_interactive(project_files)
    click.echo("Added " + str(added_files) + " files")
    save_configuration(active_configuration)


@builds.command('remove')
@click.argument('files', nargs=-1, type=str)
def remove(files):
    """Remove file(s) from the build."""
    default_project = active_configuration.setdefault('default_project', 'default')
    projects = active_configuration.setdefault('projects', {'default':{}})
    project_settings = projects.get(default_project)
    project_files = project_settings.setdefault('files', [])
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
@click.argument('project_name', default=active_configuration.get('default_project', 'default'))
@click.option('target', '--target', default='debug', help='Select target to build (debug/release)')
@click.option('verbose', '--verbose', flag_value=True, help='Verbose command output')
@click.option('rebuild', '--rebuild', flag_value=True, help='Clean and re-build .o files')
@click.option('jobs', '--jobs', default=multiprocessing.cpu_count(),
              help='Run commands in parallel with x amount of jobs')
@click.option('run', '--run', flag_value=True, help='Run executable output after building')
def build(project_name, target, verbose, rebuild, jobs, run):
    """This builds the selected project with the current settings in BUILDSFILENAME file. 
    Selected project defaults to the currently active project set in the BUILDSFILENAME file."""

    projects = active_configuration.setdefault('projects', {'default': {}})

    if projects is None:
        click.echo("No projects configured")
        return

    project_settings = projects.get(project_name)

    if project_settings is None:
        click.echo("No project found with name " + project_name)
        return

    project_files = project_settings.setdefault('files', [])
    build_settings = project_settings.get('build-settings', [])
    project_libraries = build_settings.get('libraries', [])
    project_library_paths = build_settings.get('library-paths', [])
    project_shared_library_paths = build_settings.get('shared-library-paths', [])
    project_include_paths = build_settings.get('include-paths', [])
    targets = project_settings.get('targets')
    project_target = targets.get(target)
    target_arguments = project_target.get('arguments')
    project_pipeline = project_settings.get('pipeline')

    if project_pipeline is None:
        click.echo('No pipeline set for project ' + project_name)
        return

    pipeline_configuration = {
        'jobs' : jobs,
        'verbose' : verbose,
        'rebuild' : rebuild,
        'libraries' : project_libraries,
        'library-paths' : project_library_paths,
        'shared-library-paths' : project_shared_library_paths,
        'include-paths' : project_include_paths,
        'arguments' : target_arguments
    }

    pipeline = BuildPipeline(
        project_name,
        project_pipeline,
        CommandPreprocessor(project_name),
        pipeline_configuration
    )

    if pipeline is None:
        click.echo('No pipeline configuration for pipeline ' + project_pipeline)
    
    stepsFinished = pipeline.Run(project_files)

    if run and not pipeline.run_command_errors:
        if target == "debug":
            click.echo(colored('debug', 'green') + " " + project_name)
            os.system("gdb ./"+project_name)
        else:
            click.echo(colored('run', 'green') + " " + project_name)
            os.system("./"+project_name)
        stepsFinished += 1

    click.echo('Finished ' + str(stepsFinished) + ' steps')


@builds.command('watch')
def watch():
    """Watch files for changes and run a build step on them if needed"""
    default_project = active_configuration.setdefault('default_project', 'default')
    projects = active_configuration.setdefault('projects', {'default':{}})
    project_settings = projects.get(default_project)
    project_files = project_settings.setdefault('files', [])
    watcher = Watcher(project_files, None)
    watcher.Start()


@builds.group('set')
def set():
    """Manages settings."""


@set.command('default_project')
@click.argument('project_name', type=str)
def set_default_project(project_name):
    """Sets the default project."""
    click.echo('Set %s as the default project' % project_name)

# @set.command('default_project')
# @click.argument('x', type=float)
# @click.argument('y', type=float)
# @click.option('ty', '--moored', flag_value='moored',
#              default=True,
#              help='Moored (anchored) mine. Default.')
# @click.option('ty', '--drifting', flag_value='drifting',
#              help='Drifting mine.')
# def set_default_project(x, y, ty):
#    """Sets a mine at a specific coordinate."""
#    click.echo('Set %s mine at %s,%s' % (ty, x, y))


if __name__ == '__main__':
    builds()
