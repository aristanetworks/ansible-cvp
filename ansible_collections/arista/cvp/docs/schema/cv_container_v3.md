# Schema for cv_container_v3

| Variable | Type | Required | Default | Choices | Description |
| -------- | ---- | -------- | ------- | ------------------ | ----------- |
| apply_mode | str | No | loose | loose<br>strict | Set how configlets are attached/detached to containers. If set to strict, all configlets not listed in your vars will be detached. |
| state | str | No | present | present<br>absent | Set if Ansible should build or remove devices on CloudVision |
| topology | dict | Yes |  |  | YAML dictionary to describe intended containers |
| &nbsp;&nbsp;&nbsp;&nbsp;parentContainerName | str | Yes |  |  | Name of the parent container |
| &nbsp;&nbsp;&nbsp;&nbsp;configlets | List | No |  |  | List of configlets |
| &nbsp;&nbsp;&nbsp;&nbsp;imageBundle | str | No |  |  | The name of the image bundle to be associated with the container |
