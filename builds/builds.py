import click
import json
import os
import types

default_builds_configuration = {
    'targets': {
        'debug' : {
            'debug' : True
        },
        'release' : {
            'debug' : False
        }
    },
    'projects' : {
        'default' : {

        }
    }
}

builds_configuration = {}
active_configuration = {}

def save_configuration(config):
    with open('builds.json', 'w', encoding='utf-8') as file:
        json.dump(config, file)

if os.path.exists('builds.json'):
    with open('builds.json', encoding='utf-8') as file:
        builds_configuration = json.loads(file)

active_configuration = {**default_builds_configuration, **builds_configuration}

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
    click.echo(json.dumps(active_configuration, sort_keys=True, indent=2))

@builds.command('add')
@click.argument('file')
def add(file):
    """Add a file to the build."""
    click.echo('Adding file ' + file + ' to the build')
    default_project = active_configuration.setdefault('default_project', 'default')
    projects = active_configuration.setdefault('projects', {'default':{}})
    project = projects.get(default_project)
    files = project.setdefault('files', [])
    files.append(file)
    print_settings()


@builds.command('build')
@click.argument('project', default=active_configuration.get('default_project', 'default'))
@click.option('target', '--target', default='debug', help='Select target to build (debug/release)')
def build(project, target):
    """Build the project.
    This builds the project with the current settings in builds.json file.
    """
    click.echo("build project " + project + " with " + target + " target")


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