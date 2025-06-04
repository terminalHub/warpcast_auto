from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass
class Cv2MinMaxLocBo:
    img_template: np.ndarray
    min_val: float
    max_val: float
    min_loc: Tuple[int, int]
    max_loc: Tuple[int, int]
