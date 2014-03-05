# supreme_dlw.py
# used in: Supreme with Cheese
# file extension: .dlw
# Supreme world file format

from sformats.utils import *

# constructs and adapters

class RleBitmap(Construct):
    def isEncoded(self, method, row):
        return bool((ord(method[row / 8]) >> (row % 8)) & 1)
        
    def _parse(self, stream, context):
        rows = []
        for row in range(24):
            if self.isEncoded(context["method"], row):
                cols = []
                while len(cols) < 32:
                    cols += map(ord, ord(stream.read(1)) * stream.read(1))
                rows.append(cols)
            else:
                rows.append(map(ord, stream.read(32)))
        return rows
        
    def _build(self, obj, stream, context):
        for row in range(24):
            cols = obj[row]
            if self.isEncoded(context["method"], row):
                value, run = cols[0], 1
                for pixel in cols[1:]:
                    if pixel == value:
                        run += 1
                    else:
                        stream.write(chr(run) + chr(value))
                        value, run = pixel, 1
                stream.write(chr(run) + chr(value))
            else:
                stream.write(''.join(map(chr, cols)))
        
    def _sizeof(self, context):
        raise SizeofError

class RleLevel(Construct):
    def _parse(self, stream, context):
        RUN = SLInt8("run")
        width, height = context["width"], context["height"]
        rawTiles = []
        while len(rawTiles) < width * height:
            run = RUN.parse(stream.read(1))
            if run < 0:
                tile = levelTile.parse(stream.read(levelTile.sizeof()))
                for i in range(-run):
                    rawTiles.append(tile)
            else:
                for i in range(run):
                    rawTiles.append(levelTile.parse(stream.read(levelTile.sizeof())))
        rows = []
        for row in range(height):
            cols = []
            for col in range(width):
                cols.append(rawTiles[row * width + col])
            rows.append(cols)
        return rows
        
    def _build(self, obj, stream, context):
        RUN = SLInt8("run")
        tiles = []
        for row in obj:
            for col in row:
                tiles.append(levelTile.build(col))
                
        runStart = sameStart = 0
        sameLength = diffLength = 1
        src = 0
        
        for pos, tile in enumerate(tiles):
            if pos == 0: continue
            if tile == tiles[src]: # the same
                sameLength += 1
                if sameLength == 128: # continue a same run
                    stream.write(RUN.build(-127))
                    stream.write(tiles[src])
                    sameStart = runStart = pos
                    sameLength = diffLength = 1
                elif sameLength == 2 and runStart != sameStart: # end a different run and start a same
                    stream.write(RUN.build(sameStart - runStart))
                    for i in range(sameStart - runStart):
                        stream.write(tiles[runStart + i])
                    runStart = sameStart
                    diffLength = 1
            else: # different
                if sameLength < 2: # continue a different run
                    sameLength = 1
                    sameStart = pos
                    src = pos
                    diffLength += 1
                    if diffLength == 128:
                        stream.write(RUN.build(127))
                        for i in range(127):
                            stream.write(tiles[runStart + i])
                        diffLength = 1
                        runStart = pos
                else: # end a same run and start a different
                    stream.write(RUN.build(-sameLength))
                    stream.write(tiles[src])
                    sameStart = runStart = pos
                    sameLength = diffLength = 1
                    src = pos
        if sameLength > 1: # finish up a same run
            stream.write(RUN.build(-sameLength))
            stream.write(tiles[src])
        else: # finish up a different run
            stream.write(RUN.build(diffLength))
            for i in range(diffLength):
                stream.write(tiles[runStart + i])
        
    def _sizeof(self, context):
        raise SizeofError

class ItemContainer(Construct):
    def _parse(self, stream, context):
        result = []
        itemId = 0
        for i in range(context["itemCount"]):
            if itemId != 255:
                itemId = ord(stream.read(1))
                data = item.parse(stream.read(item.sizeof()))
                data.itemId = itemId
                result.append(data)
            else:
                data = item.parse(stream.read(item.sizeof()))
                data.itemId = 255
                result.append(data)
        return result
        
    def _build(self, obj, stream, context):
        part = 0
        for data in obj:
            if data.itemId == 255:
                if part == 0:
                    stream.write(chr(255))
                    part = 1
                stream.write(item.build(data))
            else:
                stream.write(chr(data.itemId))
                stream.write(item.build(data))
        
    def _sizeof(self, context):
        raise SizeofError

class ItemDropAdapter(Adapter):
    def _encode(self, obj, ctx):
        return chr(int(256 * (obj - int(obj)))) + chr(int(obj))
    def _decode(self, obj, ctx):
        return ord(obj[1]) + ord(obj[0]) / 256.0

# structures

monster = Struct("monster",
    ULInt8("x"),
    ULInt8("y"),
    ULInt8("type"),
    ULInt8("item"),
)

