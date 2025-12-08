"""

log, raise interfaces
"""

from .exceptions import CoreExceptionError, make_raise

from .log_message import err_msg, log_msg, warn_msg

__ALL_ = [log_msg, err_msg, warn_msg, make_raise, CoreExceptionError]
