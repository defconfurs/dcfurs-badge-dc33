include("$(PORT_DIR)/boards/manifest.py")

# Drivers
require("espflash")

# Utils
require("time")
require("senml")
require("logging")
require("tarfile")

# Modules
module("boot.py")
