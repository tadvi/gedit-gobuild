GEdit and Go
============

There are number of editors and IDEs for Go development. Liteide, Vim,
Emacs, GEdit just to name a few. Each developer has its own favourites.

Some like full featured IDE environments while others prefer speed over 
features.

My personal favourites at the moment: Vim and GEdit.

GEdit comes as part of many Linux distros. If you use Ubuntu it is part
of the OS. GEdit has some decent features like: syntax highlighting, split
windows, word wrapping, etc. Advanced features are left to be handled by
external plug-ins. 

I prefer project-less development. That means there are no formal project
files kept around. Project is preserved via directory structure.

Go has excellent support for project-less development. You do not need 
makefiles for most of the development, and concept of Go package helps too.

GEdit is a decent editor but I could not find any good plug-ins that would
allow me to perform Go build right from the editor. **"External Tools"** 
plug-in is useful. You can setup shortcut and get "go build" execute as
external tool. It is OK. When you click on errors displayed in the bottom 
pane of GEdit cursor jumps to extract error location.

When I just started Go programming **"External Tools"** plug-in worked 
for me for quite some time. But after awhile I started to wish that Go 
build would run similar to how Linters run for some of the scripting 
languages: run after file is saved. 

Because Go build usually takes only few seconds, plug-in could execute on save
and jump to error if there is any. 

GEdit plug-in is developed in Python. Depending on version of the Python you 
have on your Linux some small adjustment might be required and covered in 
"Known Issues" below.

Meet GoBuild for GEdit 3.x
--------------------------

GoBuild - Gedit 3 plug-in for Go (golang) develoment. 

GoBuild plug-in version 1.0 for GEdit. plug-in attaches to on_save event
in GEdit for Go language files only. It does nothing for other file types.

Runs "go build" but if current filename has "_test.go" in the name 
then runs "go test" on current file's directory. Waits for number of seconds 
and then timeouts if process takes way too long, so GEdit would no freeze.

Current build directory is determined based on current open file directory.

 * Plug-in designed for fast development on small to mid size projects.
 * Not designed for large Go projects because compilation will timeout if it 
takes too long.
 * Not designed for Go unit tests that take long time to run.

![screen1](gobuildscreen1.png)

Plug-in captures go build errors and shows them in the Gedit status bar.
It also jumps to the first error and highlights error line if error is in 
the current file.

![screen2](gobuildscreen2.png)

Shows last successful build.

![screen3](gobuildscreen3.png)

Shows "go test" failures.

Known issues 
------------

Has been tested on Ubuntu 13.04 and 13.10.

Ubuntu 13.10 requires small change in the gobuild.plugin.
Line with python should be changed to python3 like below:

Loader=python3

This is because Gedit seems to default on using python 3 instead of 
python 2.7 on newer versions of Linux.

Usage
-----

 * Simply drop files into ~/.local/share/gedit/plugins .
 * If this directory does not exist - create it.
 * Start GEdit
 * Open Edit-Preferences, then plug-ins and check "GoBuild after save" plug-in.
 
Idea
----

Plug-in idea is based on the fact that Go builds are fast for even decent size
projects. Because build is fast plug-in can run on every Save and still appear 
responsive.
Go development with this plug-in goes into tight iteration of save-edit-save-edit
cycle. 

If you work on Go projects with build times over 5 seconds this plug-in should be
modified to use keyboard shortcut (such as 'F5') instead of on_save action.

Ops, I forgot to mention...Go is **awesome**. But you probably already know that.


