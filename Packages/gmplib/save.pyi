from matplotlib.pyplot import figure
from os import PathLike
from typing import Dict, List, Optional, Tuple, Union

def create_directories(
    results_path: Tuple[str, str] = ..., results_dir: str = ...
) -> str: ...
def create_dir(dir_: str) -> str: ...
def export_results(
    results_dir: PathLike, filename: PathLike, raw_dict: Dict, suffix: str = ...
) -> None: ...
def export_plots(
    fig_dict: Dict,
    results_dir: PathLike,
    file_types: Union[List[str], Tuple[str], str] = ...,
    suffix: str = ...,
    dpi: Optional[int] = ...,
) -> None: ...
def export_plot(
    fig_name: str,
    fig: figure,
    results_dir: PathLike,
    file_type: str = ...,
    suffix: str = ...,
    dpi: Optional[int] = ...,
) -> None: ...