trigger = Struct("trigger",
    ULInt8("parameter"),
    ULInt8("type"),
    ULInt8("x"),
    ULInt8("y"),
    ULInt32("index1"),
    ULInt32("index2"),
)

effect = Struct("effect",
    Embed(trigger),
    PackedString("text"),
)

special = Struct("special",
    ULInt8("x"),
    ULInt8("y"),
    ULInt8("uses"),
    BitStruct("length",
        BitField("effects", 5),
        BitField("triggers", 3)
    ),
    Array(lambda ctx: ctx["length"]["triggers"], trigger),
    Array(lambda ctx: ctx["length"]["effects"], effect),
)

levelTile = Struct("levelTile",
    ULInt16("floor"),
    ULInt16("wall"),
    ULInt8("item"),
    SLInt8("light"),
)

level = Struct("level",
    #Tell("level"),
    ULInt8("width"),
    ULInt8("height"),
    #Tell("text"),
    PackedString("name"),
    PackedString("song"),
    #Tell("monsters"),
    ULInt8("monsterCount"),
    Array(lambda ctx: ctx["monsterCount"], monster),
    ULInt8("specialCount"),
    Array(lambda ctx: ctx["specialCount"], special),
    BitStruct("flags",
        Flag("underwater"),
        Flag("starry"),
        Flag("lantern"),
        Flag("torch"),
        Flag("secret"),
        Flag("hub"),
        Flag("raining"),
        Flag("snowing"),
        Flag("reserved5"),
        Flag("reserved4"),
        Flag("reserved3"),
        Flag("reserved2"),
        Flag("reserved1"),
        Flag("reserved0"),
        Flag("stealth"),
        Flag("underlava"),
    ),
    ULInt16("brains"),
    ULInt16("candles"),
    ItemDropAdapter(Bytes("itemDrop", 2)),
    #Tell("tiles"),
    RleLevel("tiles"),
)

tileImage = Struct("tileImage",
    Bytes("method", 3),
    RleBitmap("bitmap"),
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
        Flag("bouncy"),
        Flag("enemyProof"),
        Flag("ghostProof"),
        Flag("bunnyPath"),
        Flag("minecartPath"),
        Flag("transparentRoof"),
        Flag("animateHit"),
        Flag("animateStep"),
    ),
    ULInt16("nextTile"),
)

item = Struct("item",
    PackedString("name"),
    SLInt8("offsetX"),
    SLInt8("offsetY"),
    ULInt16("sprite"),
    ULInt8("fromColor"),
    ULInt8("toColor"),
    SLInt8("light"),
    ULInt8("rarity"),
    BitStruct("flags",
        Padding(1),
        Flag("useTileGraphic"),
        Flag("loonyColor"),
        Flag("pickup"),
        Flag("bulletproof"),
        Flag("impassible"),
        Flag("glowing"),
        Flag("shadow"),
        Padding(8)
    ),
    BitStruct("themes",
        Flag("crate"),
        Flag("rock"),
        Flag("tree"),
        Flag("door"),
        Flag("bulletproof"),
        Flag("obstacle"),
        Flag("decoration"),
        Flag("pickup"),
        Flag("chair"),
        Flag("entrance"),
        Flag("food"),
        Flag("collectible"),
        Flag("key"),
        Flag("powerup"),
        Flag("weapon"),
        Flag("sign"),
        Padding(7),
        Flag("custom"),
        Padding(8)
    ),
    BitStruct("trigger",
        Flag("always"),
        Flag("minecart"),
        Flag("machete"),
        Flag("friendbump"),
        Flag("enemybump"),
        Flag("playerbump"),
        Flag("shoot"),
        Flag("pickup"),
        Padding(8)
    ),
    ULInt8("effect"),
    SLInt16("effectData"),
    PackedString("message", 64),
    ULInt16("sound")
)

sound = Struct("sound",
    ULInt16("soundId"),
    PackedString("name"),
    BitStruct("theme",
        Padding(2),
        Flag("custom"),
        Flag("vocal"),
        Flag("effect"),
        Flag("monster"),
        Flag("player"),
        Flag("intface")
    ),
    SLInt32("dataSize"),
    MetaField("data", lambda ctx: ctx["dataSize"])
)

supreme_dlw = Struct("world",
    String("gameid", 8),
    PackedString("author"),
    PackedString("name"),
    ULInt8("levelCount"),
    ULInt32("totalPoints"),
    ULInt16("tileCount"),
    Array(lambda ctx: ctx["tileCount"], tileImage),
    Array(lambda ctx: ctx["tileCount"], tileData),
    Array(lambda ctx: ctx["levelCount"], level),
    #Tell("items"),
    ULInt16("itemCount"),
    ItemContainer("items"),
    SLInt16("soundCount"),
    Array(lambda ctx: ctx["soundCount"], sound),
    #Tell("end")
)
