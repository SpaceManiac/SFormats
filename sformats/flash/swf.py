# swf.py
# program: Adobe Flash
# file extension: .swf
# Shockwave Flash player movies

from construct import *
from io import StringIO

class arr(object):
    def __init__(self, type):
        self.type = type
    def __call__(self, n, *args, **kwargs):
        return Array(n, self.type(*args, **kwargs))

class Unnamed(object):
    def __init__(self, base, *args, **kwargs):
        self.base = base
        self.args = args
        self.kwargs = kwargs
    def __call__(self, name):
        return self.base(name, *self.args, **self.kwargs)

# Types used in SWF specification
# Integer types
#SI8 = SBInt8
#SI16 = SBInt16
#SI32 = SBInt32
#SI8n = arr(SI8)
#SI16n = arr(SI16)
#UI8 = ULInt8
#UI16 = ULInt16
#UI32 = ULInt32
#UI8n = arr(UI8)
#UI16n = arr(UI16)
#UI24n
#UI32n = arr(UI32)
#UI64n = arr(ULInt64)

# Floating-point types
# ...

def pad(nbits):
    size = 5 + 4 * nbits
    pad = 8 * (1 + (size - 1) / 8) - size
    return pad

def fixbits(bits):
    value = 0
    for bit in bits:
        value = 2 * value + bit
    return value

def BitIntN(name):
    return Embed(Struct(name,
        Array(lambda ctx: ctx["nbits"], BitField("_bits", 1)),
        Value(name, lambda ctx: fixbits(ctx["_bits"]))
    ))

def GreedyField(name):
    return StringAdapter(GreedyRange(Field(name, 1)))

def KerningRecord(name, field):
    return Struct(name,
        field("code1"),
        field("code2"),
        SLInt16("adjustment")
    )

RGB = Unnamed(Struct, ULInt8("red"), ULInt8("green"), ULInt8("blue"))
RGBA = Unnamed(Struct, ULInt8("red"), ULInt8("green"), ULInt8("blue"), ULInt8("alpha"))
ARGB = Unnamed(Struct, ULInt8("alpha"), ULInt8("red"), ULInt8("green"), ULInt8("blue"))
Rect = Unnamed(BitStruct,
    BitField("nbits", 5, swapped=True),
    BitIntN("xmin"),
    BitIntN("xmax"),
    BitIntN("ymin"),
    BitIntN("ymax"),
    MetaField("_padding", lambda ctx: pad(ctx["nbits"]))
)
LangCode = Enum(ULInt8("languageCode"),
    Undefined = 0,
    Latin = 1,
    Japanese = 2,
    Korean = 3,
    ChineseSimple = 4,
    ChineseTraditional = 5
)

# Shapes
Shape = Unnamed(Struct,
    Embed(BitStruct("bits",
        BitField("fillbits", 4),
        BitField("linebits", 4)
    )),
    GreedyField("shapeData")
)
ShapeWithStyle = GreedyField

# Various tag types

