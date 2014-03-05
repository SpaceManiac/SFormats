# ll2_profile.py
# used in: Loonyland 2
# file extension: .loony
# Character profile

from sformats.utils import *
import functools

# helpers

Mystery = MysteryCounter()

def countNumber(len, obj, ctx):
	if ctx == None:
		# not the first call
		return
	while not "_varNumber" in ctx:
		ctx = ctx["_"]
	if len == -1:
		note = "Variable #%03d (flag)" % ctx["_varNumber"]
		ctx["_varNumber"] += 1
	else:
		note = "Variable #%03d" % ctx["_varNumber"]
		ctx["_varNumber"] += len
	return note
	
def clockFormatter(obj, ctx):
	seconds = obj / 30.0
	minutes = int(seconds) / 60
	hours = minutes / 60
	return "%d:%02d:%02.2d" % (hours, minutes % 60, seconds % 60)

def VarNumber(name, len=1):
	return EditableAdapter(NoteWrapper(EditNumber, functools.partial(countNumber, len)), [ULInt8, ULInt16][len-1](name))
def VarFlag(name):
	return EditableAdapter(NoteWrapper(EditBoolean, functools.partial(countNumber, -1)), Flag(name))

def Timer(name):
	return EditableAdapter(NoteWrapper(EditNumber, clockFormatter), ULInt32(name))

# structures

def InventoryItem(name):
	return Struct(name,
		ULInt8("amount"),
		ULInt8("type"),
		ULInt8("primaryStat"),
		Flag("sharpened"),
		ULInt8("prefix"),
		ULInt8("secondaryStat"),
		Array(3, ULInt8("skillUpgrades"))
	)

def Inventory(name, length):
	return Array(length, InventoryItem(name))

variables = Struct("variables",
	Value("_varNumber", lambda ctx: 0),
	Array(50, VarFlag("questAssigned")),
	Array(50, VarFlag("questCompleted")),
	VarNumber("killCount"),
	Array(99, VarFlag("collectedPresent")),
	VarFlag("killedMagicHat"),
	VarFlag("killedStoneRose"),
	Struct("phileasDestinations",
		VarFlag("eisburg"),
		VarFlag("arena"),
		VarFlag("baskerville"),
		VarFlag("frostyCliffs"),
		VarFlag("hauntedHighway"),
		VarFlag("glacialGorge"),
		Array(9, VarFlag("unused"))
	),
	VarFlag("melodyUnlocked"),
	VarFlag("toyFactoryDestroyed"),
	VarFlag("killedStinkySock"),
	Struct("treesChopped",
		VarFlag("limpidLake"),
		VarFlag("westwood")
	),
	VarNumber("cellarRatCount"),
	Array(33, VarNumber("temporaryVars")),
	Array(50, VarFlag("chestOpened")),
	VarFlag("killedKlonk"),
	VarNumber("mickeyKillCount"),
	VarNumber("bearKillCount"),
	VarFlag("snugglyBunny"),
	VarFlag("killedKillbor"),
	VarFlag("hasMagicGlasses"),
	VarNumber("arenaSwordsCollected"),
	Struct("bridgeRoped",
		VarFlag("northwoodTopLeft"),
		VarFlag("frostyCliffsLeft"),
		VarFlag("frostyCliffsTop"),
		VarFlag("frostyCliffsRight"),
		VarFlag("toyFactory"),
		VarFlag("northwoodTopLeft2"),
		VarFlag("northwoodTopRight"),
		VarFlag("unknown")
	),
	VarFlag("killedRatatouille"),
	VarFlag("talkedToOnion"),
	VarFlag("factoryFirstFloorCleared"),
	VarFlag("killedBurningBush"),
	VarFlag("killedTrigun"),
	Array(4, VarFlag("shakenMerchants")),
	VarFlag("supplyBaseDestroyed"),
	VarFlag("wonRumble"),
	VarFlag("escapedPrison"),
	VarFlag("killedJunksmith"),
	VarFlag("highwayMissionCompleted"),
	Struct("clockworkBot",
		VarNumber("logs"),
		VarNumber("gears"),
		VarNumber("tinCans"),
		VarNumber("stuffing"),
		VarNumber("socks"),
		VarNumber("iceCubes"),
		VarNumber("seeds"),
		VarNumber("rocks"),
		VarNumber("ectoplasm"),
		VarNumber("claws"),
		VarNumber("silver"),
		VarNumber("gold"),
		VarNumber("rubies"),
		VarNumber("emeralds"),
		VarNumber("diamonds")
	),
	VarNumber("clockbotHealthLower"),
	VarNumber("currentGuruTalent"),
	VarFlag("historianGotBook"),
	Array(5, VarFlag("crystalBarriers")),
	VarFlag("killedGourdzilla"),
	VarNumber("bodzhasAliveLeft"),
	VarNumber("bodzhasAliveRight"),
	VarFlag("shrumfordYoungified"),
	Array(10, VarFlag("bokbokRescued")),
	VarNumber("bokboksReturned"),
	VarFlag("furnaceLit"),
	VarNumber("justhefAxeTimer"),
	Array(10, VarFlag("killedTitans")),
	VarNumber("captainStatus"),
	Struct("tipsShown",
		VarFlag("playingTheGame"),
		VarFlag("quests"),
		VarFlag("badguys"),
		VarFlag("skills"),
		VarFlag("agonyOfDefeat"),
		VarFlag("throwingAxes"),
		VarFlag("stamina"),
		VarFlag("equipment"),
		VarFlag("potions"),
		VarFlag("savingGame"),
		VarFlag("startingOut"),
		VarFlag("magicItems"),
		VarFlag("shoveling"),
		VarFlag("magicGlasses"),
		VarFlag("levelUp"),
		VarFlag("magicSpells"),
		VarFlag("clockwork"),
		VarFlag("junksmithing"),
		VarFlag("spellSynergy"),
		Array(6, VarFlag("unused")),
	),
	VarFlag("frostburnDoorSmashed"),
	Array(5, VarNumber("puppetHealth")),
	VarFlag("killedFrostburn"),
	VarFlag("killedMelton"),
	Array(4, VarFlag("frostburnSwitchFlipped")),
	VarNumber("mimicTamed"),
	Array(4, VarFlag("frostburn2SwitchFlipped")),
	Array(5, VarNumber("selectedSpell")),
	VarFlag("spokenToBird"),
	VarFlag("madcapMode"),
	Struct("madcapCrystals",
		VarNumber("might"),
		VarNumber("life"),
		VarNumber("shield"),
		VarNumber("curse"),
		VarNumber("health"),
		VarNumber("shock"),
		VarNumber("fire"),
		VarNumber("ice"),
		VarNumber("wind"),
		VarNumber("nature"),
		VarNumber("death")
	),
	Array(4, VarNumber("modifiers")),
	VarNumber("crystalPoints"),
	VarNumber("parryTimer"),
	VarNumber("clockbotLifeUpper"),
	Array(20, VarNumber("controls")),
	Array(10, VarNumber("skipped")),
	VarNumber("soundVolume"),
	VarNumber("musicVolume"),
	VarFlag("commentaryEnabled"),
	Struct("killCounters",
		VarNumber("ghosts", 2),
		VarNumber("ice", 2),
		VarNumber("bears", 2),
		VarNumber("mice", 2),
		VarNumber("bodzhas", 2),
		VarNumber("puppets", 2),
		VarNumber("monkeys", 2),
		VarNumber("stone", 2),
		VarNumber("shrooms", 2),
		VarNumber("soldiers", 2),
		VarNumber("plants", 2),
		VarNumber("gangsters", 2),
		VarNumber("knights", 2)
	),
	VarNumber("arenaVictories"),
	VarNumber("deathCount"),
	VarFlag("flameSkillUsed"),
	VarNumber("klonkTreesSmashed"),
	Array(385, VarNumber("custom"))
)

