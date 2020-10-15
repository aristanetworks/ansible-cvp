# Docker & Development environment

Two methods can be used get Ansible up and running quickly with all the requirements to leverage ansible-avd.
A Python Virtual Environment or Docker container.

The best way to use the development files, is to copy them to the root directory where you have your repositories cloned.
For example, see the file/folder structure below.

```shell
├── git_projects
│   ├── ansible-avd
│   ├── ansible-cvp
│   ├── ansible-avd-cloudvision-demo
│   ├── <your-own-test-folder>
│   ├── Makefile
...
```

## Step by step installation process

This process is similar to [ansible-avd collection](https://github.com/aristanetworks/ansible-avd). It means if you use AVD, this step is not required.

```shell
mkdir git_projects
cd git_projects
git clone https://github.com/aristanetworks/ansible-avd.git
git clone https://github.com/aristanetworks/ansible-cvp.git
git clone https://github.com/arista-netdevops-community/ansible-avd-cloudvision-demo.git
cp ansible-cvp/development/Makefile ./
make run
```

## One liner installation

[One liner script](https://github.com/arista-netdevops-community/avd-install/blob/master/install.sh) to setup a development environment. it does following actions:

- Create local folder for development
- Instantiate a local git repository (no remote)
- Clone AVD and CVP collections
- Deploy Makefile

```shell
$ sh -c "$(curl -fsSL https://get.avd.sh)"
```

## Build local environment

### Docker Container for Ansible Testing and Development

The docker container approach for development can be used to ensure that everybody is using the same development environment while still being flexible enough to use the repo you are making changes in. You can inspect the Dockerfile to see what packages have been installed.
The container will mount the current working directory, so you can work with your local files.

The ansible version is passed in with the docker build command using ***ANSIBLE*** variable.  If the ***ANSIBLE*** variable is not used the Dockerfile will by default set the ansible version to 2.9.2

Before you can use a container, you must install [__Docker CE__](https://www.docker.com/products/docker-desktop) and [__docker-compose__](https://docs.docker.com/compose/) on your workstation.

#### Development containers

- [Ansible shell](https://hub.docker.com/repository/docker/avdteam/base): provide a built-in container with all AVD and CVP requirements already installed.
- [MKDOCS](https://github.com/titom73/docker-mkdocs) for documentation update: Run MKDOCS in a container and expose port `8000` to test and validate markdown rendering for AVD site.

#### Container commands

In this folder you have a `Makefile` providing a list of commands to start a development environment:

- `run`: Start a shell within a container and local folder mounted in `/projects`
- `dev-start`: Start a stack of containers based on docker-compose: 1 container for ansible playbooks and 1 container for mkdocs
- `dev-stop`: Stop compose stack and remove containers.
- `dev-run`: Connect to ansible container to run your test playbooks.
- `dev-reload`: Run stop and start.

If you want to test a specific ansible version, you can refer to this [dedicated page](https://github.com/arista-netdevops-community/docker-avd-base/blob/master/docs/run-options.md) to start your own docker image. You can also use following make command: `make ANSIBLE_VERSION=2.9.3 run`

Since docker image is now automatically published on [__docker-hub__](https://hub.docker.com/repository/docker/avdteam/base), a dedicated repository is available on [__Arista Netdevops Community__](https://github.com/arista-netdevops-community/docker-avd-base).

```shell
# Start development stack
$ make dev-start
docker-compose -f ansible-cvp/development/docker-compose.yml up -d
Creating development_webdoc_1  ... done
Creating development_ansible_1 ... done

# List containers started with stack
$ docker-compose -f ansible-avd/development/docker-compose.yml ps
        Name                       Command               State           Ports
---------------------------------------------------------------------------------------
development_ansible_1   /bin/sh -c while true; do  ...   Up
development_webdoc_1    sh -c pip install -r ansib ...   Up      0.0.0.0:8000->8000/tcp

# Get a shell with ansible
$ make dev-run
docker-compose -f ansible-cvp/development/docker-compose.yml exec ansible zsh
Agent pid 52
➜  /projects

# Test MKDOCS access
$ curl -s http://127.0.0.1:8001 | head -n 10
<!doctype html>
<html lang="en" class="no-js">
  <head>

      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width,initial-scale=1">

# Stop development stack
$ make dev-stop
docker-compose -f ansible-cvp/development/docker-compose.yml kill &&\
        docker-compose -f ansible-cvp/development/docker-compose.yml rm -f
Killing development_ansible_1 ... done
Killing development_webdoc_1  ... done
Going to remove development_ansible_1, development_webdoc_1
Removing development_ansible_1 ... done
Removing development_webdoc_1  ... done
```
