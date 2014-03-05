# lunatic_options.py
# used in: Dr. Lunatic
# file extension: .cfg
# global configuration options

from sformats.utils import *

# structures

controls = Struct("controls",
	ULInt8("up"),
	ULInt8("down"),
	ULInt8("left"),
	ULInt8("right"),
	ULInt8("button1"),
	ULInt8("button2")
)

lunatic_options = Struct("options",
	Array(2, controls),
	Array(2, ULInt8("joyControls")),
	Flag("sound"),
	Flag("music"),
	ULInt8("playAs"),
	Flag("wonGame"),
	Flag("gotAllSecrets"),
	Flag("youSuck"),
	Flag("discoMode"),
	Flag("smoothLight")
)
