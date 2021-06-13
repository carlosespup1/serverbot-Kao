# Server bot for Kao Discord Channel

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

We use Python to all the development, feel free to send your suggestions or pull request, just have clear the next advices.

- Make sure everything is working on your code. ✔︎
- Add comment in your code. 💻
- That all. 😎
## Features
- Here we're gonna put all features.


## Tech

We're gonna use the next tech:

- Discord dev. API
- Python
- Python libraries as Request/Flask.

## Installation

You are gonna find a requeriments.txt in the repo files. 

Create and activate Virtual Enviroment
```sh
cd <project file>
python3 -m venv .env
source .env/bin/activate
pip -r requirements.txt
```

Then check if everything is ok

```sh
pip freeze
```
and make sure all the package were installed.

## Contributions

If is your first contribution follow since step 1, else 
### 1. Clone the repository

Open a terminal and run the following command

```sh
git clone "https://github.com/carlosespup1/serverbot-Kao.git"
```

### 2. Create a branch

We are using [GitFlow](https://cleventy.com/que-es-git-flow-y-como-funciona/), so create a new branch to code a new feature from **develop** branch.

```sh
# from develop branch
git checkout -b >new-branch-name>
```

### 3. Add and commit your changes
Make your changes, and commit only the necessary files for this feature.

```sh
# for example: app.py is updated
git add app.py
git commit -m "ADD new meme command"
```

### 4. Push changes to Github
Push your changes using 

```sh
git push origin <branch-name>
```

### 5. Submit your changes to review

Click to *Compare & pull request* button

![cap1](/caps/compare.JPG)

Then, select your branch and the destination branch. **Make sure that *develop* is the destination**.

Fill the gaps, and add reviewers (@gcmurillo, @kaolof, @carlosespup1)

![cap2](/caps/pr.JPG)

If the changes are approved, a reviewer will close the PR.

![cap3](/caps/close.JPG)
