# Contribute to Arista ansible-cvp collection

Please take a moment to review this document in order to make the contribution
process easy and effective for everyone involved.

Following these guidelines helps to communicate that you respect the time of
the developers managing and developing this open source project. In return,
they should reciprocate that respect in addressing your issue or assessing
patches and features.

## Reporting Bugs

- First, ensure that you've installed the [latest stable version](https://github.com/aristanetworks/ansible-cvp/releases)
of **ansible-cvp**. If you're running an older version, it's possible that the bug has
already been fixed.

- Next, check the GitHub [issues list](https://github.com/aristanetworks/ansible-cvp/issues)
to see if the bug you've found has already been reported. If you think you may
be experiencing a reported issue that hasn't already been resolved, please
click "add a reaction" in the top right corner of the issue and add a thumbs
up (+1). You might also want to add a comment describing how it's affecting your
installation. This will allow us to prioritize bugs based on how many users are
affected.

- If you haven't found an existing issue that describes your suspected bug, **Do not** file an issue until you
have received confirmation that it is in fact a bug. Invalid issues are very
distracting and slow the pace at which **ansible-cvp** is developed.

- When submitting an issue, please be as descriptive as possible. Be sure to
include:

  - The environment in which **ansible-cvp** is running
  - The exact steps that can be taken to reproduce the issue (if applicable)
  - Any error messages generated
  - Screenshots (if applicable)

- Please avoid prepending any sort of tag (e.g. "[Bug]") to the issue title.
The issue will be reviewed by a moderator after submission and the appropriate
labels will be applied for categorization.

- Keep in mind that we prioritize bugs based on their severity and how much
work is required to resolve them. It may take some time for someone to address
your issue.

## Feature Requests

- First, check the GitHub [issues list](https://github.com/aristanetworks/ansible-cvp/issues)
to see if the feature you're requesting is already listed. (Be sure to search
closed issues as well, since some feature requests have been rejected.) If the
feature you'd like to see has already been requested and is open, click "add a
reaction" in the top right corner of the issue and add a thumbs up (+1). This
ensures that the issue has a better chance of receiving attention. Also feel
free to add a comment with any additional justification for the feature.
(However, note that comments with no substance other than a "+1" will be
deleted. Please use GitHub's reactions feature to indicate your support.)

- Before filing a new feature request, consider raising your idea on the
mailing list first. Feedback you receive there will help validate and shape the
proposed feature before filing a formal issue.

- Good feature requests are very narrowly defined. Be sure to thoroughly
describe the functionality and data model(s) being proposed. The more effort
you put into writing a feature request, the better its chance is of being
implemented. Overly broad feature requests will be closed.

- When submitting a feature request on GitHub, be sure to include the
following:

  - A detailed description of the proposed functionality
  - A use case for the feature; who would use it and what value it would add
      to **ansible-cvp**
  - A rough description of changes necessary
  - Any third-party libraries or other resources which would be involved

- Please avoid prepending any sort of tag (e.g. "[Feature]") to the issue
title. The issue will be reviewed by a moderator after submission and the
appropriate labels will be applied for categorization.

## Using the issue tracker

The issue tracker is the preferred channel for [**bug reports**](#reporting-bugs),
[**features requests**](#feature-requests) and [**submitting pull
requests**](#pull-requests), but please respect the following restrictions:

- Please **do not** use the issue tracker for personal support requests.

- Please **do not** derail or troll issues. Keep the discussion on topic and
  respect the opinions of others.

## Branches

### Current active branches

- Current development branch: **`devel`**
- Stable branch: `releases/v1.1.x`

## Pull requests

- Be sure to open an issue **before** starting work on a pull request, and
discuss your idea with the **ansible-cvp** maintainers before beginning work. This will
help prevent wasting time on something that might we might not be able to
implement. When suggesting a new feature, also make sure it won't conflict with
any work that's already in progress.

- Any pull request which does *not* relate to an accepted issue will be closed.

- All major new functionality must include relevant tests where applicable.

- When submitting a pull request, please be sure to work off of the `releases/grant-v1.x`
branch, rather than `master`. The `releases/grant-v1.x` branch is used for ongoing
development, while `master` is used for tagging new stable releases.

- All code submissions should meet the following criteria (CI will enforce
these checks):

  - Python syntax is valid
  - All tests pass when run with `make sanity`
  - PEP 8 compliance is enforced, with the exception that lines may be
      greater than 80 characters in length

Adhering to the following this process is the best way to get your work
merged:

1. [Fork](http://help.github.com/fork-a-repo/) the repo, clone your fork,
   and configure the remotes:

   ```bash
   # Clone your fork of the repo into the current directory
   git clone https://github.com/<your-username>/ansible-cvp

   # Navigate to the newly cloned directory
   cd ansible-cvp

   # Assign the original repo to a remote called "upstream"
   git remote add upstream https://github.com/aristanetworks/ansible-cvp.git
   ```

2. If you cloned a while ago, get the latest changes from upstream:

   ```bash
   git checkout <dev-branch>
   git pull upstream <dev-branch>
   ```

   > Please refer to [branches section](#branches) to get current branch to use as `<dev-branch>`

3. Create a new topic branch (off the main project development branch) to
   contain your feature, change, or fix:

   ```bash
   git checkout -b <topic-branch-name>
   ```

4. Commit your changes in logical chunks. Please adhere to these [git commit
   message guidelines](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)
   or your code is unlikely be merged into the main project. Use Git's
   [interactive rebase](https://help.github.com/articles/interactive-rebase)
   feature to tidy up your commits before making them public.

5. Locally merge (or rebase) the upstream development branch into your topic branch:

   ```bash
   git pull [--rebase] upstream <dev-branch>
   ```

6. Push your topic branch up to your fork:

   ```bash
   git push origin <topic-branch-name>
   ```

7. [Open a Pull Request](https://github.com/aristanetworks/ansible-cvp/pulls)
    with a clear title and description.