ll2_profile = Struct("ll2profile",
	PackedString("characterName", 16),
	ULInt32("money"),
	Mystery(1),
	ULInt8("mapName"),
	Struct("loony",
		ULInt32("idleTime"),
		ULInt16("health"),
		ULInt16("maxHealth"),
		Mystery(6),
		ULInt8("petrifiedTime"),
		Mystery(1),
		ULInt8("invincibilityTime"),
		Mystery(2),
		ULInt8("x"),
		Mystery(3),
		ULInt8("y"),
		Mystery(13),
		ULInt32("monster"),
	),
	ULInt16("baseHealth"),
	Mystery(10),
	Flag("timerEnabled"),
	Timer("timerValue"),
	Mystery(8),
	ULInt32("axesUsed"),
	ULInt32("spellsCast"),
	Mystery(4),
	ULInt32("moneyCollected"),
	ULInt32("damageTaken"),
	Mystery(1),
	variables,
	Mystery(81),
	PackedString("adventureName", 10),
	Mystery(8),
	Timer("clock"),
	ULInt32("potionsMade"),
	ULInt32("monstersSlain"),
	ULInt32("herbsCollected"),
	ULInt32("holesDug"),
	ULInt32("damageDealt"),
	SLInt32("experience"),
	ULInt32("experienceToLevel"),
	ULInt8("playerLevel"),
	Mystery(3),
	ULInt8("axeMode"),
	Mystery(1),
	ULInt8("magic"),
	ULInt8("maxMagic"),
	ULInt8("baseMagic"),
	ULInt8("stamina"),
	ULInt8("maxStamina"),
	Mystery(2),
	Struct("inventory",
		InventoryItem("equippedAxe"),
		InventoryItem("equippedParka"),
		InventoryItem("equippedAmulet"),
		ULInt8("lense1"),
		ULInt8("lense2"),
		Inventory("loony", 60),
		Inventory("blackMarket", 24),
		Inventory("geoffrey", 24),
		Inventory("taylor", 24),
		Inventory("guyMagic", 24),
		Inventory("rupert", 24),
		Inventory("shroud", 24),
		Inventory("mimic", 24)
	),
	Mystery(648),
	Array(50, ULInt8("skillUnlocked")),
	Array(50, ULInt8("skillLevels")),
	ULInt8("plagueActivated"),
	ULInt8("plagueDuration"),
	Mystery(74),
	ULInt8("heatShieldStrength"),
	ULInt8("heatShieldDuration"),
	Mystery(22),
	Array(30, ULInt16("talentProgress")),
	Array(30, ULInt8("talents")),
	Mystery(7),
	ULInt16("berserkTime"),
	Mystery(8),
	Array(30, PackedString("messageLog", 64)),
	Mystery.Finish()
)
