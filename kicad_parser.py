#!/usr/bin/env python3
import sys
from pprint import pp
from collections import defaultdict
import glom

def parse_tokens(file):
	"""generator that iterates over all tokens inside given stream"""
	s=""
	while True:
		c=file.read(1)
		if c=="":
			if s != "":
				yield s
				s=""
			break
		if c in '() \n':
			# special character inside of a string
			if s != "" and s[0] == '"':
				s+=c
				continue
			# special character means previous token is over
			if s != "":
				yield s;
				s=""
			if c in '()':
				yield c
			continue
		if c == '"':
			# are we inside a string already? then send that string
			if s != "" and s[0]=='"':
				s+=c
				yield s
				s=""
				continue
			# starting a new string
			if s == "":
				s+=c
				continue
			else:
				raise Exception("Parse error: cannot have \" inside string")
		#continuing the previous token
		s += c

def empty_list():
	return []

def parser(tokens, nxt=None):
	token=nxt if nxt else next(tokens)
	values = []
	if token != '(':
		raise Exception(f"Parse error: expected (, got {token}")
	
	while True:
		nxt=next(tokens)
		if nxt == ')':
			if len(values) <= 1:
				raise Exception(f"Don't know how to parse less than 1 token")
			if len(values) == 2:
				return {values[0]: values[1]}
			else:
				# if all we have is strings, we return an array of strings in a dict
				# we have exceptions for some weirdly formated values
				if values[0] in ("module",):
					if not isinstance(values[1], str):
						print(f"Expected str in {values[0]}")
					values[1] = {"name":values[1]}
				for v in values[1:]:
					if isinstance(v, str):
						#print(f"We are in {values[0]}, returning list of strings")
						return {values[0]:values[1:]}
				# we have a list of objects. It may be better to create a coalesced dict rather
				# than a list.
				vdict={}
				vlist=defaultdict(empty_list)

				for v in values[1:]:
					k=v.keys()
					if len(k) != 1:
						print("How to parse k?", k)
					k=list(k)[0]
					if k in ("net", "add_net", "module", "segment", "via", "xy", "zone", "fp_line", "gr_text", "gr_line", "filled_polygon", "pad", "fp_text", "fp_circle"):
						#special treatment, they are to be counted as list, not dicts
						#continue #remove me
						vlist[k].append(v[k])
					else:
						if k in vdict.keys():
							print(f"Duplicate key for {k}")
						vdict[k]=v[k]
				#pp(vdict)
				#pp(vlist)
				vdict.update(vlist)
				return {values[0]:vdict}
		elif nxt == '(':
			values.append(parser(tokens, nxt))
		else:
			values.append(nxt)

def parse(filename):
	with open(filename, "r") as f:
		t=parse_tokens(f)
		p=parser(t)
	return p


def main(args):
	p=parse(args[0])
	print(glom.glom(p, "kicad_pcb.general.drawings"))
	#pp(p)

if __name__=="__main__":
	main(sys.argv[1:])
