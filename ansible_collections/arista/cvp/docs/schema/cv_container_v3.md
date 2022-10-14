# Schema for cv_container_v3

| Variable | Type | Required | Default | Choices | Description |
| -------- | ---- | -------- | ------- | ------------------ | ----------- |
| apply_mode | str | No | loose | loose<br>strict | Set how configlets are attached/detached on container. If set to strict all configlets not listed in your vars are detached. |
| state | str | No | present | present<br>absent | Set if ansible should build or remove devices on Cloudvision |
| topology | dict | Yes |  |  | Yaml dictionary to describe intended containers |
| &nbsp;&nbsp;&nbsp;&nbsp;parentContainerName | str | Yes |  |  | Name of the parent container |
| &nbsp;&nbsp;&nbsp;&nbsp;configlets | List | No |  |  | List of configlets |
| &nbsp;&nbsp;&nbsp;&nbsp;imageBundle | str | No |  |  | The name of the image bundle to be associated with the container |
