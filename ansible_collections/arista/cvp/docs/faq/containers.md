# Ansible Execution Environment

## Ansible EE and builder overview

An automation execution environment is a container image used to execute Ansible playbooks and roles. It provides a defined, consistent, portable environment for executing automation.

Ansible Builder was developed to automate the process of building Execution Environments.  It does this by using the dependency information defined in various Ansible Content Collections, as well as by the user. Ansible Builder will produce a directory that acts as the build context for the container image build, which will contain the Containerfile, along with any other files that need to be added to the image.

You can read more on [Ansible website](https://www.ansible.com/blog/introduction-to-ansible-builder) or also [here](https://docs.ansible.com/automation-controller/latest/html/userguide/execution_environments.html)

## Ansible Execution Environment for arista.cvp

Repository provides 2 different Execution environment definition:

- Execution Environment to execute stable version of CV Collection
- Execution Environment to execute development version of CV collection

!!! info
    Even if CV collection provides such image, Execution Environments should be defined per ansible project and CV images only for testing. Indeed, our images are built with only our own requirements that can differ from your global project.

### Build your runner for stable version

By default, `ansible-builder` uses podman to build image, if you want to use docker instead, add `--container-runtime docker` to your CLI

```bash
# clone repository
git clone https://github.com/aristanetworks/ansible-cvp.git

# Move to root of the repo
cd ansible-cvp

# Build image
$ ansible-builder build --tag <your-image-tag> -f ansible_collections/arista/cvp/meta/execution-environment.yml
Running command:
  podman build -f context/Containerfile -t inetsix/ansible-ee-avd:devel context
Complete! The build context can be found at: /Users/tgrimonet/Projects/avd-stack/ansible-cvp/context

# Validate collection is installed
## PODMAN method
podman container run -it --rm inetsix/ansible-ee-avd:pr ansible-galaxy collection list

## Docker method
docker run -it --rm inetsix/ansible-ee-avd:pr ansible-galaxy collection list

# /usr/share/ansible/collections/ansible_collections
Collection        Version
----------------- -------
ansible.netcommon 2.5.0
ansible.utils     2.4.3
arista.eos        4.0.0
community.general 4.3.0

# /home/runner/.ansible/collections/ansible_collections
Collection Version
---------- -------
arista.cvp 3.2.0

# Execute your playbook (not covered here)
...
```

This image is based on the [latest ansible image version](https://quay.io/repository/ansible/ansible-runner?tag=latest&tab=tags). You can change it to use a specific version with: `--build-arg EE_BASE_IMAGE=quay.io/ansible/ansible-runner:latest`

!!! info
    You can use this image with AWX to execute code using Ansible Execution Environment

### Build image for testing a PR

By default, `ansible-builder` use podman to build image, if you want to use docker instead, add `--container-runtime docker` to your CLI

```bash
# clone repository
git clone https://github.com/aristanetworks/ansible-cvp.git

# Move to root of the repo
cd ansible-cvp

# Build image
$ ansible-builder build --tag <your-image-tag> -f execution-environment.yml -c .
Running command:
  podman build -f context/Containerfile -t inetsix/ansible-ee-avd:devel context
Complete! The build context can be found at: /Users/tgrimonet/Projects/avd-stack/ansible-cvp/context

# Validate collection is installed
## PODMAN method
podman container run -it --rm inetsix/ansible-ee-avd:pr ansible-galaxy collection list

## Docker method
docker run -it --rm inetsix/ansible-ee-avd:pr ansible-galaxy collection list

# /usr/share/ansible/collections/ansible_collections
Collection        Version
----------------- -------
ansible.netcommon 2.5.0
ansible.utils     2.4.3
arista.cvp        0.0.0
arista.eos        4.0.0
community.general 4.3.0

# Execute your testing (not covered here)
...
```

This image is based on the [latest ansible image version](https://quay.io/repository/ansible/ansible-runner?tag=latest&tab=tags). You can change it to use a specific version with: `--build-arg EE_BASE_IMAGE=quay.io/ansible/ansible-runner:latest`.

This build will copy local version of your collection to the container to `/usr/share/ansible/collections/ansible_collections`

## Resources

- [Ansible builder](https://ansible-builder.readthedocs.io/en/stable/) documentation
- [Ansible runner](https://ansible-runner.readthedocs.io/en/stable/) documentation
- Ansible [introduction to builder and runner](https://www.ansible.com/blog/introduction-to-ansible-builder)
- Network To Code [introduction to builder and runner](https://blog.networktocode.com/post/ansible-builder-runner-ee/)
