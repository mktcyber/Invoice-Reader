"""
This module abstracts templates for invoice providers.
Templates are initially read from .yml files and then kept as class.
See: extract.invoice_template

"""

import codecs
import logging
import os
from collections import OrderedDict

import chardet
import yaml

from .invoice_template import InvoiceTemplate


logging.getLogger("chardet").setLevel(logging.WARNING)


# borrowed from http://stackoverflow.com/a/21912744
def ordered_load(stream, _loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """
    Loader to load mappings and ordered mappings into the Python 2.7+ OrderedDict type,
    instead of the vanilla dict and the list of pairs it currently uses.

    """

    class OrderedLoader(_loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
    )

    return yaml.load(stream, OrderedLoader)


def load_templates(path):
    """
    Loads YAML template(s) from the given path.
    Returns a list of instances of class InvoiceTemplate.
    If path represents a file instead of a folder, the list
    will contains, if successful, one instance only, and there's no problem.

    Though, it's recommended to use load_template(path)
    if path represents a file, and not a folder

    Parameters
    ----------
    path : str
        Path to a single template file, or a folder

    Returns
    -------
    output : list [InvoiceTemplate]
        A list of instances of class InvoiceTemplate

    Note
    ----
    - A template file MUST be a valid YAML file with extension .yml

    After reading the templates, you can use the result as an instance of **InvoiceTemplate**
    to extract fields using InvoiceTemplate.extract_data()

    """

    output = []

    if os.path.isfile(path):
        assert path.endswith(".yml"), f"{path} is not a valid YAML file"
        output.append(load_template(path))
    else:
        for dir_path, dir_names, filenames in os.walk(path):
            for name in sorted(filenames):
                if name.endswith(".yml"):
                    output.append(load_template(os.path.join(dir_path, name)))
                
    return output


def load_template(path):
    """
    Loads a YAML template from the given path.
    Returns an instance of class InvoiceTemplate.

    Where path must be a file.

    """
    with open(path, "rb") as f:
        encoding = chardet.detect(f.read())["encoding"]
    with codecs.open(path, encoding=encoding) as path:
        template = ordered_load(path.read())
    template["template_name"] = path

    # Test if all required fields are in template:
    assert "keywords" in template.keys(), "Missing keywords field."

    # Keywords as list, if only one.
    if type(template["keywords"]) is not list:
        template["keywords"] = [template["keywords"]]

    return InvoiceTemplate(template)
