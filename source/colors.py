#colors.py
#A part of NonVisual Desktop Access (NVDA)
#Copyright (C) 2006-2008 NVDA Contributors <http://www.nvda-project.org/>
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

from collections import namedtuple
import math
import colorsys
from ctypes.wintypes import COLORREF
import re

class RGB(namedtuple('RGB',('red','green','blue'))):
	"""Represents a color as an RGB (red green blue) value"""

	@classmethod
	def fromCOLORREF(cls,c):
		"""factory method to create an RGB from a COLORREF ctypes instance"""
		if isinstance(c,COLORREF):
			c=c.value
		return cls(c&0xff,(c>>8)&0xff,(c>>16)&0xff)

	_re_RGBFunctionString=re.compile(r'rgb\(\s*(\d+%?)\s*,\s*(\d+%?)\s*,\s*(\d+%?)\s*\)',re.I)
	_re_RGBAFunctionString=re.compile(r'rgba\(\s*(\d+%?)\s*,\s*(\d+%?)\s*,\s*(\d+%?)\s*,\s*\d+(\.\d+)?\s*\)',re.I)

	@staticmethod
	def _RGBStringValToInt(s):
		val=int(round(int(s[:-1])*2.55)) if s.endswith('%') else int(s)
		if val<0 or val>255:
			raise ValueError("%s out of range"%val)
		return val

	@classmethod
	def fromString(cls,s):
		"""
		Factory method to create an RGB instance from a css RGB string representation.
		"""
		s=s.strip()
		#Try to match on the form RGB(x,y,z)
		m=cls._re_RGBFunctionString.match(s) or cls._re_RGBAFunctionString.match(s)
		if m:
			r=cls._RGBStringValToInt(m.group(1))
			g=cls._RGBStringValToInt(m.group(2))
			b=cls._RGBStringValToInt(m.group(3))
			return RGB(r,g,b)
		if s.startswith('#'):
			sLen=len(s)
			try:
				val=int(s[1:],16)
			except ValueError:
				val=None
			if val is not None:
				#Perhaps its a #aarrggbb or #rrggbb hex string
				if sLen==7 or sLen==9:
					r=(val>>16)&0xff
					g=(val>>8)&0xff
					b=val&0xff
					return RGB(r,g,b)
				#Perhaps its a #argb or #rgb hex string
				if sLen==4 or sLen==5:
					r=((val>>8)&0xf)+(((val>>8)&0xf)<<4)
					g=((val>>4)&0xf)+(((val>>4)&0xf)<<4)
					b=(val&0xf)+((val&0xf)<<4)
					return RGB(r,g,b)
		raise ValueError("invalid RGB string: %s"%s)

	@property
	def name(self):
		foundName=RGBToNamesCache.get(self,None)
		if foundName:
			return foundName
		# convert to hsv (hue, saturation, value)
		h,s,v=colorsys.rgb_to_hsv(self.red/255.0,self.green/255.0,self.blue/255.0)
		h=int(h*360)
		sv=s*v
		if sv<0.05:
			# There is not enough saturation to perceive a hue, therefore its on the scale from black to white.
			closestName=shadeNames[int(round((len(shadeNames)-1)*(1-v)))]
		else:
			# Find the closest named hue (red, orange, yellow...)
			# or a paile, dark or paile dark variation
			nh=min((x for x in colorNamesByHue),key=lambda x: abs(x-h))
			hueShadeNames=colorNamesByHue[nh][int(s<=0.5)]
			closestName=hueShadeNames[int(round((len(hueShadeNames)-1)*(1-v)))]
		RGBToNamesCache[self]=closestName
		return closestName

RGBToNamesCache={}

# a dictionary whos keys are hues in degrees, and values are:
# a 2d array containing labels for normal and dark, and also pale versions of all of these 
# the names should only be variations on well-understood hues (red orange yellow green aqua blue purple pink)  and brown (dark orange)
colorNamesByHue={
	0:[['red','dark red'],['pale red','pale dark red']],
	15:[['red-orange','red-brown','dark red-brown'],['pale red-orange','pale red-brown','pale dark red-brown']],
	30:[['orange','brown','dark brown'],['pale orange','pale brown','pale dark brown']],
	45:[['orange-yellow','brown-yellow','dark brown-yellow'],['pale orange-yellow','pale brown-yellow','pale dark brown-yellow']],
	60:[['yellow','dark yellow'],['pale yellow','pale dark yellow']],
	90:[['yellow-green','dark yellow-green'],['pale yellow-green','pale dark yellow-green']],
	120:[['green','dark green'],['pale green','pale dark green']],
	150:[['green-aqua','dark green-aqua'],['pale green-aqua','pale dark green-aqua']],
	180:[['aqua','dark aqua'],['pale aqua','pale dark aqua']],
	210:[['aqua-blue','dark aqua-blue'],['pale aqua-blue','pale dark aqua-blue']],
	240:[['blue','dark blue'],['pale blue','pale dark blue']],
	263:[['blue-purple','dark blue-purple'],['pale blue-purple','pale dark blue-purple']],
	285:[['purple','dark purple'],['pale purple','pale dark purple']],
	300:[['purple-pink','dark purple-pink'],['pale purple-pink','pale dark purple-pink']],
	315:[['pink','dark pink'],['pale pink','pale dark pink']],
	338:[['pink-red','dark pink-red'],['pale pink-red','pale dark pink-red']],
}

shadeNames=['white','light grey','grey','dark grey','black']

