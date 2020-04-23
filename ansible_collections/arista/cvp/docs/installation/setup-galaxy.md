# Collection installation via ansible-galaxy

## Install from Ansible Galaxy

__arista.cvp__ collection is available on [Ansible Galaxy](https://galaxy.ansible.com/arista/cvp) server and can be automatically installaded on your system.

### Latest version

```shell
$ ansible-galaxy collection install arista.cvp
```

### Install specific version

```shell
$ ansible-galaxy collection install arista.cvp:==1.0.2
```

### Install in specific directory

If you want to install collection in a specific directory part of your project, you can call `ansible-galaxy` and update your `ansible.cfg`

```shell
# Install collection under ${PWD/collections/}
$ ansible-galaxy collection install arista.cvp -p collections/

# Update ansible.cfg file
$ vim ansible.cfg
collections_paths = ${PWD}/collections:~/.ansible/collections:/usr/share/ansible/collections
```
