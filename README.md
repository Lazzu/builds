# Builds
A CLI project building tool.

I was fed up with current C++ building tools, so I created my own. I borrowed the interface from GIT so it would be somewhat familiar for everyone to use.

Not production ready.

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
