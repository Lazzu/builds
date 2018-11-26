# Builds
A CLI project building tool.

I was fed up with current C++ building tools, so I created my own. I borrowed the interface from Git so it would be somewhat familiar for everyone to use.

Not production ready yet. You can test the tool with the example usage below.

## Example usage

```
$ python builds.py add hello.cpp
+ hello.cpp
Added 1 file(s)
$ python builds/builds.py add-library memmanage -p libs
+ path libs
+ memmanage
$ python builds.py build
compile hello.cpp
build hello
$ ./hello
Hello, world!
```

## Requirements

- Python 3.5

## Supported features

- Manage projects
- Manage C++ project files
- Build C++ projects
- Add include paths
- Add libraries and paths
- Add shared libraries and paths
- Modular support for multiple project types (i.e. other than C++)

## Roadmap

- Watch project files and run build steps on them
- Python 3.4 support (or maybe even earlier)
- Manage project folder structure

## Possible future features

- Import make or cmake files
- Export make or cmake files
