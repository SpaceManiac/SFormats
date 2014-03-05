# abcfile.py
# program: Adobe Flash
# contained inside .swf files
# AS3 bytecode file

import math, functools
from construct import *

# utility stuff

class PrintAnchor(Anchor):
    def _parse(self, stream, context):
        print "PrintAnchor(%s): %d" % (self.name, stream.tell())
        return stream.tell()

class DebugValue(Value):
    def _parse(self, stream, context):
        print "DebugValue(%s): %s" % (self.name, self.func(context))
        return self.func(context)

def PrintContext():
    return DebugValue("_printContext", lambda ctx: ctx)

def PrintContextItem(field):
    return DebugValue("_contextItem_" + field, lambda ctx: ctx["field"])

# abc-specific stuff

class VariableInteger(Construct):
    def _parse(self, stream, context):
        result = 0
        i = 0
        while True:
            byte = ord(stream.read(1))
            result += (byte & 0x7f) << i
            if byte < 0x80: break
            i += 7
        return result

    def _build(self, obj, stream, context):
        bits = int(math.ceil(math.log(obj + 1) / math.log(2) / 7))
        for i in range(bits):
            top = 0x00 if i == bits - 1 else 0x80
            val = obj >> (7 * i) & 0x7f
            stream.write(chr(val | top))

    def _sizeof(self, context):
        raise SizeofError("bad wolf")

class ULInt30Adapter(Adapter):
    def _encode(self, obj, context):
        return obj & ((1 << 30) - 1)
    def _decode(self, obj, context):
        return obj & ((1 << 30) - 1)

class PoolAdapter(Adapter):
    def __init__(self, zero, subcon):
        Adapter.__init__(self, subcon)
        self.zero = zero
    def _encode(self, obj, context):
        return ListContainer(obj[1:])
    def _decode(self, obj, context):
        return ListContainer([self.zero] + obj)

def ULInt30(name):
    return ULInt30Adapter(VariableInteger(name))

def U30Repeater(piece):
    name = "_%s_count" % piece.name
    return Embed(Struct("garbage", ULInt30(name), Array(lambda ctx: ctx[name], piece)))

def PoolRepeater(piece, zero = None):
    name = "_%s_count" % piece.name
    return Embed(Struct("garbage", ULInt30(name), PoolAdapter(zero, Array(lambda ctx: ctx[name] - 1, piece))))

# constant pool and other references

class Reference(object):
    def __init__(self, index, desc = None, resolve = None):
        self.index = index
        if resolve: self.resolve = resolve
        if desc: self.desc = desc
    def __repr__(self):
        return "<%s: %d>" % (self.desc, self.index)

class ConstantReference(Reference):
    def __init__(self, index, kind):
        Reference.__init__(self, index, "constant %s" % kind)
        self.kind = kind
    def resolve(self, abcFile, *args):
        if len(args) and self.index == 0: return args[0]
        try:
            return abcFile["constantPool"]["%ss" % self.kind][self.index]
        except:
            print self
            raise

class QuickReference(Reference):
    def __init__(self, index, array):
        Reference.__init__(self, index, array)
    def resolve(self, abcFile):
        return abcFile[self.desc][self.index]

class ReferenceAdapter(Adapter):
    def __init__(self, kind, boundargs, name):
        Adapter.__init__(self, ULInt30(name))
        self.kind = kind
        self.boundargs = boundargs
    def _encode(self, obj, context):
        return obj.index
    def _decode(self, obj, context):
        return self.kind(obj, *self.boundargs)

def BoundAdapter(reftype, *args):
    return functools.partial(ReferenceAdapter, reftype, args)

