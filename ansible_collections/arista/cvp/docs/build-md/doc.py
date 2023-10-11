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
    )

    template = env.get_template("md.j2")
    name = name.removesuffix(".py")
    filename = f"{name}.md"

    content = template.render(
        module=data,
        name=name,
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
