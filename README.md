# Kelp plugins
This is a set of Hairball plugins that correspond to the Kelp curriculum.

## Installation

If you are checking out the source, the simplest way to install everything is
via `python setup.py develop`. This will install all the dependencies of the
project. You may need to prefix that line with `sudo` if you are installing at
the system-level.

Once installed in development mode, the command `kelp` can be run from any
directory (regardless of where your source directory is located).


## Using Git
You can also use the Github application, but if you'd rather use terminal, here are some useful commands:

0. Check out the source

	git clone git@github.com:charlottehill/KelpPlugin.git

0. Commit changes - first test your code using flake8. To install flake 8:

	pip install flake8

To run flake8 (from inside your KelpPlugin directory):

	flake8 .

0. Review what files you modified. (commands are from inside your KelpPlugin directory)

	git status

0. If you want to review the changes you made in detail:

	git diff

0. Add the files you changed to the list of stuff you'll later commit:

	git add filename

0. Run git status again to make sure that you added what you wanted to add and nothing extra. You can also use this to look over what you're about to commit:

	git diff --staged

0. Add a commit message so other people can get a idea of what you did without looking through the code.

	git commit -m "replace with your message"

0. Push the code.

        git push
        # The first time you push run
        # git push -u origin master

0. If the remote repository has changed since you last pulled, you might get an
error here. Here are the basic steps for merging, although it can get more
difficult. First, pull the latest version.

	git pull

0. If you have any merge issues, figure those out. Otherwise, merge the two heads.

	git commit -m "Merged heads"

0. Then push again

	git push

## Running Plugins Offline

Basically, you're going to run Hairball but tell it to use the Kelp plugins and
use the Kurt octopi plugin so that it can read .oct files.

Offline.py calls Hairball and figures out which plugins you need for your
lesson and project.

Lesson options:

* sequential
* events
* initialization
* broadcast
* costumes
* scenes (just runs the same stuff as costumes)

Project options:

* (none yet)

If you just want to use the default lesson with no extra project plugins, leave
off the `projectconcept` argument.

For now, you have to have octopi.py in the same directory as the plugins, but
we can change that if you'd like. Assuming you have installed the kelp package
as per the above instruction run:

    kelp filename.oct lessonname [projectconcept]

For example, if you want to run the `sequential` lesson plugin on `project.oct`
you would run:

    kelp project.oct sequential

If the file you want to analyze, `test.oct` is in a directory named
`testfiles` you will want to run:

    kelp testfiles/test.oct sequential
