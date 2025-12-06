import os
from ruamel.yaml import YAML
from devops_cli.models.k8s import K8sResourceList

class YamlRenderer:
    def __init__(self):
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)

    def render(self, resource_list: K8sResourceList, output_dir: str) -> list[str]:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        generated_files = []

        for resource in resource_list.resources:
            # Determine filename
            kind = resource.kind.lower()
            name = resource.metadata.name
            filename = f"{name}-{kind}.yaml"
            filepath = os.path.join(output_dir, filename)

            # Dump model to dict
            # We use exclude_none=True to keep it clean, but careful with required fields
            # Pydantic's model_dump is good.
            resource_dict = resource.model_dump(exclude_none=True, by_alias=True)

            with open(filepath, 'w') as f:
                self.yaml.dump(resource_dict, f)
            
            generated_files.append(filepath)

        return generated_files
