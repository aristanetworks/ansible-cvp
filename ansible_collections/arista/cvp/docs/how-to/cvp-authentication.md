<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# CloudVision Authentication

CloudVision supports 2 different types of authentication depending on what kind of instance you are targeting:

- [On-premise CloudVision](https://www.arista.com/en/products/eos/eos-cloudvision) instance:
  - username and password authentication
  - user token authentication
- [Cloudvision-as-a-Service](https://www.youtube.com/embed/Sobh9XVZhcw?rel=0&wmode=transparent): User token authentication

## On-premise CloudVision authentication

This authentication mechanism is default approach leveraged in the collection and can be configured as below in your variables. It is based on a pure **username/password** model

```yaml
# Default Ansible variables for authentication
ansible_host: < IP address or hostname to target >
ansible_user: < Username to connect to CVP instance >
ansible_password: < Password to use to connect to CVP instance >
ansible_connection: httpapi
ansible_network_os: eos

# Optional Ansible become configuration.
ansible_become: true
ansible_become_method: enable

# HTTPAPI plugin configuration
ansible_httpapi_port: '{{ansible_port}}'
ansible_httpapi_host: '{{ ansible_host }}'
ansible_httpapi_use_ssl: true
ansible_httpapi_validate_certs: false
```

Alternatively **user token** can be used just as with CVaaS. See [How to generate service account tokens](#how-to-generate-service-account-tokens) for the token generation steps.

```yaml
# Default Ansible variables for authentication
ansible_host: < IP address or hostname to target >
# The username "svc_account" will change authentication process to use "api_token" towards CVP.
# The username does not need to match anything defined on CVP, since the token
# contains all the required information.
ansible_user: svc_account
ansible_password: < User token to use to connect to CVP instance >
ansible_connection: httpapi
ansible_network_os: eos
```

!!! note
    Depending on the ansible version, vault encrypted variables may not be supported because of https://github.com/ansible/ansible/issues/75503. ansible-cvp code will check if the provided password (and password only) is malformed and inform the user by raising an exception.
    Either upgrade ansible-core to a version that has the fix: https://github.com/ansible/ansible/pull/78236 or use ansible vault file instead: https://docs.ansible.com/ansible/latest/user_guide/vault.html#encrypting-files-with-ansible-vault

### Example reading from a file

```yaml
ansible_user: svc_account
ansible_password: "{{ lookup('file', '/path/to/onprem.token')}}"
```

### Example reading from an environment variable

```shell
export ONPREM_TOKEN=`cat /path/to/onprem.token`
```

```yaml
ansible_user: svc_account
ansible_password: "{{ lookup('env', 'ONPREM_TOKEN')}}"
```

> NOTE Both `ansible_ssh_pass` and `ansible_password` can be used to specify the password or the token.

### Example using vault

This example is based on the inventory below:

```yaml
---
all:
  children:
    CVP_group:
      hosts:
        CloudVision:
          ansible_httpapi_host: 192.0.2.79
          ansible_host: 192.0.2.79
          ansible_user: svc_account
          ansible_password: "{{vault_token}}"
          ansible_connection: httpapi
          ansible_httpapi_use_ssl: True
          ansible_httpapi_validate_certs: False
          ansible_network_os: eos
          ansible_httpapi_port: 443
          ansible_python_interpreter: $(which python3)
```

1. Create a subdirectory for your CVP group in `group_vars` folder: `mkdir -p ./group_vars/CVP_group/`

2. Save the token generated from the CV/CVaaS UI into a file named `vault` inside `./group_vars/CVP_group/` following the format below:

   ```yaml
   vault_token: <token>
   ```

3. Encrypt the file using `ansible-vault encrypt vault`

4. Refer to the token in your host_vars or inventory file using `ansible_password: "{{ vault_token }}"`

5. Run the playbook with `ansible-playbook example.yaml --ask-vault-pass` or instead of `--ask-vault-pass`
provide the password with any other methods as described in the [ansible vault documentation](https://docs.ansible.com/ansible/latest/user_guide/vault.html#using-encrypted-variables-and-files).

> NOTE Encrypting individual variables using vault may not be supported - cf notes at the end of ## On-premise CloudVision authentication section

## CloudVision as a Service authentication

This authentication method uses a **user token** that has to be generated on the CVaaS UI. See [How to generate service account tokens](#how-to-generate-service-account-tokens) for the token generation steps. Then, ansible can be instructed to use the token instead of username and password authentication method.

```yaml
# Default Ansible variables for authentication
ansible_host: < IP address or hostname to target >
ansible_user: cvaas # Shall not be changed. ansible will switch to cvaas mode
ansible_password: < User token to use to connect to CVP instance >
ansible_connection: httpapi
ansible_network_os: eos

# Optional Ansible become configuration.
ansible_become: true
ansible_become_method: enable

# HTTPAPI plugin configuration
ansible_httpapi_port: '{{ansible_port}}'
ansible_httpapi_host: '{{ ansible_host }}'
ansible_httpapi_use_ssl: true
ansible_httpapi_validate_certs: false
```

### Example reading from a file

```yaml
ansible_user: cvaas
ansible_password: "{{ lookup('file', '/path/to/cvaas.token')}}"
```

### Example reading from an environment variable

export CVAAS_TOKEN=`cat /path/to/cvaas.token`

```yaml
ansible_user: cvaas
ansible_password: "{{ lookup('env', 'CVAAS_TOKEN')}}"
```

> NOTE Both `ansible_ssh_pass` and `ansible_password` can be used to specify the token.

### Example using vault

1. Save the token generated from the CV/CVaaS UI and encrypt it using `ansible-vault encrypt cvaas.token`
2. Run the playbook with `ansible-playbook example.yaml --ask-vault-pass`

## How to validate SSL certificate

### Validate SSL cert signed by public CA

Starting version `2.1.1`, `arista.cvp` collection supports mechanism to validate SSL certificate. To configure ansible to validate SSL certificate provided by your CV instance, you must update httpapi information like this:

```yaml
# HTTPAPI plugin configuration
ansible_httpapi_port: '{{ansible_port}}'
ansible_httpapi_host: '{{ ansible_host }}'
ansible_httpapi_use_ssl: true
ansible_httpapi_validate_certs: true
```

### Validate SSL cert signed by custom CA

> This mechanism works also with self-signed certificate

Update httpapi as shown below:

```yaml
# HTTPAPI plugin configuration
ansible_httpapi_port: '{{ansible_port}}'
ansible_httpapi_host: '{{ ansible_host }}'
ansible_httpapi_use_ssl: true
ansible_httpapi_validate_certs: true
```

Since `HTTPAPI` plugin is based on Python `Requests` library, you need to use `Requests` method to [support custom `CA_BUNDLE`](https://requests.readthedocs.io/en/master/user/advanced/#ssl-cert-verification)

```shell
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

> Please note `export` is only working in your active shell unless you configure your `.bashrc` or `.zshrc` with this configuration.

For information, `Requests` embeds its bundles in the following paths, for reference:

```shell
/usr/local/lib/python2.7/site-packages/requests/cacert.pem
/usr/lib/python3/dist-packages/requests/cacert.pem
```

### Validate SSL using CloudVision self-signed certificate

Update httpapi as shown below:

```yaml
# HTTPAPI plugin configuration
ansible_httpapi_port: '{{ansible_port}}'
ansible_httpapi_host: '{{ ansible_host }}'
ansible_httpapi_use_ssl: true
ansible_httpapi_validate_certs: true
```

And then, import your CA or server CRT file into database of your CA for Python using [certifi](https://github.com/certifi/python-certifi) which is [recommended libs from Requests](https://requests.readthedocs.io/en/master/community/recommended/#certifi-ca-bundle)

```shell
# Get CVP SSL Cert (If not already provided by your CV admin)
$ true | openssl s_client -connect <YOUR-CV-IP>:443 2>/dev/null | openssl x509 > cvp.crt

# Update Python DB for known CA
$ cat cvp.crt >> `python -m certifi`
```

> Note it is per virtual environment configuration.

### Invalid SSL certification

If identity cannot be validated by ansible, playbook stops with following error message:

```shell
$ ansible-playbook playbooks/extract-facts.yml

PLAY [CV Facts] ***************************************************************

TASK [Gather CVP facts from cv_server] ****************************************
Monday 05 October 2020  21:09:22 +0200 (0:00:00.063)       0:00:00.063 ********
Monday 05 October 2020  21:09:22 +0200 (0:00:00.063)       0:00:00.063 ********
fatal: [cv_server]: FAILED! => changed=false
  msg: |2-

    x.x.x.x: HTTPSConnectionPool(host='x.x.x.x', port=443): Max retries \
        exceeded with url: /web/login/authenticate.do \
        (Caused by SSLError(SSLError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] \
        certificate verify failed (_ssl.c:852)'),))
```

## Configure connection timeout

When used in large environment, API calls can take more than 30 seconds to run. It can be configured in ansible by leveraging either `ansible.cfg` file or variables.

### Ansible configuration file

Edit `ansible.cfg` file and add the following

```ini
[persistent_conenction]
connection_timeout = 120
command_timeout = 120
```

> If also configured in variables, it will be overwrite.

### Inventory variables

Add in either inventory file, group_vars or host_vars following lines:

```yaml
---
ansible_connect_timeout: 30
ansible_command_timeout: 90
```

## How to generate service account tokens

Service accounts can be created from the Settings page where a service token can be generated as seen below:

![serviceaccount1](../_media/serviceaccount1.png)
![serviceaccount2](../_media/serviceaccount2.png)
![serviceaccount3](../_media/serviceaccount3.png)

> NOTE The name of the service account must match a username configured to be authorized on EOS, otherwise device interactive API calls might fail due to authorization denial.

The token should be copied and saved to a file or as an environment variable that can be referred to in the host vars.
