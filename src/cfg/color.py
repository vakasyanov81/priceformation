"""Color scheme"""

import dataclasses


@dataclasses.dataclass
class Colors:
    """Color scheme"""

    HEADER = "\033[95m"
    OK_BLUE = "\033[94m"
    OK_CYAN = "\033[96m"
    OK_GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    END_COLOR = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
