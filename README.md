# Kelp plugins
This is a set of Hairball plugins that correspond to the Kelp curriculum.

## Requirements
You need the latest version of Hairball and Kurt. If you have pip, you can install Kurt using:

	pip install kurt

And Hairball:

	pip install hairball

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

0. If the remote repository has changed since you last pulled, you might get an error here. Here are the basic steps for merging, although it can get more difficult. First, pull the latest version.

	git pull

0. If you have any merge issues, figure those out. Otherwise, merge the two heads.

	git commit -m "Merged heads"

0. Then push again

	git push

## Running Plugins
Basically, you're going to run Hairball but tell it to use the Kelp plugins and use the Kurt octopi plugin so that it can read .oct files.

	hairball -k path/octopiplugin.py -d folder where sequenceViewer is -p sequenceViewer.Sequence path/test.sb

For example, if everything is inside your current directory:

	hairball -k octopiplugin.py -d . -p sequenceViewer.Sequence test.sb

If octopiplugin and sequenceViewer are inside of a directory called "plugins" and test.sb is in a directory called "testfiles":

	hairball -k plugins/octopiplugin.py -d plugins -p testfiles/sequenceViewer.Sequence test.sb

