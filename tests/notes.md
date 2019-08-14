# Ansible module notes

## cv_containers module

### Add container to CVP

__Information:__

A playbook exists for example and test purpose: [playbook.container.add.yaml](playbook.container.add.yaml)

__Code validation:__

```shell
(.venv) tests|master⚡ ⇒ ash ../.ci/check_container.sh                                     CVP Server: 10.73.1.139
Authenticate user: tom
{"sessionId":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NjU4NjI5NzUsImlhdCI6MTU2NTc3NjU3NTkwMjk5NjUwMSwiaXNzIjoiYWFhIiwianRpIjoidG9tIiwibmJmIjoxNTY1Nzc2NTc1LCJzdWIiOiJDdnAgYXV0aGVudGljYXRpb24ifQ.oABbacADoom1h0nIuh4rLr2G7eTtJMHyGgnwxDtWq
...
-----------------
Query CVP server: ansible_cvp
-----------------
[]

-->FAILURE - container does not exist on CVP

(.venv) tests|master⚡ ⇒ aansible-playbook playbook.container.add.yaml

PLAY [Test cv_container] ********

TASK [Create a container on CVP.] ********
changed: [cvp_server]

PLAY RECAP ********
cvp_server                 : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

(.venv) tests|master⚡ ⇒ sh ../.ci/check_container.sh
CVP Server: 10.73.1.139
Authenticate user: tom
{"sessionId":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NjU4NjI5OTAsImlhdCI6MTU2NTc3NjU5MDA0NDg4NTk1NiwiaXNzIjoiYWFhIiwianRpIjoidG9tIiwibmJmIjoxNTY1Nzc2NTkwLCJzdWIiOiJDdnAgYXV0aGVudGljYXRpb24ifQ.IPRXvhcUM9IwPAiym6L1EfUB59UxlNdOP2rO_Hx61Pc","user":{"userId":"tom",...
-----------------
Query CVP server: ansible_cvp
-----------------
[{"Key":"container_11_77801813261403","Name":"ansible_container","CreatedBy":"tom","CreatedOn":1565776588295,"Mode":"expand"}]

-->OK - container exists on CVP
```



### Delete container from CVP

__Information:__

A playbook exists for example and test purpose: [playbook.container.delete.yaml](playbook.container.delete.yaml)

__Code validation:__

```shell
(.venv) tests|master⚡ ⇒ sh ../.ci/check_container.sh
CVP Server: 10.73.1.139
Authenticate user: tom
{"sessionId":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NjU4NjI5OTAsImlhdCI6MTU2NTc3NjU5MDA0NDg4NTk1NiwiaXNzIjoiYWFhIiwianRpIjoidG9tIiwibmJmIjoxNTY1Nzc2NTkwLCJzdWIiOiJDdnAgYXV0aGVudGljYXRpb24ifQ.IPRXvhcUM9IwPAiym6L1EfUB59UxlNdOP2rO_Hx61Pc","user":{"userId":"tom",...
-----------------
Query CVP server: ansible_cvp
-----------------
[{"Key":"container_11_77801813261403","Name":"ansible_container","CreatedBy":"tom","CreatedOn":1565776588295,"Mode":"expand"}]

-->OK - container exists on CVP

(.venv) tests|master⚡ ⇒ ansible-playbook playbook.container.delete.yaml

PLAY [Test cv_container] ********

TASK [Delete a container on CVP.] ********
changed: [cvp_server]

PLAY RECAP ********
cvp_server                 : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0


(.venv) tests|master⚡ ⇒ sh ../.ci/check_container.sh
CVP Server: 10.73.1.139
Authenticate user: tom
{"sessionId":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NjU4NjMwMDAsImlhdCI6MTU2NTc3NjYwMDMwMDk2MTMyNSwiaXNzIjoiYWFhIiwianRpIjoidG9tIiwibmJmIjoxNTY1Nzc2NjAwLCJzdWIiOiJDdnAgYXV0aGVudGljYXRpb24ifQ.6MpBxCX_QtJhs1zw3RyBpT8bIKhw-p_IzRUhADMEaZs","user":{"userId":"tom",...
-----------------
Query CVP server: ansible_cvp
-----------------
[]

-->FAILURE - container does not exist on CVP
```