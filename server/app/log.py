import logging
import sys

log = logging.getLogger("COAP_SERVER")
log.setLevel(logging.INFO)
_handler = logging.StreamHandler(sys.stdout)
_handler.setLevel(logging.INFO)
log.addHandler(_handler)
