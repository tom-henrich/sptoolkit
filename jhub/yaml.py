#!/usr/bin/env python3

"""A consolidated yaml API with ruamel.yaml workaround.

ensures the same yaml settings for reading/writing throughout.

"""
from ruamel.yaml.composer import Composer
from ruamel.yaml import YAML


class _NoEmptyFlowComposer(Composer):
    """yaml composer that avoids setting flow_style on empty containers.

    A workaround for ruamel.yaml issue #255.

    """

    def compose_mapping_node(self, anchor):
        node = super().compose_mapping_node(anchor)
        if not node.value:
            node.flow_style = False
        return node

    def compose_sequence_node(self, anchor):
        node = super().compose_sequence_node(anchor)
        if not node.value:
            node.flow_style = False
        return node


# create the global yaml object:
yaml = YAML(typ="rt")
yaml.Composer = _NoEmptyFlowComposer
