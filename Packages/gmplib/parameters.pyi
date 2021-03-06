from typing import Dict, List, Optional, Tuple, Union

def import_parameters(
    path: Tuple[str], filenames: Tuple[str] = ...
) -> Tuple[Dict, str]: ...
def read_json_file(filepaths: Union[Tuple[str], List[str]]) -> Dict: ...

class Parameters:
    def __init__(
        self,
        imported_parameters: Dict,
        evaluations: Optional[Dict] = ...,
        sequence: Tuple = ...,
    ) -> None: ...

class ParametersNestedGroup:
    def __init__(
        self,
        parent: Parameters,
        group_name: str,
        parameters_dict: Dict,
        evaluations: Optional[Dict] = ...,
    ) -> None: ...
