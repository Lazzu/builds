# Builds
A CLI project building tool.

I was fed up with current C++ building tools, so I created my own. I borrowed the interface from Git so it would be somewhat familiar for everyone to use.

Not production ready yet. You can test the tool with the example usage below.

## Example usage

```
$ builds add hello.cpp
+ hello.cpp
Added 1 file(s)
$ builds project rename hello
$ builds add-library memmanage -p libs
+ path libs
+ memmanage
$ builds build
compile hello.cpp
build hello
$ ./hello
Hello, world!
```

## Requirements

- Python 3.5 or newer

## Getting started

1. Clone the repo
2. `pip install -r requirements.txt`
3. `ln -s /path/to/builds.py /usr/local/bin/builds`
4. Try the example usage with a hello.cpp of your own

## Supported features

- Manage projects
- Manage C++ project files
- Build C++ projects
- Add include paths
- Add libraries and paths
- Add shared libraries and paths
- Modular support for multiple project types (i.e. other than C++)

## Upcoming features

- Watch project files and run specific build steps on them
- Python 3.4 support
- Manage project folder structure

## Possible future features

- Import make or cmake files
- Export make or cmake files
- Support for older versions of python

## List of commands

With a lack of better documentation, here are some commands:

- `builds.py build [--rebuild] [--verbose] [--jobs n] [--run] [--target release] [projectname]` build current or named project
- `builds.py project show` show active project name
- `builds.py project rename [-p projectname] newprojectname` rename a project or a current project with a new name
- `builds.py add filename` add a file
- `builds.py add --interactive` add files interactively
- `builds.py remove filename` remove a file
- `builds.py add-library libraryname [--path librarypath]` add a library and/or a library path
- `builds.py add-include includepath` add a include path
- `builds.py add-shared-library sharedlibrary` add a shared library
- `builds.py settings print` print the current settings as json to the stdout