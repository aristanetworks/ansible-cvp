#!/bin/bash
#
# Purpose: AVD Installation script
# Author: Arista Ansible Team
# --------------------------------------

# Update PATH to match ATD Jumphost setting
export PATH=$PATH:$HOME/.local/bin/
export PYTHONPATH=$PYTHONPATH:$HOME/.local/lib/python3.8/site-packages/

# Bin path
_CURL=$(which curl)
_GIT=$(which git)

# Local Installation Path
_INSTALLATION_PATH="arista-ansible"
_PERSIST="/home/coder/project/persist"
_ROOT_INSTALLATION_DIR="${_PERSIST}/${_INSTALLATION_PATH}"

# List of Arista Repositories
_REPO_CVP="https://github.com/aristanetworks/ansible-cvp.git"
_PR_BRANCH="$1"

# Path for local repositories
_LOCAL_CVP="${_ROOT_INSTALLATION_DIR}/ansible-cvp"
_LOCAL_EXAMPLE_PLAYBOOKS="${_PERSIST}/PR_testing"

# Print post-installation instructions
info_installation_done() {
    echo ""
    echo "Installation done."
    echo ""
}


##############################################
# Main content for script
##############################################

echo "Arista Ansible AVD installation is starting"

# Test if git is installed
if hash git 2>/dev/null; then
    echo "  * git has been found here: " $(which git)
else
    echo "  ! git is not installed, installation aborted"
    exit 1
fi

echo "  * Deployed AVD environment"
if [ ! -d "${_ROOT_INSTALLATION_DIR}" ]; then
    echo "  * creating local ansible-cvp installation folder: ${_ROOT_INSTALLATION_DIR}"
    mkdir -p ${_ROOT_INSTALLATION_DIR}
    echo "  * cloning ansible-cvp collections to ${_LOCAL_CVP}"
    ${_GIT} clone ${_REPO_CVP} ${_LOCAL_CVP} > /dev/null 2>&1

    cd ${_LOCAL_CVP}
    echo "input pr branch is ${_PR_BRANCH}"
    ${_GIT} fetch origin pull/${_PR_BRANCH}/head && ${_GIT} checkout FETCH_HEAD > /dev/null 2>&1
    cd ${_PERSIST}
    echo "copying ansible workspace"
    mkdir -p ${_LOCAL_EXAMPLE_PLAYBOOKS}
    cp ${_LOCAL_CVP}/tests/PR_testing/ansible.cfg ${_LOCAL_EXAMPLE_PLAYBOOKS}
    cp ${_LOCAL_CVP}/tests/PR_testing/inventory.yaml ${_LOCAL_EXAMPLE_PLAYBOOKS}

    echo "copying example playbooks from ${_REPO_CVP} to /persist"
    cp -r ${_LOCAL_CVP}/ansible_collections/arista/cvp/examples/* ${_LOCAL_EXAMPLE_PLAYBOOKS}

    echo "ansible collection install"
    cd ${_LOCAL_EXAMPLE_PLAYBOOKS}
    ansible-galaxy collection install community.general
    ansible-galaxy collection install ansible.netcommon
    ansible-galaxy collection install arista.eos

    info_installation_done
else
    echo "  ! local installation folder already exists - ${_ROOT_INSTALLATION_DIR}"

    exit 1
fi
