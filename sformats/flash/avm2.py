# avm2.py
# program 
# ActionScript VM 2 bytecode instructions
# defines structure of AVM2 bytecode instructions

from construct import *
from sformats.flash.abcfile import ULInt30, ConstantReference

# helper type thingumies

class SLInt24Adapter(Adapter):
    def _encode(self, obj, context):
        if obj < 0: obj = 0x1000000 + obj
        return ULInt32("").build(obj)[:3]
    def _decode(self, obj, context):
        num = ULInt32("").parse(obj + '\x00')
        if num > 0x800000: num = num - 0x1000000
        return num

def SLInt24(name):
    return SLInt24Adapter(Field(name, 3))

# all the instructions
instructions = {}
translations = {}
def instr(opcode, name, *args, **kwargs):
    instructions[opcode] = Struct(name, *args)
    if "trs" in kwargs:
        trans = kwargs["trs"]
        if callable(trans):
            translations[opcode] = trans
        else:
            translations[opcode] = lambda instr: trans
        translations[name] = translations[opcode]

def resolve(text, kind): return lambda instr: text % "<%s=%d>" % (kind, instr["index"])
def jumper(text): return lambda instr: "jump[%d] if %s" % (instr["offset"], text)
def runtimeMultiname(text, before, after = 0): return lambda instr: text % "<rt_multiname=%d,%d,%d>" % (instr["index"], before, after)

def debug(instr):
    if instr["debugType"] == 1:
        return "// register %d is named <string=%d>" % (instr["register"], instr["index"])
    else:
        return "// unknown debug type %d" % instr["debugType"]

# basic stuff
instr(0x02, "nop", trs = "// nop")
instr(0x03, "throw", trs = "throw := pop[0]")
instr(0x04, "getsuper", ULInt30("index"), trs = runtimeMultiname("push := getsuper(%s)", 1))
instr(0x05, "setsuper", ULInt30("index"), trs = runtimeMultiname("super(%s) := pop[0]", 1, 1))
instr(0x06, "dxns", ULInt30("index"), trs = resolve("xmlnamespace := \"%s\"", "string"))
instr(0x07, "dxnslate", trs = "xmlnamespace := pop[0]")
instr(0x08, "kill", ULInt30("index"), trs = lambda instr: "locals[%d] := undefined" % instr["index"])
instr(0x09, "label", trs = "// label")

# jumps
instr(0x0c, "ifnlt", SLInt24("offset"), trs = jumper("pop[1] >= /*N*/ pop[0]"))
instr(0x0d, "ifnle", SLInt24("offset"), trs = jumper("pop[1] > /*N*/ pop[0]"))
instr(0x0e, "ifngt", SLInt24("offset"), trs = jumper("pop[1] <= /*N*/ pop[0]"))
instr(0x0f, "ifnge", SLInt24("offset"), trs = jumper("pop[1] < /*N*/ pop[0]"))
instr(0x10, "jump", SLInt24("offset"), trs = lambda instr: "jump[%d]" % instr["offset"])
instr(0x11, "iftrue", SLInt24("offset"), trs = jumper("pop[1]"))
instr(0x12, "iffalse", SLInt24("offset"), trs = jumper("!pop[0]"))
instr(0x13, "ifeq", SLInt24("offset"), trs = jumper("pop[1] == pop[0]"))
instr(0x14, "ifne", SLInt24("offset"), trs = jumper("pop[1] != pop[0]"))
instr(0x15, "iflt", SLInt24("offset"), trs = jumper("pop[1] < pop[0]"))
instr(0x16, "ifle", SLInt24("offset"), trs = jumper("pop[1] <= pop[0]"))
instr(0x17, "ifgt", SLInt24("offset"), trs = jumper("pop[1] > pop[0]"))
instr(0x18, "ifge", SLInt24("offset"), trs = jumper("pop[1] >= pop[0]"))
instr(0x19, "ifstricteq", SLInt24("offset"), trs = jumper("pop[1] === pop[0]"))
instr(0x1a, "ifstrictne", SLInt24("offset"), trs = jumper("pop[1] !== pop[0]"))
instr(0x1b, "lookupswitch", SLInt24("offset"), ULInt30("caseCount"), Array(lambda ctx: 1 + ctx["caseCount"], SLInt24("caseOffsets"))) #***