tagTypes = {
    0: Struct("End"),
    1: Struct("ShowFrame"),
##    2: Struct("DefineShape",
##        ULInt16("shapeId"),
##        Rect("shapeBounds"),
##        ShapeWithStyle("shapeInfo")
##    ),
    9: Struct("SetBackgroundColor",
        RGB("color")
    ),
##    14: Struct("DefineSound",
##        ULInt16("soundId"),
##        Embed(BitStruct("soundInfo",
##            BitField("format", 4),
##            BitField("rate", 2),
##            BitField("size", 1),
##            BitField("type", 1)
##        )),
##        ULInt32("sampleCount"),
##        GreedyField("soundData")
##    ),
##    22: Struct("DefineShape2",
##        ULInt16("shapeId"),
##        Rect("shapeBounds"),
##        ShapeWithStyle("shapeInfo")
##    ),
##    32: Struct("DefineShape3",
##        ULInt16("shapeId"),
##        Rect("shapeBounds"),
##        ShapeWithStyle("shapeInfo")
##    ),
##    39: Struct("DefineSprite",
##        ULInt16("spriteId"),
##        ULInt16("frameCount"),
##        GreedyField("tags")
##    ),
    43: Struct("FrameLabel",
        GreedyField("label")
    ),
    64: Struct("EnableDebugger2",
        ULInt16("reserved"),
        CString("password")
    ),
    65: Struct("ScriptLimits",
        ULInt16("maxRecursion"),
        ULInt16("scriptTimeout")
    ),
    69: BitStruct("FileAttributes",
        Padding(1),
        Flag("directBlit"),
        Flag("useGPU"),
        Flag("hasMetadata"),
        Flag("as3"),
        Padding(2),
        Flag("useNetwork"),
        Padding(24)
    ),
##    75: Struct("DefineFont3",
##        ULInt16("fontId"),
##        BitStruct("flags",
##            Flag("hasLayout"),
##            Flag("shiftJis"),
##            Flag("smallText"),
##            Flag("ansi"),
##            Flag("wideOffsets"),
##            Flag("wideCodes"),
##            Flag("italic"),
##            Flag("bold")
##        ),
##        LangCode,
##        PascalString("name"),
##        ULInt16("numGlyphs"),
##        IfThenElse("offsets", lambda ctx: ctx["flags"]["wideOffsets"],
##            Array(lambda ctx: ctx["numGlyphs"], ULInt32("offsets")),
##            Array(lambda ctx: ctx["numGlyphs"], ULInt16("offsets"))
##        ),
##        Array(lambda ctx: ctx["numGlyphs"], Shape("glyphs")),
##        Array(lambda ctx: ctx["numGlyphs"], ULInt16("codeTable")),
##        If(lambda ctx: ctx["flags"]["hasLayout"], Struct("layout",
##            Array(lambda ctx: ctx["_"]["numGlyphs"], SLInt16("advance")),
##            Array(lambda ctx: ctx["_"]["numGlyphs"], Rect("bounds")),
##            ULInt16("kerningCount"),
##            IfThenElse("kerning", lambda ctx: ctx["_"]["flags"]["wideCodes"],
##                Array(lambda ctx: ctx["kerningCount"], KerningRecord("kerning", ULInt16)),
##                Array(lambda ctx: ctx["kerningCount"], KerningRecord("kerning", ULInt8))
##            )
##        ))
##    ),
    76: Struct("SymbolClass",
        ULInt16("numSymbols"),
        Array(lambda ctx: ctx["numSymbols"],
            Struct("symbol",
                ULInt16("tag"),
                CString("name")
            )
        )
    ),
    77: Struct("Metadata",
        CString("xml")
    ),
    82: Struct("DoABC",
        ULInt32("flags"),
        CString("name"),
        GreedyField("abcData")
    ),

}

# SWF structure

def parseData(ctx):
    if ctx["type"] in tagTypes:
        return tagTypes[ctx["type"]].parse(ctx["_data"])
    else:
        return ctx["_data"]

header = Struct("header",
    Field("signature", 3),
    ULInt8("version"),
    ULInt32("fileLength"),
    Rect("frameSize"),
    ULInt16("frameRate"),
    ULInt16("frameCount")
)

tag = Struct("tag",
    ULInt16("typeAndLength"),
    Value("type", lambda ctx: ctx['typeAndLength'] >> 6),
    IfThenElse("length", lambda ctx: ctx['typeAndLength'] & 0x3f == 0x3f,
        SLInt32("length"),
        Value("length", lambda ctx: ctx['typeAndLength'] & 0x3f)
    ),
    Field("_data", lambda ctx: ctx['length']),
    Value("data", parseData)
)

# bunge in parse function that accomodates for compression
class SwfStruct(Struct):
    def parse_stream(self, data):
        hdr = header.parse_stream(data)
        if hdr.signature[0] == "C":
            import zlib
            data.seek(0)
            data = StringIO(data.read(8) + zlib.decompress(data.read()))
        return Struct.parse_stream(self, data)

swf = SwfStruct("swf",
    header,
    GreedyRange(tag)
)

# bytecode extraction method

def extract_bytecode(data):
    for tag in data['tag']:
        if tag['type'] == 82:
            yield tag['data']

# simple test

if __name__ == "__main__":
    data = swf.parse_stream(open('input/Test.swf', 'rb'))
    i = 0
    for code in extract_bytecode(data):
        i += 1
        out = open('code%d.abc' % i, 'wb')
        print('writing abc file %s to code%d.abc' % (tagData['name'], i))
        out.write(code)
        out.close()
