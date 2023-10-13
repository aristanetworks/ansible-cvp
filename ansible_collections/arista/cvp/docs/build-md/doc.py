#!/usr/bin/python
# coding: utf-8 -*-
#
# Copyright 2023 Arista Networks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
from pathlib import Path

from ansible.parsing.plugin_docs import read_docstring
from jinja2 import Environment, FileSystemLoader

MODULE_NAME_STARTS_WITH = "cv_"
MODULEDIR = "../../plugins/modules/"
OUTPUTDIR = "../modules"


def jinja2_writer(template_dir, name, data):
    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        keep_trailing_newline=True
    )

    template = env.get_template("md.j2")
    name = name.removesuffix(".py")
    filename = f"{name}.md"

    try:
        Path(f"../schema/{name}.md").read_text(encoding="UTF-8")
        schema = f"../schema/{name}.md"
    except FileNotFoundError:
        schema = None

    try:
        Path(f"../outputs/{name}.txt").read_text(encoding="UTF-8")
        module_output = f"docs/outputs/{name}.txt"
    except FileNotFoundError:
        module_output = None

    content = template.render(
        module=data, name=name, schema=schema, module_output=module_output
    )
    with open(os.path.join(OUTPUTDIR, filename), mode="w", encoding="utf-8") as file:
        file.write(content)
        print(f"{filename} saved")

    return env, template


def main():
    for module in os.listdir(MODULEDIR):
        if module.startswith(MODULE_NAME_STARTS_WITH):
            file = os.path.join(MODULEDIR, module)
            if Path(file).is_file():
                data = read_docstring(file)
                jinja2_writer("./templates", module, data)


if __name__ == "__main__":
    main()
