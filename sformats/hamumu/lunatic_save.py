# lunatic_save.py
# used in: Dr. Lunatic
# file extension: .sav
# user save slot

from sformats.utils import *

# struct description from Dr. Lunatic source

# byte = ULInt8, int = SLInt32
# MAX_CUSTOM = 128, MAX_MAPS = 24

# // values for the overall game
# byte musicSettings;
# int prevScore; // so you can lose all your points when you die
# int score;
# byte levelPassed[MAX_CUSTOM][MAX_MAPS];
# byte keychain[MAX_CUSTOM][4];
# // total completion is how many "points" the world has in it
# int totalCompletion[MAX_CUSTOM];
# // complete is how many of those points the player has, to create a percentage complete display
# int complete[MAX_CUSTOM];
# char customName[MAX_CUSTOM][32];
# byte lunacyKey[MAX_CUSTOM];
# // values reset for each world
# byte levelsPassed;
# byte worldNum;
# // values reset for each level
# byte shield;
# byte levelNum;
# byte keys[4];
# int boredom;
# byte hammers;
# byte hamSpeed;
# byte weapon;
# int ammo;
# byte reload;
# byte wpnReload;
# byte life;
# int brains;
# byte pushPower; // for pushing pushy blocks
# byte hammerFlags;
# byte vehicle;
# byte garlic;
# byte speed; // accelerated
# byte rageClock;
# word rage;
# byte invisibility;
# byte jetting;

# structures

MAX_CUSTOM = 128
MAX_MAPS = 24

keychains = Struct("keychains",
	Flag("pumpkin"),
	Flag("hammer"),
	Flag("rocket"),
	Flag("squash")
)

progress = Struct("progress",
	Array(MAX_CUSTOM, Array(MAX_MAPS, Flag("levelPassed"))),
	Array(MAX_CUSTOM, keychains),
	Array(MAX_CUSTOM, SLInt32("totalCompletion")),
	Array(MAX_CUSTOM, SLInt32("completion")),
	Array(MAX_CUSTOM, PackedString("filename")),
	Array(MAX_CUSTOM, Flag("loonyKey")),
)

levelData = Struct("levelData",
	ULInt8("shield"),
	ULInt8("levelNum"),
	Array(4, ULInt8("keys")),
	SLInt32("boredom"),
	ULInt8("hammers"),
	ULInt8("hamSpeed"),
	ULInt8("weapon"),
	Padding(1),
	SLInt32("ammo"),
	ULInt8("reload"),
	ULInt8("wpnReload"),
	ULInt8("life"),
	Padding(1),
	SLInt32("brains"),
	ULInt8("pushPower"),
	ULInt8("hammerFlags"),
	ULInt8("vehicle"),
	ULInt8("garlic"),
	ULInt8("speed"),
	ULInt8("rageClock"),
	ULInt16("rage"),
	ULInt8("invisibility"),
	ULInt8("jetting"),
	Padding(2),
)

player = Struct("player",
	ULInt8("musicSettings"),
	Padding(3),
	SLInt32("previousScore"),
	SLInt32("score"),
	progress,
	ULInt8("levelsPassed"),
	ULInt8("worldNum"),
	levelData
)

lunatic_save = Struct("lunatic_save",
	Array(3, player)
)