# stack operations
instr(0x1c, "pushwith", trs = "pushscope := with(pop[0])")
instr(0x1d, "popscope", trs = "popscope[0]")
instr(0x1e, "nextname", trs = "push := nextname(pop[1], pop[0])")
instr(0x1f, "hasnext", trs = "push := nextproperty(pop[1], pop[0])")
instr(0x20, "pushnull", trs = "push := null")
instr(0x21, "pushundefined", trs = "push := undefined")
instr(0x23, "nextvalue", trs = "push := nextvalue(pop[1], pop[0])")
instr(0x24, "pushbyte", ULInt8("value"), trs = lambda instr: "push := %d" % instr["value"])
instr(0x25, "pushshort", ULInt30("value"), trs = lambda instr: "push := %d" % instr["value"])
instr(0x26, "pushtrue", trs = "push := true")
instr(0x27, "pushfalse", trs = "push := false")
instr(0x28, "pushnan", trs = "push := nan")
instr(0x29, "pop", trs = "pop[0]")
instr(0x2a, "dup", trs = "push := peek[0]")
instr(0x2b, "swap", trs = "swap")
instr(0x2c, "pushstring", ULInt30("index"), trs = resolve("push := %s", "string"))
instr(0x2d, "pushint", ULInt30("index"), trs = resolve("push := %s", "int"))
instr(0x2e, "pushuint", ULInt30("index"), trs = resolve("push := %s", "uint"))
instr(0x2f, "pushdouble", ULInt30("index"), trs = resolve("push := %s", "double"))
instr(0x30, "pushscope", trs = "pushscope := pop[0]")
instr(0x31, "pushnamespace", ULInt30("index"), trs = resolve("push := %s", "namespace"))
instr(0x32, "hasnext2", ULInt30("object"), ULInt30("index"), trs = lambda instr: "push := nextpropertyref(locals[%d], locals[%d])" % (instr["object"], instr["index"]))

# method and constructor calls
instr(0x40, "newfunction", ULInt30("index")) # todo
instr(0x41, "call", ULInt30("argCount")) # handled
instr(0x42, "construct", ULInt30("argCount")) # handled
instr(0x43, "callmethod", ULInt30("index"), ULInt30("argCount")) # handled
instr(0x44, "callstatic", ULInt30("index"), ULInt30("argCount")) # handled
instr(0x45, "callsuper", ULInt30("index"), ULInt30("argCount")) # handled
instr(0x46, "callproperty", ULInt30("index"), ULInt30("argCount")) # handled
instr(0x47, "returnvoid", trs = "return := void")
instr(0x48, "returnvalue", trs = "return := pop[0]")
instr(0x49, "constructsuper", ULInt30("argCount")) # handled
instr(0x4a, "constructprop", ULInt30("index"), ULInt30("argCount")) # handled
instr(0x4c, "callproplex", ULInt30("index"), ULInt30("argCount")) # handled
instr(0x4e, "callsupervoid", ULInt30("index"), ULInt30("argCount")) # handled
instr(0x4f, "callpropvoid", ULInt30("index"), ULInt30("argCount")) # handled
instr(0x55, "newobject", ULInt30("argCount")) # todo
instr(0x56, "newarray", ULInt30("argCount")) # todo
instr(0x57, "newactivation", trs = "push := newactivation")
instr(0x58, "newclass", ULInt30("index")) # todo
instr(0x59, "getdescendants", ULInt30("index"), trs = runtimeMultiname("push := getdescendants(%s)", 1))
instr(0x5a, "newcatch", ULInt30("index")) # todo
instr(0x5d, "findpropstrict", ULInt30("index"), trs = runtimeMultiname("push := findpropstrict(%s)", 0))
instr(0x5e, "findproperty", ULInt30("index"), trs = runtimeMultiname("push := findproperty(%s)", 0))
instr(0x60, "getlex", ULInt30("index"), trs = resolve("push := %s", "multiname"))
instr(0x61, "setproperty", ULInt30("index"), trs = runtimeMultiname("property(%s) := pop[0]", 1, 1))
instr(0x62, "getlocal", ULInt30("index"), trs = lambda instr: "push := locals[%d]" % instr["index"])
instr(0x63, "setlocal", ULInt30("index"), trs = lambda instr: "locals[%d] := pop[0]" % instr["index"])
instr(0x64, "getglobalscope", trs = "push := globalscope")
instr(0x65, "getscopeobject", ULInt30("index"), trs = lambda instr: "push := scope[%d]" % instr["index"])
instr(0x66, "getproperty", ULInt30("index"), trs = runtimeMultiname("push := property(%s)", 1))
instr(0x68, "initproperty", ULInt30("index"), trs = runtimeMultiname("property(%s) := pop[0]", 1, 1)) #***
instr(0x6a, "deleteproperty", ULInt30("index"), trs = runtimeMultiname("push := deleteproperty(%s)", 1))
instr(0x6c, "getslot", ULInt30("index"), trs = lambda instr: "push := pop[0].slot[%d]" % instr["index"])
instr(0x6d, "setslot", ULInt30("index"), trs = lambda instr: "pop[1].slot[%d] := pop[0]" % instr["index"])
instr(0x6e, "getglobalslot", ULInt30("index"), trs = lambda instr: "push := globals[%d]" % instr["index"])
instr(0x6f, "setglobalslot", ULInt30("index"), trs = lambda instr: "globals[%d] := pop[0]" % instr["index"])
instr(0x70, "convert_s", trs = "push := (String) pop[0]")
instr(0x71, "esc_xelemn", trs = "push := xmlelement(pop[0])")
instr(0x72, "esc_xattr", trs = "push := xmlattribute(pop[0])")
instr(0x73, "convert_i", trs = "push := (int) pop[0]")
instr(0x74, "convert_u", trs = "push := (uint) pop[0]")
instr(0x75, "convert_d", trs = "push := (Number) pop[0]")
instr(0x76, "convert_b", trs = "push := (Boolean) pop[0]")
instr(0x77, "convert_o", trs = "push := (Object) pop[0]")
instr(0x78, "checkfilter", trs = "checkfilter := peek[0]")
instr(0x80, "coerce", ULInt30("index"), trs = resolve("push := (%s) pop[0]", "multiname"))
instr(0x82, "coerce_a", trs = "push := pop[0]")
instr(0x85, "coerce_s", trs = "push := (String) pop[0]")
instr(0x86, "astype", ULInt30("index"), trs = resolve("push := astype(%s, pop[0])", "multiname")) #***
instr(0x87, "astypelate", trs = "push := (pop[0]) pop[1]")
instr(0x90, "negate", trs = "push := -pop[0]")
instr(0x91, "increment", trs = "push := pop[0] + 1")
instr(0x92, "inclocal", ULInt30("index"), trs = lambda instr: "local[%d] := local[%d] + 1" % (instr["index"], instr["index"]))
instr(0x93, "decrement", trs = "push := pop[0] - 1")
instr(0x94, "declocal", ULInt30("index"))

