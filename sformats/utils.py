# utils.py
# common utilities for structures below

from construct import *

# constructs

class MysteryCounter():
	def __init__(self):
		self.num = 0
	def __call__(self, len):
		self.num += 1
		return Field("mystery_%d" % self.num, len)
	def Finish(self):
		self.num += 1
		return FinishAdapter(OptionalGreedyRange(Field("mystery_%d" % self.num, 1)))
		
class FinishAdapter(Adapter):
	def _decode(self, obj, ctx):
		return ''.join(obj)
	def _encode(self, obj, ctx):
		return list(obj)

class WithContext(Construct):
	def __init__(self, func):
		Construct.__init__(self, "_WithContext")
		self.func = func
	def _parse(self, stream, context):
		self.func(context)

class NullTerminateAdapter(Adapter):
	def _encode(self, obj, ctx):
		return obj
	def _decode(self, obj, ctx):
		idx = obj.find('\x00')
		if idx >= 0:
			return obj[:idx]
		else:
			return obj

def PrintContext():
	return WithContext(print)

def PrintContextItem(field):
	return WithContext(lambda ctx: print(ctx[field]))

def PackedString(name, len=32):
	return NullTerminateAdapter(String(name, len, padchar="\x00"))


