# lunatic_dlw.py
# used in: Dr. Lunatic
# file extension: .dlw
# old-style world file

from sformats.utils import *

# structures

monster = Struct("monster",
	ULInt8("x"),
	ULInt8("y"),
	ULInt8("type")
)

special = Struct("special",
	BitStruct("trigger",
		Flag("shoot"),
		Flag("haveBrains"),
		Flag("killAll"),
		Flag("haveKeychains"),
		Flag("passedLevels"),
		Flag("near"),
		Flag("enemyStep"),
		Flag("step"),
		Flag("floorAt"),
		Flag("killMonster"),
		Flag("hasLoonyKey"),
		Flag("randomChance"),
		Flag("timer"),
		Flag("chainAdjacent"),
		Flag("showMessage"),
		Flag("canRepeat")
	),
	ULInt8("triggerValue"),
	ULInt8("effect"),
	ULInt8("x"),
	ULInt8("y"),
	ULInt8("effectX"),
	ULInt8("effectY"),
	PackedString("message")
)

levelTile = Struct("levelTile",
	ULInt8("floor"),
	ULInt8("wall"),
	ULInt8("item"),
	SLInt8("light"),
	SLInt8("tempLight"),
	ULInt8("opaque")
)

level = Struct("level",
	SLInt16("width"),
	SLInt16("height"),
	PackedString("name"),
	Array(128, monster),
	Array(32, special),
	ULInt8("song"),
	ULInt8("flags"),
	Array(lambda ctx: ctx["height"],
		Array(lambda ctx: ctx["width"], levelTile)
	)
)

tileData = Struct("tileData",
	BitStruct("flags",
		Flag("animate"),
		Flag("canpushon"),
		Flag("pushable"),
		Flag("lava"),
		Flag("water"),
		Flag("muddy"),
		Flag("icy"),
		Flag("impassible"),
		Padding(3),
		Flag("bunnyPath"),
		Flag("minecartPath"),
		Flag("transparentRoof"),
		Flag("animateHit"),
		Flag("animateStep"),
	),
	ULInt8("nextTile")
)

lunatic_dlw = Struct("world",
	ULInt8("levelCount"),
	SLInt16("totalPoints"),
	Array(400, Field("tileImage", 32*24)),
	Array(200, tileData),
	Array(lambda ctx: ctx["levelCount"], level)
)
