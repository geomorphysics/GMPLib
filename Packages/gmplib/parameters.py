"""
---------------------------------------------------------------------

Import job parameters from JSON files and build a settings dictionary

TODO: This might be better done using dataclasses

---------------------------------------------------------------------

Requires Python packages/modules:
  -  :mod:`sympy`

---------------------------------------------------------------------
"""

import warnings
import logging
from os.path import realpath, join
from json import load
from copy import copy

# Typing
from typing import Dict, Tuple, Any, List, Union, Optional

# SymPy
from sympy.parsing.sympy_parser import parse_expr

warnings.filterwarnings("ignore")

__all__ = ['import_parameters', 'read_json_file',
           'Parameters', 'ParametersNestedGroup']


def import_parameters(
    path: Tuple[str],
    filenames: Tuple[str] = ('defaults',)
) -> Tuple[Dict, str]:
    """
    Load JSON parameters files (defaults and job) and parse them in turn to
    generate a job parameters dictionary.

    Args:
        path (list): path to JSON parameters files
        filenames (str): list of defaults and job JSON parameter filenames

    Return:
        dict:  job parameter dictionary
    """
    # Parse default and assigned JSON parameters files
    dirpath: str = realpath(join(*path))
    filepaths: List[str] \
        = [realpath(join(dirpath, filename)) for filename in filenames]
    return (read_json_file(filepaths), dirpath)


def read_json_file(filepaths: Union[Tuple[str], List[str]]) -> Dict:
    """
    Load and parse a list of JSON parameters files into a parameters dict.

    Step through a list of JSON parameters files
    (usually "defaults.json" and the job JSON file).
    Parse each into a parameters dict, ensuring that subsequent JSON parameters
    override any set by previous JSON files.

    Args:
        filepaths: JSON parameters files to be read and parsed

    Return:
        dict:  job parameters dictionary
    """
    # Start wit a clean parameters dictionary
    parameters_dict: Dict[Any, Any] = {}
    # Step through each JSON parameters file in turn
    for filepath in filepaths:
        parameters_file_name = filepath+'.json'
        # Read in the parameters file
        with open(parameters_file_name, encoding='latin-1') as json_file:
            parameters = load(json_file)
        # Step through all the dict items in turn
        # We do this so that we can replace a (sub-)dict item
        #   if the second (etc) JSON file needs to override
        #   an item value set in the first (etc) JSON parameters file.
        for key, item in zip(parameters.keys(), parameters.items()):
            # Check to see if the item is itself a dict
            if isinstance(item[1], dict):
                # If so, step through this source sub-dict
                for subitem in item[1].items():
                    # If the destination sub-dict doesn't exist yet, create it
                    # Either way, add the item to this sub-dict
                    # logging.debug(item[0])
                    if item[0] in parameters_dict:
                        # logging.debug(parameters_dict[item[0]])
                        # The sub-dict exists: update this key and value
                        parameters_dict[item[0]].update(
                            {subitem[0]: subitem[1]})
                    else:
                        # The sub-dict does not exist yet, so set this key
                        #    and value as its first item
                        parameters_dict[item[0]] = {subitem[0]: subitem[1]}
            else:
                # If not a dict, set the key, value
                parameters_dict[key] = item[1]
                # This should not happen if the parameters file is a set
                #   of sub-dicts only, one per workflow class instance
    return parameters_dict


class Parameters():
    """
    Parameters (job parameters) container
    """

    def __init__(
            self,
            imported_parameters: Dict,
            evaluations: Optional[Dict] = None,
            sequence: Tuple = ()
    ) -> None:
        """
        Initialize class instance.
        Convert top-level items in the parameters dictionary,
        whose keys are group names
        and whose values are sub-dictionary groups of parameters,
        into class attributes.
        The attribute names are the group names and their values
        are the sub-dictionaries.

        Args:
            imported_parameters:
                job parameters dictionary

        Attributes:
            various (class attribute): matching top-level items in the
            parameters dictionary
        """

        evaluations_: Dict = {} if evaluations is None else evaluations
        imported_parameters_: Dict = copy(imported_parameters)
        for group_name in sequence:
            group_dict = imported_parameters[group_name]
            setattr(
                self,
                group_name,
                ParametersNestedGroup(group_name, group_dict, evaluations_)
            )
            imported_parameters_.pop(group_name)
        for group_name, group_dict in imported_parameters_.items():
            group_dict = imported_parameters_[group_name]
            setattr(
                self,
                group_name,
                ParametersNestedGroup(group_name, group_dict, evaluations_)
            )


class ParametersNestedGroup():
    """
    ParametersNestedGroup (job parameters) sub-container
    """

    def __init__(
            self,
            group_name: str,
            parameters_dict: Dict,
            evaluations: Optional[Dict] = None
    ) -> None:
        """
        Initialize class instance.
        Convert items in a parameters sub-dictionary into class attributes,
        setting the attribute name to the dict item's key and the
        attribute value to the dict item's value.
        If the value is a Sympy reference, parse it into a Sympy object
        before attribution.

        Args:
            imported_parameters (dict): job parameters dictionary

        Attributes:
            various (class attribute): matching second-level items in the
            parameters dictionary
        """
        if evaluations is None:
            evaluations = {}
        # logging.debug(group_name, parameters_dict, evaluations)
        for s_key, s_value in parameters_dict.items():
            setattr(self, s_key, parse_expr(s_value.replace('sy.', ''))
                    if isinstance(s_value, str) and 'sy.' in s_value else
                    (None if s_value == 'None' else (s_value)))
        # For each item containing a "p." reference, evaluate it
        #  - this allows us to set parameters that are dependent on
        #    other parameters
        p = self
        if group_name in evaluations.keys():
            for attr in evaluations[group_name]:
                logging.debug(group_name, attr, eval(str(getattr(self, attr))))
                setattr(p, attr, eval(str(getattr(self, attr))))
