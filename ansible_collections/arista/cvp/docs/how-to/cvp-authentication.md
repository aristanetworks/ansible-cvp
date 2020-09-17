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