IntReference = BoundAdapter(ConstantReference, "int")
UIntReference = BoundAdapter(ConstantReference, "uint")
DoubleReference = BoundAdapter(ConstantReference, "double")
StringReference = BoundAdapter(ConstantReference, "string")
NamespaceReference = BoundAdapter(ConstantReference, "namespace")
NamespaceSetReference = BoundAdapter(ConstantReference, "namespaceSet")
MultinameReference = BoundAdapter(ConstantReference, "multiname")
MetadataReference = BoundAdapter(QuickReference, "metadata")
MethodReference = BoundAdapter(QuickReference, "methods")
ClassReference = BoundAdapter(QuickReference, "classes")

# constant pool

string = PascalString("strings", length_field = ULInt30("_string_len"))
namespace = Struct("namespaces",
    Enum(ULInt8("kind"),
        Namespace = 0x08,
        PackageNamespace = 0x16,
        PackageInternalNs = 0x17,
        ProtectedNamespace = 0x18,
        ExplicitNamespace = 0x19,
        StaticProtectedNs = 0x1A,
        PrivateNs = 0x05
    ),
    StringReference("name")
)
namespaceSet = Struct("namespaceSets",
    U30Repeater(NamespaceReference("namespaces"))
)
multiname = Struct("multinames",
    Enum(ULInt8("kind"),
        QName = 0x07,
        QNameA = 0x0D,
        RTQName = 0x0F,
        RTQNameA = 0x10,
        RTQNameL = 0x11,
        RTQNameLA = 0x12,
        Multiname = 0x09,
        MultinameA = 0x0E,
        MultinameL = 0x1B,
        MultinameLA = 0x1C
    ),
    Switch("data", lambda ctx: ctx["kind"].replace('A', ''), {
        "QName": Struct("data", NamespaceReference("namespace"), StringReference("name")),
        "RTQName": Struct("data", StringReference("name")),
        "RTQNameL": Struct("data"),
        "Multiname": Struct("data", StringReference("name"), NamespaceSetReference("namespaceSet")),
        "MultinameL": Struct("data", NamespaceSetReference("namespaceSet"))
    })
)

constantPool = Struct("constantPool",
    PoolRepeater(VariableInteger("ints"), 0),
    PoolRepeater(VariableInteger("uints"), 0),
    PoolRepeater(LFloat64("doubles"), 0),
    PoolRepeater(string, ""),
    PoolRepeater(namespace),
    PoolRepeater(namespaceSet),
    PoolRepeater(multiname)
)

# method signature

constantKind = Enum(ULInt8("kind"),
    Int = 0x03,
    UInt = 0x04,
    Double = 0x06,
    Utf8 = 0x01,
    True = 0x0B,
    False = 0x0A,
    Null = 0x0C,
    Undefined = 0x00,
    Namespace = 0x08,
    PackageNamespace = 0x16,
    PackageInternalNs = 0x17,
    ProtectedNamespace = 0x18,
    ExplicitNamespace = 0x19,
    StaticProtectedNs = 0x1A,
    PrivateNs = 0x05
)
options = Struct("options",
    ULInt30("value"),
    constantKind
)
methodSignature = Struct("methods",
    ULInt30("paramCount"),
    MultinameReference("returnType"),
    MetaRepeater(lambda ctx: ctx["paramCount"], MultinameReference("paramTypes")),
    StringReference("name"),
    BitStruct("flags",
        Flag("hasParamNames"),
        Flag("usesDxns"),
        Padding(2),
        Flag("hasOptional"),
        Flag("needRest"),
        Flag("needActivation"),
        Flag("needArguments")
    ),
    If(lambda ctx: ctx["flags"]["hasOptional"],
        U30Repeater(options)
    ),
    If(lambda ctx: ctx["flags"]["hasParamNames"],
        MetaRepeater(lambda ctx: ctx["paramCount"], StringReference("paramNames"))
    )
)

# metadata

metadataItem = Struct("items",
    StringReference("key"),
    StringReference("value")
)
metadata = Struct("metadata",
    StringReference("name"),
    U30Repeater(metadataItem)
)

# traits

