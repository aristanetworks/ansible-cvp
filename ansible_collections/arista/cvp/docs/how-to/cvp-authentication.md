# Cloudvision Authentication

Cloudvision supports 2 different types of authentication depending on what kind of instance you are targeting:

- [On-premise Cloudvision](https://www.arista.com/en/products/eos/eos-cloudvision) instance: username and password authentication
- [Cloudvision-as-a-Service](https://www.youtube.com/embed/Sobh9XVZhcw?rel=0&wmode=transparent): User token authentication

## On-premise Cloudvision authentication

This authentication mechanism is default approach leveraged in the collection and can be configured as below in your variables. It is based on a pure __username/password__ model

```yaml
# Default Ansible variables for authentication
ansible_host: < IP address or hostname to target >
ansible_user: < Username to connect to CVP instance >
ansible_ssh_pass: < Password to use to connect to CVP instance >
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

## Cloudvision as a Service authentication

This authentication method leverage a __user token__ to first get from your CVaaS instance. Then, instruct ansible to use token instead of username and password authentication

```yaml
# Default Ansible variables for authentication
ansible_host: < IP address or hostname to target >
ansible_user: cvaas # Shall not be changed. ansible will switch to cvaas mode
ansible_ssh_pass: < User token to use to connect to CVP instance >
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

### Validate SSL cert signed by unknown CA

> This mechanism works also with self-signed certificate

Update httpapi as shown below:

```yaml
# HTTPAPI plugin configuration
ansible_httpapi_port: '{{ansible_port}}'
ansible_httpapi_host: '{{ ansible_host }}'
ansible_httpapi_use_ssl: true
ansible_httpapi_validate_certs: true
```

And then, import your CA or server CRT file into database of your CA for Python

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