# math and other operations
instr(0x95, "typeof", trs = "push := typeof(pop[0])")
instr(0x96, "not", trs = "push := !pop[0]")
instr(0x97, "bitnot", trs = "push := ~pop[0]")
instr(0xa0, "add", trs = "push := pop[1] + pop[0]")
instr(0xa1, "subtract", trs = "push := pop[1] - pop[0]")
instr(0xa2, "multiply", trs = "push := pop[1] * pop[0]")
instr(0xa3, "divide", trs = "push := pop[1] / pop[0]")
instr(0xa4, "modulo", trs = "push := pop[1] % pop[0]")
instr(0xa5, "lshift", trs = "push := pop[1] << pop[0]")
instr(0xa6, "rshift", trs = "push := pop[1] >> pop[0]")
instr(0xa7, "urshift", trs = "push := pop[1] >>> pop[0]")
instr(0xa8, "bitand", trs = "push := pop[0] & pop[1]")
instr(0xa9, "bitor", trs = "push := pop[0] | pop[1]")
instr(0xaa, "bitxor", trs = "push := pop[0] ^ pop[1]")
instr(0xab, "equals", trs = "push := pop[0] == pop[1]")
instr(0xac, "strictequals", trs = "push := pop[1] === pop[0]")
instr(0xad, "lessthan", trs = "push := pop[1] < pop[0]")
instr(0xae, "lessequals", trs = "push := pop[1] <= pop[0]")
instr(0xaf, "greaterthan", trs = "push := pop[1] > pop[0]")
instr(0xb0, "greaterequals", trs = "push := pop[1] >= pop[0]")  # AVM2 spec lists greaterequals as 0xaf, likely an error; 0xb0 is inferred
instr(0xb1, "instanceof", trs = "push := pop[1] instanceof pop[0]")
instr(0xb2, "istype", ULInt30("index"), trs = resolve("push := pop[0] istype %s", "multiname"))
instr(0xb3, "istypelate", trs = "push := pop[1] istype pop[0]")
instr(0xb4, "in", trs = "push := pop[1] in pop[0]")
instr(0xc0, "increment_i", trs = "push := pop[0] + 1")
instr(0xc1, "decrement_i", trs = "push := pop[0] - 1")
instr(0xc2, "inclocal_i", ULInt30("index"), trs = lambda instr: "local[%d] := local[%d] + 1" % (instr["index"], instr["index"]))
instr(0xc3, "declocal_i", ULInt30("index"), trs = lambda instr: "local[%d] := local[%d] - 1" % (instr["index"], instr["index"]))
instr(0xc4, "negate_i", trs = "push := -pop[0]")
instr(0xc5, "add_i", trs = "push := pop[1] + pop[0]")
instr(0xc6, "subtract_i", trs = "push := pop[1] - pop[0]")
instr(0xc7, "multiply_i", trs = "push := pop[1] * pop[0]")

# shortcut local accessors and debug instructions
for n in range(4): instr(0xd0 + n, "getlocal_%d" % n, trs = "push := locals[%d]" % n)
for n in range(4): instr(0xd4 + n, "setlocal_%d" % n, trs = "locals[%d] := pop[0]" % n)
instr(0xef, "debug", ULInt8("debugType"), ULInt30("index"), ULInt8("register"), ULInt30("extra"), trs = debug)
instr(0xf0, "debugline", ULInt30("linenum"), trs = lambda instr: "// *line %d" % instr["linenum"])
instr(0xf1, "debugfile", ULInt30("index"), trs = resolve("// file %s", "string"))

# bring it all together

def lookupName(opcode):
    if opcode in instructions:
        return instructions[opcode].name
    else:
        return "?? [%s]" % hex(opcode)

instruction = Struct("instructions",
    Anchor("codePos"),
    ULInt8("opcode"),
    Value("optype", lambda ctx: lookupName(ctx["opcode"])),
    Embed(Switch("data", lambda ctx: ctx["opcode"], instructions))
)

avm2code = GreedyRange(instruction)