slotTrait = Struct("slotTrait",
    ULInt30("slotId"),
    MultinameReference("typeName"),
    ULInt30("vIndex"),
    If(lambda ctx: ctx["vIndex"] > 0,
        constantKind
    )
)
classTrait = Struct("classTrait",
    ULInt30("slotId"),
    ClassReference("class")
)
functionTrait = Struct("functionTrait",
    ULInt30("slotId"),
    MethodReference("function")
)
methodTrait = Struct("methodTrait",
    ULInt30("dispId"),
    MethodReference("method")
)
trait = Struct("traits",
    MultinameReference("name"),
    #PrintAnchor("position"),
    #DebugValue("name", lambda ctx: ctx["name"]),
    #DebugValue("strName", lambda ctx: ctx["_"]["_"]["constantPool"]["strings"][ctx["name"] - 1]),
    BitStruct("attributes",
        Padding(1),
        Flag("metadata"),
        Flag("override"),
        Flag("final"),
        Enum(Nibble("_kind"),
            Slot = 0,
            Method = 1,
            Getter = 2,
            Setter = 3,
            Class = 4,
            Function = 5,
            Const = 6,
        ),
    ),
    Value("kind", lambda ctx: ctx["attributes"]["_kind"]),
    Switch("data", lambda ctx: ctx["kind"], {
        "Slot": slotTrait,
        "Method": methodTrait,
        "Getter": methodTrait,
        "Setter": methodTrait,
        "Class": classTrait,
        "Function" : functionTrait,
        "Const": slotTrait
    }),
    If(lambda ctx: ctx["attributes"]["metadata"],
        U30Repeater(MetadataReference("metadata"))
    )
)

# instances - nonstatic attributes of classes

instance = Struct("instances",
    MultinameReference("name"),
    MultinameReference("superName"),
    BitStruct("flags",
        Padding(4),
        Flag("protectedNamespace"),
        Flag("interface"),
        Flag("final"),
        Flag("sealed")
    ),
    If(lambda ctx: ctx["flags"]["protectedNamespace"],
        NamespaceReference("protectedNamespace"),
    ),
    U30Repeater(MultinameReference("interfaces")),
    MethodReference("iinit"),
    U30Repeater(trait)
)

# classes - static attributes of classes

classInfo = Struct("classes",
    MethodReference("cinit"),
    U30Repeater(trait)
)

# scripts

script = Struct("scripts",
    MethodReference("init"),
    U30Repeater(trait)
)

# method body

exception = Struct("exceptions",
    ULInt30("from"),
    ULInt30("to"),
    ULInt30("target"),
    ULInt30("exceptionType"),
    ULInt30("variableName")
)
methodBody = Struct("methodBodies",
    MethodReference("method"),
    ULInt30("maxStack"),
    ULInt30("localCount"),
    ULInt30("initScopeDepth"),
    ULInt30("maxScopeDepth"),
    U30Repeater(ULInt8("_code")),
    Value("code", lambda ctx: "".join(chr(x) for x in ctx["_code"])),
    U30Repeater(exception),
    U30Repeater(trait)
)

# bring it all together

abcfile = Struct("abcfile",
    ULInt16("minor_version"),
    ULInt16("major_version"),
    constantPool,
    U30Repeater(methodSignature),
    U30Repeater(metadata),
    ULInt30("class_len"),
    MetaRepeater(lambda ctx: ctx["class_len"], instance),
    MetaRepeater(lambda ctx: ctx["class_len"], classInfo),
    U30Repeater(script),
    U30Repeater(methodBody),
    #PrintAnchor("end")
)

if __name__ == "__main__":
    from sformats.flash.swf import swf, extract_bytecode

    flash = swf.parse_stream(open('output/Test.swf', 'rb'))
    code = None
    for c in extract_bytecode(flash):
        code = c
        break

    data = abcfile.parse(code)

    # parse methods
    from avm2 import avm2code
    for body in data['methodBodies']:
        body['code'] = avm2code.parse(body['code'])

    out = open("output/code.txt", "w")
    out.write(str(data))
    out.close()
