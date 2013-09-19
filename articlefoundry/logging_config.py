import logging

print logging.getLogger('').handlers

logging.basicConfig(level=logging.DEBUG,
                    format=("%(asctime)s %(name)-12s %(levelname)-8s "
                            "%(message)s"))
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)
