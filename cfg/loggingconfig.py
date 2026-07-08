import sys
import logging

sys.path.append(r"C:\Users\ncbof\hypoxia\cbibsbaseproj\cbibsbase")

def setup_logging():
    log_dir = r"C:\Users\ncbof\hypoxia\windroseproj\logs"
    import os
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(
                r"C:\Users\ncbof\hypoxia\windroseproj\logs\windrose.log"
            ),
            logging.StreamHandler()
        ]
    )