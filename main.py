from consts import *

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import QXmlStreamReader, pyqtSignal, QObject

from functools import partial

from rtmidi import MidiIn as rtMidiIn

from phue import Bridge

#import faulthandler; faulthandler.enable()

# Philips Hue Inegration Parameters
PHUE_BRIDGE_IP = "192.168.2.44"
PHUE_LIGHT_1 = "Hue color lamp 1"
PHUE_LIGHT_2 = "Hue color lamp 2"
PHUE_LIGHT_3 = "Hue Downlight 1"
PHUE_LIGHT_4 = "Hue color downlight 1"

class SVG:
	def __init__(self, code, inverted=False):
		self.code = code
		self.args = self.code.count("%s")
		self.inverted = inverted

	def getArgs(self, text):
		return tuple([text for i in range(self.args)])

	def get(self, night=False):
		if(self.inverted):
			night = not night
		return self.code % self.getArgs("white" if night else "black")

VECTORS = {
	"VOLUME": SVG('<svg><g id="VOLUME"><path d="M16.875,0c9.314,0 16.875,7.561 16.875,16.875c0,9.314 -7.561,16.875 -16.875,16.875c-9.314,0 -16.875,-7.561 -16.875,-16.875c0,-9.314 7.561,-16.875 16.875,-16.875Zm-6.098,18.826c2.289,0 4.147,1.858 4.147,4.147c0,2.289 -1.858,4.147 -4.147,4.147c-2.289,0 -4.147,-1.858 -4.147,-4.147c0,-2.289 1.858,-4.147 4.147,-4.147Z" style="fill:%s;fill-opacity:0.5;"/></g></svg>', 1),
	"SPEAKER": SVG('<svg><g id="OP1_KEY4"><circle r="40" style="fill:%s;fill-opacity:0.15;"/></g></svg>'),
	OP1_ARROW_DOWN_BUTTON: SVG('<svg><g id="OP1_ARROW_DOWN_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><g><path d="M11.136,18.027l11.478,0m-5.739,-2.318l0,-7.726m5.408,2.87l-5.408,4.856l-5.298,-4.856" style="fill:none;fill-rule:nonzero;stroke:rgb(241,89,36);stroke-width:0.75px;"/><path d="M18.31,24.539c-0.111,0.772 -0.773,1.324 -1.545,1.214c-0.773,-0.11 -1.325,-0.773 -1.214,-1.435l0,-0.11c0.11,-0.773 0.772,-1.325 1.545,-1.214c0.772,0.11 1.324,0.772 1.214,1.545Z" style="fill:none;stroke:%s;stroke-width:0.75px;"/></g></g></svg>'),
	OP1_ARROW_UP_BUTTON: SVG('<svg><g id="OP1_ARROW_UP_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><g><path d="M10.866,16.901l11.478,0m-5.739,-10.044l0,7.836m-5.408,-2.98l5.408,-4.856l5.408,4.856" style="fill:none;fill-rule:nonzero;stroke:rgb(241,89,36);stroke-width:0.75px;"/><path d="M23.448,24.185l-5.298,0l3.974,-3.752l0,5.297" style="fill:none;stroke:%s;stroke-width:0.75px;stroke-linejoin:miter;stroke-miterlimit:1.5;"/><path d="M11.086,20.433l0,5.297" style="fill:none;stroke:%s;stroke-width:0.75px;stroke-linejoin:miter;stroke-miterlimit:1.5;"/><path d="M12.852,23.302l3.974,0" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/></g></g></svg>'),
	OP1_COM: SVG('<svg><g id="OP1_COM"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><path d="M19.469,26.257l0,-5.298l0.22,0l1.215,3.201l0.22,0l1.214,-3.201l0.221,0l0,5.298" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><path d="M13.84,24.822c0,0.772 -0.662,1.324 -1.325,1.324c-0.772,0 -1.324,-0.662 -1.324,-1.324l0,-2.76c0,-0.772 0.662,-1.324 1.324,-1.324c0.773,0 1.325,0.662 1.325,1.324" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><path d="M15.054,22.283l0,2.428c0,0.883 0.662,1.546 1.545,1.546c0.883,0 1.545,-0.663 1.545,-1.546l0,-2.428c0,-0.883 -0.662,-1.545 -1.545,-1.545c-0.883,0 -1.545,0.662 -1.545,1.545Z" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><circle cx="16.709" cy="12.239" r="4.746" style="fill:none;stroke:%s;stroke-width:0.75px;"/><path d="M15.275,12.239c0,-0.772 0.662,-1.434 1.434,-1.434c0.773,0 1.435,0.662 1.435,1.434c0,0.773 -0.662,1.435 -1.435,1.435c-0.772,0 -1.434,-0.662 -1.434,-1.435Z" style="fill:none;stroke:%s;stroke-width:0.75px;"/></g></svg>'),
	OP1_ENCODER_1: SVG('<svg><g id="OP1_ENCODER_1"><circle cx="24" cy="24" r="24" style="fill:%s;fill-opacity:0.05;"/><circle cx="24" cy="24" r="16.875" style="fill:rgb(36,174,255);"/><path d="M19.63,33.126l0,-18.252c0,-2.443 1.928,-4.371 4.37,-4.371c2.442,0 4.37,1.928 4.37,4.371l0,18.252c0,2.443 -1.928,4.371 -4.37,4.371c-2.442,0 -4.37,-1.928 -4.37,-4.371Z" style="fill-opacity:0.2;"/></g></svg>'),
	OP1_ENCODER_2: SVG('<svg><g id="OP1_ENCODER_2"><circle cx="24" cy="24" r="24" style="fill:%s;fill-opacity:0.05;"/><circle cx="24" cy="24" r="16.875" style="fill:rgb(27,180,83));"/><path d="M19.63,33.126l0,-18.252c0,-2.443 1.928,-4.371 4.37,-4.371c2.442,0 4.37,1.928 4.37,4.371l0,18.252c0,2.443 -1.928,4.371 -4.37,4.371c-2.442,0 -4.37,-1.928 -4.37,-4.371Z" style="fill-opacity:0.2;"/></g></svg>'),
	OP1_ENCODER_3: SVG('<svg><g id="OP1_ENCODER_3"><circle cx="24" cy="24" r="24" style="fill:%s;fill-opacity:0.05;"/><circle cx="24" cy="24" r="16.875" style="fill:rgb(255,255,255);"/><path d="M19.63,33.126l0,-18.252c0,-2.443 1.928,-4.371 4.37,-4.371c2.442,0 4.37,1.928 4.37,4.371l0,18.252c0,2.443 -1.928,4.371 -4.37,4.371c-2.442,0 -4.37,-1.928 -4.37,-4.371Z" style="fill-opacity:0.2;"/></g></svg>'),
	OP1_ENCODER_4: SVG('<svg><g id="OP1_ENCODER_4"><circle cx="24" cy="24" r="24" style="fill:%s;fill-opacity:0.05;"/><circle cx="24" cy="24" r="16.875" style="fill:rgb(241,89,36);"/><path d="M19.63,33.126l0,-18.252c0,-2.443 1.928,-4.371 4.37,-4.371c2.442,0 4.37,1.928 4.37,4.371l0,18.252c0,2.443 -1.928,4.371 -4.37,4.371c-2.442,0 -4.37,-1.928 -4.37,-4.371Z" style="fill-opacity:0.2;"/></g></svg>'),
	OP1_HELP_BUTTON: SVG('<svg><g id="OP1_HELP_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><path d="M14.061,19.524c-1.877,0 -3.532,-1.545 -3.532,-3.532m9.271,3.532c1.876,0 3.311,-1.545 3.311,-3.532m0.004,0c0,-1.876 -1.439,-3.422 -3.426,-3.422m-5.628,0c-1.877,0 -3.532,1.546 -3.532,3.532m3.532,-3.532l5.628,0m-5.628,6.954l2.759,0m0.11,0l0,1.766m0,0l1.877,-1.766m0.993,0l-1.104,0" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/></g></svg>'),
	OP1_KEY1: SVG('<svg><g id="OP1_KEY1"><path d="M0,16.766c0.059,-9.263 7.598,-16.766 16.875,-16.766c9.314,0 16.875,7.561 16.875,16.875l0,48c0,9.314 -7.561,16.875 -16.875,16.875c-9.314,0 -16.875,-7.561 -16.875,-16.875l0,-48l0,-0.109Z" style="fill:%s;fill-opacity:0.05;"/></g></svg>'),
	OP1_KEY4: SVG('<svg><g id="OP1_KEY4"><circle cx="16.875" cy="16.875" r="16.875" style="fill:black;fill-opacity:0.7;"/></g></svg>'),
	OP1_LEFT_ARROW: SVG('<svg><g id="OP1_LEFT_ARROW"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><path d="M20.186,22.338l-6.733,-5.518l6.844,-5.408" style="fill:none;stroke:%s;stroke-width:0.75px;stroke-linecap:round;stroke-linejoin:miter;stroke-miterlimit:1.5;"/></g></svg>'),
	OP1_METRONOME_BUTTON: SVG('<svg><g id="OP1_METRONOME_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><g><path d="M21.014,15.343c-0.839,0 -1.559,-0.719 -1.559,-1.558c0,-0.84 0.72,-1.559 1.559,-1.559c0.839,0 1.559,0.719 1.559,1.559c0,0.959 -0.72,1.558 -1.559,1.558Z" style="fill:%s;"/><path d="M11.301,21.952l3.422,-10.154l1.214,0l3.532,10.154l-8.168,0Z" style="fill:none;stroke:%s;stroke-width:0.75px;stroke-linejoin:miter;stroke-miterlimit:1.5;"/><path d="M14.943,20.297l5.078,-5.409" style="fill:none;stroke:%s;stroke-width:0.75px;stroke-linejoin:miter;stroke-miterlimit:1.5;"/></g></g></svg>'),
	OP1_MICRO: SVG('<svg><g id="OP1_MICRO"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><path d="M19.193,17.041c-0.331,0 -0.662,-0.111 -0.994,-0.221l-4.635,4.635l-1.214,-1.214l4.635,-4.635c-0.11,-0.331 -0.22,-0.663 -0.22,-0.994c0,-1.324 1.103,-2.317 2.317,-2.317c1.215,0 2.318,1.103 2.318,2.317c0,1.214 -0.883,2.429 -2.207,2.429Z" style="fill:rgb(241,89,36);"/></g></svg>'),
	OP1_MODE_1_BUTTON: SVG('<svg><g id="OP1_MODE_1_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><path d="M24.16,14.447c0,-0.662 -0.552,-1.214 -1.215,-1.214c-0.662,0 -1.214,0.552 -1.214,1.214l0,4.856c0,0.662 -0.551,1.214 -1.214,1.214c-0.662,0 -1.214,-0.552 -1.214,-1.214l0,-4.856c0,-0.662 -0.552,-1.214 -1.214,-1.214c-0.662,0 -1.214,0.552 -1.214,1.214l0,4.856c0,0.662 -0.552,1.214 -1.214,1.214c-0.662,0 -1.214,-0.552 -1.214,-1.214l0,-4.856c0,-0.662 -0.552,-1.214 -1.214,-1.214c-0.663,0 -1.214,0.552 -1.214,1.214l0,4.856c0,0.662 -0.552,1.214 -1.214,1.214c-0.663,0 -1.215,-0.552 -1.215,-1.214" style="fill:none;fill-rule:nonzero;stroke:rgb(36,174,255);stroke-width:0.75px;"/></g></svg>'),
	OP1_MODE_2_BUTTON: SVG('<svg><g id="OP1_MODE_2_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><g><circle cx="16.875" cy="15.771" r="4.856" style="fill:none;stroke:rgb(27,180,83);stroke-width:0.75px;"/><path d="M17.868,16.654c0,0.552 -0.441,0.994 -0.993,0.994c-0.552,0 -0.993,-0.442 -0.993,-0.994c0,-0.552 0.441,-0.883 0.993,-0.883c0.552,-0.11 0.993,0.331 0.993,0.883Zm-0.993,6.181l0,-6.181" style="fill:none;fill-rule:nonzero;stroke:rgb(27,180,83);stroke-width:0.75px;"/></g></g></svg>'),
	OP1_MODE_3_BUTTON: SVG('<svg><g id="OP1_MODE_3_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><g><circle cx="12.129" cy="16.82" r="3.642" style="fill:none;stroke:rgb(241,89,36);stroke-width:0.75px;"/><circle cx="21.621" cy="16.82" r="3.642" style="fill:none;stroke:rgb(241,89,36);stroke-width:0.75px;"/><path d="M12.129,20.572l9.492,0" style="fill:none;fill-rule:nonzero;stroke:rgb(241,89,36);stroke-width:0.75px;"/></g></g></svg>'),
	OP1_MODE_4_BUTTON: SVG('<svg><g id="OP1_MODE_4_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><g><path d="M11.908,15.44l0,6.071" style="fill:none;stroke:%s;stroke-width:0.75px;stroke-linejoin:miter;stroke-miterlimit:1.5;"/><path d="M15.219,12.239l0,9.272" style="fill:none;stroke:%s;stroke-width:0.75px;stroke-linejoin:miter;stroke-miterlimit:1.5;"/><path d="M18.531,16.985l0,4.526" style="fill:none;stroke:%s;stroke-width:0.75px;stroke-linejoin:miter;stroke-miterlimit:1.5;"/><path d="M21.842,15.44l0,6.071" style="fill:none;stroke:%s;stroke-width:0.75px;stroke-linejoin:miter;stroke-miterlimit:1.5;"/></g></g></svg>'),
	OP1_PATTERN: SVG('<svg><g id="OP1_PATTERN"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><g><path d="M18.862,20.517c-0.773,0 -1.435,-0.662 -1.435,-1.435c0,-0.772 0.662,-1.434 1.435,-1.434c0.772,0 1.435,0.662 1.435,1.434c0,0.773 -0.663,1.435 -1.435,1.435Z" style="fill:rgb(36,174,255);"/><path d="M23.387,20.517c-0.773,0 -1.435,-0.662 -1.435,-1.435c0,-0.772 0.662,-1.434 1.435,-1.434c0.773,0 1.435,0.662 1.435,1.434c0,0.773 -0.662,1.435 -1.435,1.435Z" style="fill:rgb(36,174,255);"/><path d="M10.363,20.517c-0.773,0 -1.435,-0.662 -1.435,-1.435c0,-0.772 0.662,-1.434 1.435,-1.434c0.773,0 1.435,0.662 1.435,1.434c0,0.773 -0.662,1.435 -1.435,1.435Z" style="fill:rgb(36,174,255);"/><path d="M14.668,16.102c-0.773,0 -1.435,-0.662 -1.435,-1.434c0,-0.773 0.662,-1.435 1.435,-1.435c0.772,0 1.434,0.662 1.434,1.435c-0.11,0.772 -0.662,1.434 -1.434,1.434Z" style="fill:rgb(36,174,255);"/></g></g></svg>'),
	OP1_PLAY_BUTTON: SVG('<svg><g id="OP1_PLAY_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><path d="M20.628,17.351c0.441,-0.221 0.441,-0.662 0,-0.883l-7.064,-3.642c-0.442,-0.331 -0.773,-0.111 -0.773,0.441l0,7.285c0,0.441 0.331,0.662 0.773,0.441l7.064,-3.642Z" style="fill:%s;"/></g></svg>'),
	OP1_REC_BUTTON: SVG('<svg><g id="OP1_REC_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><path d="M16.875,28.805c6.546,0 11.93,-5.279 11.93,-11.93c0,-6.546 -5.279,-11.93 -11.93,-11.93c-6.546,0 -11.93,5.279 -11.93,11.93c0,6.546 5.279,11.93 11.93,11.93Zm0,-15.572c2.01,0 3.642,1.632 3.642,3.642c0,2.01 -1.632,3.642 -3.642,3.642c-2.01,0 -3.642,-1.632 -3.642,-3.642c0,-2.01 1.632,-3.642 3.642,-3.642Z" style="fill:rgb(241,89,36);"/></g></svg>'),
	OP1_RIGHT_ARROW: SVG('<svg><g id="OP1_RIGHT_ARROW"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><path d="M13.453,11.412l6.844,5.408l-6.844,5.518" style="fill:none;stroke:%s;stroke-width:0.75px;stroke-linecap:round;stroke-linejoin:miter;stroke-miterlimit:1.5;"/></g></svg>'),
	OP1_SCISSOR_BUTTON: SVG('<svg><g id="OP1_SCISSOR_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><g><circle cx="21.124" cy="9.756" r="1.656" style="fill:none;stroke:rgb(241,89,36);stroke-width:0.75px;"/><circle cx="21.124" cy="15.385" r="1.656" style="fill:none;stroke:rgb(241,89,36);stroke-width:0.75px;"/><path d="M21.897,11.191l-10.706,3.973m0,-5.187l10.706,3.973" style="fill:none;fill-rule:nonzero;stroke:rgb(241,89,36);stroke-width:0.75px;"/><path d="M19.138,20.352l0,5.298" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><path d="M10.308,24.325c0,0.773 0.552,1.325 1.324,1.325c0.773,0 1.325,-0.552 1.325,-1.325l0,-3.973" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><path d="M20.793,25.65l0,-5.298l0.331,0l2.097,5.298l0.221,0l0,-5.298" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><path d="M14.502,21.787l0,2.428c0,0.772 0.662,1.435 1.435,1.435c0.772,0 1.435,-0.663 1.435,-1.435l0,-2.428c0,-0.773 -0.663,-1.435 -1.435,-1.435c-0.773,0 -1.435,0.662 -1.435,1.435Z" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/></g></g></svg>'),
	OP1_SHIFT_BUTTON: SVG('<svg><g id="OP1_SHIFT_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><g><path d="M7.438,18.751c0,1.104 0.883,1.877 1.877,1.877c1.103,0 1.876,-0.883 1.876,-1.877c0,-0.441 -0.331,-0.993 -0.773,-1.324c-0.441,-0.331 -1.766,-0.883 -2.207,-1.104c-0.552,-0.331 -0.773,-0.883 -0.773,-1.324c0,-1.104 0.883,-1.877 1.877,-1.877c1.103,0 1.876,0.883 1.876,1.877" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><path d="M13.178,13.012l0,7.726m0,-3.201c0,-0.772 0.662,-1.435 1.434,-1.435c0.773,0 1.435,0.663 1.435,1.435l0,3.201m2.208,-4.636l0,4.636m0,-7.726l0,0.993m3.752,-0.772l0.773,0m-1.876,7.505l0,-6.402c0,-0.551 0.441,-1.103 1.103,-1.103m4.305,7.505l-0.773,0m-0.993,-7.505l0,6.401c0,0.552 0.441,1.104 1.104,1.104m-6.181,-4.636l2.869,0m0.773,0l2.87,0" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/></g></g></svg>'),
	OP1_SS1_BUTTON: SVG('<svg><g id="OP1_SS1_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><g><path d="M16.323,7.107l0,9.602" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><path d="M14.116,20.572l0,6.071" style="fill:none;fill-rule:nonzero;stroke:rgb(27,180,83);stroke-width:0.75px;"/><path d="M16.544,26.643l0,-6.071l0.331,0l2.428,6.071l0.331,0l0,-6.071" style="fill:none;fill-rule:nonzero;stroke:rgb(27,180,83);stroke-width:0.75px;"/></g></g></svg>'),
	OP1_SS2_BUTTON: SVG('<svg><g id="OP1_SS2_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><path d="M18.31,16.709l-4.857,0l4.305,-5.739c0.331,-0.441 0.441,-0.883 0.441,-1.435c0,-1.324 -1.103,-2.428 -2.428,-2.428c-1.324,0 -2.428,1.104 -2.428,2.428" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><path d="M19.745,20.572l3.752,0m-1.766,0l0,6.071m-6.401,-6.071l0,4.526c0,0.883 0.662,1.545 1.545,1.545c0.883,0 1.545,-0.662 1.545,-1.545l0,-4.526" style="fill:none;fill-rule:nonzero;stroke:rgb(27,180,83);stroke-width:0.75px;"/><path d="M10.253,22.228l0,2.759c0,0.883 0.772,1.656 1.655,1.656c0.883,0 1.656,-0.773 1.656,-1.656l0,-2.759c0,-0.883 -0.773,-1.656 -1.656,-1.656c-0.883,0 -1.655,0.773 -1.655,1.656Z" style="fill:none;fill-rule:nonzero;stroke:rgb(27,180,83);stroke-width:0.75px;"/></g></svg>'),
	OP1_SS3_BUTTON: SVG('<svg><g id="OP1_SS3_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><path d="M17.813,21.235l2.318,0c1.545,0 2.759,1.214 2.759,2.759c0,1.545 -1.214,2.759 -2.759,2.759l-6.512,0c-1.545,0 -2.759,-1.214 -2.759,-2.759c0,-1.545 1.214,-2.759 2.759,-2.759" style="fill:none;fill-rule:nonzero;stroke:rgb(27,180,83);stroke-width:0.75px;"/><path d="M17.703,22.559l-2.208,-1.324l2.208,-1.214l0,2.538Z" style="fill:none;fill-rule:nonzero;stroke:rgb(27,180,83);stroke-width:0.75px;"/><path d="M14.061,6.997l4.856,0l0,0.441l-2.428,4.305c1.324,0 2.428,1.103 2.428,2.428c0,1.324 -1.104,2.428 -2.428,2.428c-1.325,0 -2.428,-1.104 -2.428,-2.428" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/></g></svg>'),
	OP1_SS4_BUTTON: SVG('<svg><g id="OP1_SS4_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><g><path d="M18.862,13.674l-5.74,0l0,-0.441l3.863,-6.291l0.442,0l0,9.602" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><circle cx="12.46" cy="24.049" r="2.759" style="fill:none;stroke:rgb(241,89,36);stroke-width:0.75px;"/><circle cx="19.634" cy="24.049" r="2.759" style="fill:none;stroke:rgb(241,89,36);stroke-width:0.75px;"/><path d="M12.46,26.808l7.174,0m1.877,-6.732c1.434,0.662 2.538,2.207 2.538,3.973" style="fill:none;fill-rule:nonzero;stroke:rgb(241,89,36);stroke-width:0.75px;"/></g></g></svg>'),
	OP1_SS5_BUTTON: SVG('<svg><g id="OP1_SS5_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><g><path d="M19.689,6.942l-4.856,0l0,7.174c0,-1.325 1.104,-2.428 2.428,-2.428c1.325,0 2.428,1.103 2.428,2.428c0,1.324 -1.103,2.428 -2.428,2.428l-2.428,0" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><path d="M19.358,26.808l0,-6.291l-3.752,0c-0.883,0 -1.545,0.663 -1.545,1.545c0,0.883 0.662,1.546 1.545,1.546l3.421,0m-1.655,0.22l-2.76,2.98" style="fill:none;fill-rule:nonzero;stroke:rgb(241,89,36);stroke-width:0.75px;"/></g></g></svg>'),
	OP1_SS6_BUTTON: SVG('<svg><g id="OP1_SS6_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><g><path d="M19.469,10.308c0,-1.325 -1.104,-2.428 -2.428,-2.428c-1.325,0 -2.429,1.103 -2.429,2.428l0,4.856" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><circle cx="17.041" cy="15.054" r="2.428" style="fill:none;stroke:%s;stroke-width:0.75px;"/><path d="M11.853,25.87c-0.883,0 -1.545,-0.662 -1.545,-1.545c0,-0.883 0.662,-1.545 1.545,-1.545c0.883,0 1.545,0.662 1.545,1.545c0,0.883 -0.662,1.545 -1.545,1.545Z" style="fill:none;stroke:rgb(241,89,36);stroke-width:0.75px;"/><path d="M22.67,25.098c-0.442,0 -0.773,-0.331 -0.773,-0.773c0,-0.441 0.331,-0.772 0.773,-0.772c0.441,0 0.772,0.331 0.772,0.772c0,0.442 -0.331,0.773 -0.772,0.773Z" style="fill:none;stroke:rgb(241,89,36);stroke-width:0.75px;"/><path d="M19.469,25.098c-0.442,0 -0.773,-0.331 -0.773,-0.773c0,-0.441 0.331,-0.772 0.773,-0.772c0.441,0 0.772,0.331 0.772,0.772c0,0.442 -0.331,0.773 -0.772,0.773Z" style="fill:none;stroke:rgb(241,89,36);stroke-width:0.75px;"/><path d="M16.158,25.098c-0.442,0 -0.773,-0.331 -0.773,-0.773c0,-0.441 0.331,-0.772 0.773,-0.772c0.441,0 0.772,0.331 0.772,0.772c0,0.442 -0.331,0.773 -0.772,0.773Z" style="fill:none;stroke:rgb(241,89,36);stroke-width:0.75px;"/></g></g></svg>'),
	OP1_SS7_BUTTON: SVG('<svg><g id="OP1_SS7_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><g><path d="M15.109,7.107l4.746,0l-4.746,9.602" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><path d="M12.902,26.643l0,-6.071l0.331,0l1.766,4.084l0.331,0l1.876,-4.084l0.331,0l0,6.071" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><path d="M20.848,20.572l0,6.071" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/></g></g></svg>'),
	OP1_SS8_BUTTON: SVG('<svg><g id="OP1_SS8_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><circle cx="17.041" cy="9.535" r="2.428" style="fill:none;stroke:%s;stroke-width:0.75px;"/><circle cx="17.041" cy="14.281" r="2.428" style="fill:none;stroke:%s;stroke-width:0.75px;"/><path d="M12.074,26.643l0,-6.071l0.331,0l1.766,4.084l0.331,0l1.876,-4.084l0.331,0l0,6.071" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/><path d="M21.566,26.643l-2.98,0l2.759,-3.642c0.221,-0.221 0.331,-0.552 0.331,-0.883c0,-0.883 -0.662,-1.546 -1.545,-1.546c-0.883,0 -1.545,0.663 -1.545,1.546" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/></g></svg>'),
	OP1_STOP_BUTTON: SVG('<svg><g id="OP1_STOP_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><rect x="13.178" y="13.233" width="7.395" height="7.285" style="fill:%s;"/></g></svg>'),
	OP1_T1_BUTTON: SVG('<svg><g id="OP1_T1_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><path d="M16.875,9.811l0,14.128" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/></g></svg>'),
	OP1_T2_BUTTON: SVG('<svg><g id="OP1_T2_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><path d="M10.142,14.502c0,-2.649 2.097,-4.746 4.746,-4.746l3.753,0c2.649,0 4.746,2.097 4.746,4.746c0,2.097 -1.214,3.753 -3.311,4.525l-9.934,4.305l0,0.662l13.466,0" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/></g></svg>'),
	OP1_T3_BUTTON: SVG('<svg><g id="OP1_T3_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><path d="M20.352,17.206l-5.077,0l5.077,0c1.986,0 3.642,1.545 3.642,3.532c0,1.987 -1.656,3.532 -3.642,3.532l-6.954,0c-1.986,0 -3.642,-1.656 -3.642,-3.642m5.519,-3.422l7.946,-7.726l-12.803,0" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/></g></svg>'),
	OP1_T4_BUTTON: SVG('<svg><g id="OP1_T4_BUTTON"><circle cx="16.875" cy="16.875" r="16.875" style="fill:%s;fill-opacity:0.05;"/><path d="M23.994,19.689l-14.238,0l0,-0.662l9.933,-9.271l0.663,0l0,14.238" style="fill:none;fill-rule:nonzero;stroke:%s;stroke-width:0.75px;"/></g></svg>')
}

VECTORS[OP1_KEY2] = VECTORS[OP1_KEY4]
VECTORS[OP1_KEY4] = VECTORS[OP1_KEY4]
VECTORS[OP1_KEY6] = VECTORS[OP1_KEY4]
VECTORS[OP1_KEY9] = VECTORS[OP1_KEY4]
VECTORS[OP1_KEY11] = VECTORS[OP1_KEY4]
VECTORS[OP1_KEY14] = VECTORS[OP1_KEY4]
VECTORS[OP1_KEY16] = VECTORS[OP1_KEY4]
VECTORS[OP1_KEY18] = VECTORS[OP1_KEY4]
VECTORS[OP1_KEY21] = VECTORS[OP1_KEY4]
VECTORS[OP1_KEY23] = VECTORS[OP1_KEY4]
VECTORS[OP1_KEY1] = VECTORS[OP1_KEY1]
VECTORS[OP1_KEY3] = VECTORS[OP1_KEY1]
VECTORS[OP1_KEY5] = VECTORS[OP1_KEY1]
VECTORS[OP1_KEY7] = VECTORS[OP1_KEY1]
VECTORS[OP1_KEY8] = VECTORS[OP1_KEY1]
VECTORS[OP1_KEY10] = VECTORS[OP1_KEY1]
VECTORS[OP1_KEY12] = VECTORS[OP1_KEY1]
VECTORS[OP1_KEY13] = VECTORS[OP1_KEY1]
VECTORS[OP1_KEY15] = VECTORS[OP1_KEY1]
VECTORS[OP1_KEY17] = VECTORS[OP1_KEY1]
VECTORS[OP1_KEY19] = VECTORS[OP1_KEY1]
VECTORS[OP1_KEY20] = VECTORS[OP1_KEY1]
VECTORS[OP1_KEY22] = VECTORS[OP1_KEY1]
VECTORS[OP1_KEY24] = VECTORS[OP1_KEY1]

class OP1Button(QLabel):
	state = False
	clicked = pyqtSignal()
	rotation = None

	def mousePressEvent(self, QMouseEvent):
		if QMouseEvent.button() == QtCore.Qt.LeftButton:
			#self.clicked.emit()
			self.toggleState(1)

	def mouseReleaseEvent(self, QMouseEvent):
		if QMouseEvent.button() == QtCore.Qt.LeftButton:
			self.clicked.emit()
			self.toggleState(0)

	def toggleState(self, state=None):
		# Change state to make the button pushed/unpushed
		if(self.state):
			self.setProperty("btnPressed", "false")
		else:
			self.setProperty("btnPressed", "true")

		# Forces the next state in case state toggle is inverted
		if((state is not None) and ((state == 1) or (state == 0))):
			self.state = state
		else:
			self.state = not self.state 

		self.style().unpolish(self)
		self.style().polish(self)
		self.update()

	def rotate(self, deg):
		if(self.rotation is None):
			self.rotation = 0
			self.vector = self.text().replace("<svg>", "<svg %s>")
		self.rotation += deg 
		self.setText((self.vector % ('transform="rotate(%d)"' % self.rotation)))

class QMidiListener(QObject):
	
	_midiStream = pyqtSignal(tuple, name="midiStream")

	def __init__(self, statusOut=None):
		super(QMidiListener, self).__init__()
		self.connected = False
		self.processor = None

		# Pass along an class to act as an indicator
		# In this case it's text line edit screen
		self.status = statusOut

		# Interface with the MIDI library
		# Attempt to connect
		self.midi = rtMidiIn()
		self.connectMidi()
		return

	def find_port(self):
		# Find the port that the OP-1 is on
		try:
			self.port = self.midi.get_ports().index('OP-1 Midi Device')
			self.out("Found %s on port %d" % (self.midi.get_port_name(self.port), self.port))
			return 1
		except ValueError:
			self.out("Could not find OP-1")
			return 0

	def connectMidi(self):
		# Connect to midi port after finding it
		# Start a callback process
		try:
			if(self.find_port()):
				# rtmidi._rtmidi.InvalidUseError: <rtmidi._rtmidi.MidiIn object at 0x7ff9e83391d0> already opened input port 0.
				self.midi.open_port(self.port)
				self.out("Connected to %s" % self.midi.get_port_name(self.port))
				self._midiStream.connect(self._midi_background_interface)
				self.midi.set_callback(self._midi_received_signal)
				self.connected = True
		except AttributeError:
			self.out("No MIDI device found")
	
	def connectProcessor(self, processor):
		# Connect external function that will handle the events
		self.processor = processor

	def _midi_received_signal(self, data, other=None):
		self._midiStream.emit(data)
		return

	@QtCore.pyqtSlot(tuple)
	def _midi_background_interface(self, data, other=None):
		# Send the midi data to the connect processor 
		msg, delta_time = data		
		if(self.processor != None):
			self.processor(msg)

	def closeMidi(self):
		# Close midi connection
		self.connected = False
		self.midi.cancel_callback()
		try:
			self.midi.close_port()
			self.out("Closed connection on port %d" % self.port)
		except AttributeError:
			pass

	def out(self, string):
		# Output message to status/debug screen
		self.status.append(string)
		return "%s\n" % string

	def toggle(self):
		# Toggle connection state
		if(self.connected):
			self.closeMidi()
		else:
			self.connectMidi()

class PhilipsHueController(Bridge):
	def __init__(self, ip, statusOut):
		super().__init__(ip)
		self.connect()
		self.status = statusOut

		# Which light is selected to control - 0 signifies all lights
		self.selected = 0

		# IDs of the four lights to control
		self.l1 = -1
		self.l2 = -1
		self.l3 = -1
		self.l4 = -1

	def setLight(self, number, name):
		# Assign the four lights by name, use name to get the light ID
		if(number == 1):
			self.l1 = int(self.get_light_id_by_name(name)) - 1
		elif(number == 2):
			self.l2 = int(self.get_light_id_by_name(name)) - 1
		elif(number == 3):
			self.l3 = int(self.get_light_id_by_name(name)) - 1
		elif(number == 4):
			self.l4 = int(self.get_light_id_by_name(name)) - 1

	def incrementBrightness(self, light, positive, value=0x8):
		brightness = self.lights[light].brightness
		value = value * (1 if positive else -1)

		# Don't adjust brightness if it's at the limit
		# This helps reduce load on the PHue API  
		if((brightness == 0 and not positive) or (brightness == 0xfe and positive)):
			return
		
		# Cap the brightness within a valid range
		if((brightness + value) > 0xff):
			brightness = 0xfe
		elif((brightness + value) < 0):
			brightness = 0
		else:
			brightness = brightness + value

		self.lights[light].brightness = brightness

		return

	def incrementHue(self, light, positive, value=0x1fe):
		hue = self.lights[light].hue
		value = value * (1 if positive else -1)

		# Restart the hue value if you reach the limit
		if((hue + value) > 0xffff):
			hue = 0
		elif((hue + value) < 0):
			hue = 0xfffe
		else:
			hue = hue + value

		self.lights[light].hue = hue

	def incrementSaturation(self, light, positive, value=0x8):
		saturation = self.lights[light].saturation
		value = value * (1 if positive else -1)

		# Don't adjust saturation if it's at the limit
		# This helps reduce load on the PHue API  
		if((saturation == 0 and not positive) or (saturation == 0xfe and positive)):
			return
		
		# Cap the saturation within a valid range
		if((saturation + value) > 0xff):
			saturation = 0xfe
		elif((saturation + value) < 0):
			saturation = 0
		else:
			saturation = saturation + value

		self.lights[light].saturation = saturation

		return

	def incrementTemp(self, light, positive, value=0x96):
		temp = self.lights[light].colortemp_k
		value = value * (1 if positive else -1)

		# Restart the temp value if you reach the limit
		if((temp + value) > 0x1964):
			temp = 2000
		elif((temp + value) < 2000):
			temp = 0x1964
		else:
			temp = temp + value

		self.lights[light].colortemp_k = temp

	def processCommand(self, mode, button, value):
		# Pass in a button and value, do some Philips Hue action as a result.
		if(not mode == 0xb0):
			return

		# Select which light to control
		if(button == OP1_MODE_2_BUTTON and value == 0x0):
			self.selected = 0
		elif(button == OP1_T1_BUTTON and value == 0x0):
			self.selected = 0 if (self.selected == 1) else 1
		elif(button == OP1_T2_BUTTON and value == 0x0):
			self.selected = 0 if (self.selected == 2) else 2
		elif(button == OP1_T3_BUTTON and value == 0x0):
			self.selected = 0 if (self.selected == 3) else 3
		elif(button == OP1_T4_BUTTON and value == 0x0):
			self.selected = 0 if (self.selected == 4) else 4

		# Control all lights
		if(self.selected == 0):

			# Encoder click to toggle light on/off
			if(button == OP1_ENCODER_BUTTON_1 and value == 0x0):
				self.lights[self.l1].on = not self.lights[self.l1].on
				self.status.append("Light %d %s" % (1, "ON" if self.lights[self.l1].on else "OFF"))
			elif(button == OP1_ENCODER_BUTTON_2 and value == 0x0):
				self.lights[self.l2].on = not self.lights[self.l2].on
				self.status.append("Light %d %s" % (2, "ON" if self.lights[self.l2].on else "OFF"))
			elif(button == OP1_ENCODER_BUTTON_3 and value == 0x0):
				self.lights[self.l3].on = not self.lights[self.l3].on
				self.status.append("Light %d %s" % (3, "ON" if self.lights[self.l3].on else "OFF"))
			elif(button == OP1_ENCODER_BUTTON_4 and value == 0x0):
				self.lights[self.l4].on = not self.lights[self.l4].on
				self.status.append("Light %d %s" % (4, "ON" if self.lights[self.l4].on else "OFF"))

			# Encoder turn controls brightness on a light
			elif(button == OP1_ENCODER_1):
				self.incrementBrightness(self.l1, 1 if (value == 0x1) else 0x0)
			elif(button == OP1_ENCODER_2):
				self.incrementBrightness(self.l2, 1 if (value == 0x1) else 0x0)
			elif(button == OP1_ENCODER_3):
				self.incrementBrightness(self.l3, 1 if (value == 0x1) else 0x0)
			elif(button == OP1_ENCODER_4):
				self.incrementBrightness(self.l4, 1 if (value == 0x1) else 0x0)

		else:
			# Individual light control
			light = self.selected-1

			# Toggle light on/off
			if(button == OP1_ENCODER_BUTTON_1 and value == 0x0):
				self.lights[light].on = not self.lights[light].on
				self.status.append("Light %d %s" % (self.selected, "ON" if self.lights[light].on else "OFF"))

			
			# Reset hue, saturation, temperature
			elif(button == OP1_ENCODER_BUTTON_2 and value == 0x0):
				self.lights[light].hue = 0xc000
			elif(button == OP1_ENCODER_BUTTON_3 and value == 0x0):
				self.lights[light].saturation = 0xd7
			elif(button == OP1_ENCODER_BUTTON_4 and value == 0x0):
				self.lights[light].colortemp_k = 0xaac

			# Encoder controls brightness, hue, saturation, temperature
			elif(button == OP1_ENCODER_1):
				self.incrementBrightness(light, 1 if (value == 0x1) else 0x0)
			elif(button == OP1_ENCODER_2):
				self.incrementHue(light, 0x1 if (value == 0x1) else 0x0)
			elif(button == OP1_ENCODER_3):
				self.incrementSaturation(light, 1 if (value == 0x1) else 0x0)
			elif(button == OP1_ENCODER_4):
				self.incrementTemp(light, 0x1 if (value == 0x1) else 0x0)
		
		return

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.nightMode = 1
		self.mode = OP1_MODE_2_BUTTON
		self.initUI()

		# Initialize midi component
		self.midi = QMidiListener(self.io["SCREEN"])
		self.midi._midiStream.connect(self.midiEventHandler)

		# Initialize Phiilips Hue component
		self.pHue = PhilipsHueController(PHUE_BRIDGE_IP, self.io["SCREEN"])
		self.pHue.setLight(1, PHUE_LIGHT_1)
		self.pHue.setLight(2, PHUE_LIGHT_2)
		self.pHue.setLight(3, PHUE_LIGHT_3)
		self.pHue.setLight(4, PHUE_LIGHT_4)

		self.show()

	def initUI(self):
		self.setFixedWidth(950)
		self.setFixedHeight(600)
		#self.setWindowIcon(QIcon('web.png'))
		self.setWindowTitle('OP-1 Macropad')
		self.setLayout(QVBoxLayout())
		main = QWidget()
		self.layout().addWidget(main)
		main.setLayout(QVBoxLayout())
		main.setFixedWidth(self.width())
		main.setFixedHeight(self.height())
		main.layout().setAlignment(QtCore.Qt.AlignCenter)

		# Create OP-1 View
		self.op1View = QWidget()
		main.layout().addWidget(self.op1View)
		self.op1View.setFixedWidth(880)
		self.op1View.setFixedHeight(int(self.op1View.width() * (6/17)))

		self.op1View.setLayout(QGridLayout())
		grid = self.op1View.layout()
		grid.setSpacing(3)

		# All the buttons on the OP-1
		self.io = {
			OP1_ENCODER_1: OP1Button(),
			OP1_ENCODER_2: OP1Button(),
			OP1_ENCODER_3: OP1Button(),
			OP1_ENCODER_4: OP1Button(),

			OP1_HELP_BUTTON: OP1Button(),
			OP1_METRONOME_BUTTON: OP1Button(),

			OP1_MODE_1_BUTTON: OP1Button(),
			OP1_MODE_2_BUTTON: OP1Button(),
			OP1_MODE_3_BUTTON: OP1Button(),
			OP1_MODE_4_BUTTON: OP1Button(),

			OP1_T1_BUTTON: OP1Button(),
			OP1_T2_BUTTON: OP1Button(),
			OP1_T3_BUTTON: OP1Button(),
			OP1_T4_BUTTON: OP1Button(),

			OP1_ARROW_UP_BUTTON: OP1Button(),
			OP1_ARROW_DOWN_BUTTON: OP1Button(),
			OP1_SCISSOR_BUTTON: OP1Button(),

			OP1_SS1_BUTTON: OP1Button(),
			OP1_SS2_BUTTON: OP1Button(),
			OP1_SS3_BUTTON: OP1Button(),
			OP1_SS4_BUTTON: OP1Button(),
			OP1_SS5_BUTTON: OP1Button(),
			OP1_SS6_BUTTON: OP1Button(),
			OP1_SS7_BUTTON: OP1Button(),
			OP1_SS8_BUTTON: OP1Button(),

			OP1_REC_BUTTON: OP1Button(),
			OP1_PLAY_BUTTON: OP1Button(),
			OP1_STOP_BUTTON: OP1Button(),

			OP1_LEFT_ARROW: OP1Button(),
			OP1_RIGHT_ARROW: OP1Button(),
			OP1_SHIFT_BUTTON: OP1Button(),

			OP1_MICRO: OP1Button(),
			OP1_COM: OP1Button(),
			OP1_PATTERN: OP1Button(),

			"SPEAKER": OP1Button(),
			"VOLUME": OP1Button(),
			"SCREEN": QTextEdit(),

			OP1_KEY1: OP1Button(),
			OP1_KEY2: OP1Button(),
			OP1_KEY3: OP1Button(),
			OP1_KEY4: OP1Button(),
			OP1_KEY5: OP1Button(),
			OP1_KEY6: OP1Button(),
			OP1_KEY7: OP1Button(),
			OP1_KEY8: OP1Button(),
			OP1_KEY9: OP1Button(),
			OP1_KEY10: OP1Button(),
			OP1_KEY11: OP1Button(),
			OP1_KEY12: OP1Button(),
			OP1_KEY13: OP1Button(),
			OP1_KEY14: OP1Button(),
			OP1_KEY15: OP1Button(),
			OP1_KEY16: OP1Button(),
			OP1_KEY17: OP1Button(),
			OP1_KEY18: OP1Button(),
			OP1_KEY19: OP1Button(),
			OP1_KEY20: OP1Button(),
			OP1_KEY21: OP1Button(),
			OP1_KEY22: OP1Button(),
			OP1_KEY23: OP1Button(),
			OP1_KEY24: OP1Button()
		}

		#buttonStyle = 'font-size:5px;width:100%%; height:100%%; background-color: rgb(%d, %d, %d);'
		#[self.io[i].setStyleSheet(buttonStyle % (random.randint(0x0,0xff), random.randint(0x0,0xff), random.randint(0x0,0xff))) for i in self.io]
		
		# Place OP-1 buttons on the grid
		grid.addWidget(self.io["SPEAKER"], 0, 0, 4, 4)
		grid.addWidget(self.io["VOLUME"], 0, 4, 2, 4)
		grid.addWidget(self.io["SCREEN"], 0, 8, 4, 8)
		grid.addWidget(self.io[OP1_ENCODER_1], 0, 16, 4, 4)
		grid.addWidget(self.io[OP1_ENCODER_2], 0, 20, 4, 4)
		grid.addWidget(self.io[OP1_ENCODER_3], 0, 24, 4, 4)
		grid.addWidget(self.io[OP1_ENCODER_4], 0, 28, 4, 4)
		grid.addWidget(self.io[OP1_MICRO], 0, 32, 2, 2)

		grid.addWidget(self.io[OP1_HELP_BUTTON], 2, 4, 2, 2)
		grid.addWidget(self.io[OP1_METRONOME_BUTTON], 2, 6, 2, 2)
		grid.addWidget(self.io[OP1_COM], 2, 32, 2, 2)

		grid.addWidget(self.io[OP1_MODE_1_BUTTON], 4, 0, 2, 2)
		grid.addWidget(self.io[OP1_MODE_2_BUTTON], 4, 2, 2, 2)
		grid.addWidget(self.io[OP1_MODE_3_BUTTON], 4, 4, 2, 2)
		grid.addWidget(self.io[OP1_MODE_4_BUTTON], 4, 6, 2, 2)
		grid.addWidget(self.io[OP1_T1_BUTTON], 4, 8, 2, 2)
		grid.addWidget(self.io[OP1_T2_BUTTON], 4, 10, 2, 2)
		grid.addWidget(self.io[OP1_T3_BUTTON], 4, 12, 2, 2)
		grid.addWidget(self.io[OP1_T4_BUTTON], 4, 14, 2, 2)
		grid.addWidget(self.io[OP1_SS1_BUTTON], 4, 16, 2, 2)
		grid.addWidget(self.io[OP1_SS2_BUTTON], 4, 18, 2, 2)
		grid.addWidget(self.io[OP1_SS3_BUTTON], 4, 20, 2, 2)
		grid.addWidget(self.io[OP1_SS4_BUTTON], 4, 22, 2, 2)
		grid.addWidget(self.io[OP1_SS5_BUTTON], 4, 24, 2, 2)
		grid.addWidget(self.io[OP1_SS6_BUTTON], 4, 26, 2, 2)
		grid.addWidget(self.io[OP1_SS7_BUTTON], 4, 28, 2, 2)
		grid.addWidget(self.io[OP1_SS8_BUTTON], 4, 30, 2, 2)
		grid.addWidget(self.io[OP1_PATTERN], 4, 32, 2, 2)

		grid.addWidget(self.io[OP1_ARROW_UP_BUTTON], 6, 0, 2, 2)
		grid.addWidget(self.io[OP1_ARROW_DOWN_BUTTON], 6, 2, 2, 2)
		grid.addWidget(self.io[OP1_SCISSOR_BUTTON], 6, 4, 2, 2)
		#2,4,6,9,11,14,16,18,21,23
		grid.addWidget(self.io[OP1_KEY2], 6, 6, 2, 3)
		grid.addWidget(self.io[OP1_KEY4], 6, 9, 2, 2)
		grid.addWidget(self.io[OP1_KEY6], 6, 11, 2, 3)
		grid.addWidget(self.io[OP1_KEY9], 6, 14, 2, 3)
		grid.addWidget(self.io[OP1_KEY11], 6, 17, 2, 3)
		grid.addWidget(self.io[OP1_KEY14], 6, 20, 2, 3)
		grid.addWidget(self.io[OP1_KEY16], 6, 23, 2, 2)
		grid.addWidget(self.io[OP1_KEY18], 6, 25, 2, 3)
		grid.addWidget(self.io[OP1_KEY21], 6, 28, 2, 3)
		grid.addWidget(self.io[OP1_KEY23], 6, 31, 2, 3)

		grid.addWidget(self.io[OP1_REC_BUTTON], 8, 0, 2, 2)
		grid.addWidget(self.io[OP1_PLAY_BUTTON], 8, 2, 2, 2)
		grid.addWidget(self.io[OP1_STOP_BUTTON], 8, 4, 2, 2)
		#1,3,5,7,8,10,12,13,15,17,19,20,22,24
		grid.addWidget(self.io[OP1_KEY1], 8, 6, 4, 2)
		grid.addWidget(self.io[OP1_KEY3], 8, 8, 4, 2)
		grid.addWidget(self.io[OP1_KEY5], 8, 10, 4, 2)
		grid.addWidget(self.io[OP1_KEY7], 8, 12, 4, 2)
		grid.addWidget(self.io[OP1_KEY8], 8, 14, 4, 2)
		grid.addWidget(self.io[OP1_KEY10], 8, 16, 4, 2)
		grid.addWidget(self.io[OP1_KEY12], 8, 18, 4, 2)
		grid.addWidget(self.io[OP1_KEY13], 8, 20, 4, 2)
		grid.addWidget(self.io[OP1_KEY15], 8, 22, 4, 2)
		grid.addWidget(self.io[OP1_KEY17], 8, 24, 4, 2)
		grid.addWidget(self.io[OP1_KEY19], 8, 26, 4, 2)
		grid.addWidget(self.io[OP1_KEY20], 8, 28, 4, 2)
		grid.addWidget(self.io[OP1_KEY22], 8, 30, 4, 2)
		grid.addWidget(self.io[OP1_KEY24], 8, 32, 4, 2)

		grid.addWidget(self.io[OP1_LEFT_ARROW], 10, 0, 2, 2)
		grid.addWidget(self.io[OP1_RIGHT_ARROW], 10, 2, 2, 2)
		grid.addWidget(self.io[OP1_SHIFT_BUTTON], 10, 4, 2, 2)

		# Add mouse press event listener
		for i in self.io:
			if(i != "SCREEN"):
				self.io[i].clicked.connect(partial(self.clickHandler, i))


		self.renderOP1()

	def renderOP1(self):

		# Set style for background
		self.setStyleSheet("background-color:%s;" % ("#333333" if self.nightMode else "#EBEBEB"))
		self.op1View.setStyleSheet("background-color: %s; border-radius: 5px;" % ("#222222" if self.nightMode else "#BEBEBE")) 

		# Stylesheet for all the buttons
		buttonStyle = "*{border-radius: 5px; background-color: %s; font-size:1px;}" % ("#333333" if self.nightMode else "#EBEBEB")
		buttonStyle += "*:!pressed:hover{border: 1px solid %s;}" % ("#444444" if self.nightMode else "#AAAAAA")
		buttonStyle += "*[btnPressed=\"true\"]{background-color: %s;}" % ("#444444" if self.nightMode else "#AAAAAA")

		for i in self.io:
			if(i != "SCREEN"):
				# Set CSS for each button
				self.io[i].setStyleSheet(buttonStyle)
				self.io[i].setProperty("btnPressed", "false")

				if(i in [54, 61, 66, 73]):
					whitespace = "&nbsp;"*75
					self.io[i].setAlignment(QtCore.Qt.AlignCenter)
				elif(i in [58, 63, 70, 75, "VOLUME"]):
					whitespace = "&nbsp;"*25
				else:
					whitespace = ""
					self.io[i].setAlignment(QtCore.Qt.AlignCenter)
				
				# Set icon from SVG data for each Icon
				try:
					self.io[i].setText(whitespace + '<img src=\'data:image/svg+xml;utf8,%s\'>' % VECTORS[i].get(self.nightMode))
				except KeyError:
					pass
			else:
				self.io[i].setFixedHeight(100)
				self.io[i].setFixedWidth(204)
				self.io[i].setStyleSheet("*{color:white;background-color:black;font-family:Courier;font-size:9px;}")
				sb = QScrollBar()
				self.io[i].setVerticalScrollBar(sb)
				self.io[i].setReadOnly(1)

	def clickHandler(self, event=None):
		if(event == "VOLUME"):
			self.nightMode = not self.nightMode
			self.renderOP1()
		elif(event == "SPEAKER"):
			self.midi.toggle()
		elif(event == OP1_ENCODER_1):
			#QKeyEvent()
			pass

	def closeEvent(self, event=None):
		try:
			self.midi.closeMidi()
		except:
			pass
		self.deleteLater()

	def midiEventHandler(self, data):
		#Handle the incoming hex midi data
		mode, button, value = data[0]

		# Encoder turn
		if(mode == 0xb0 and button >= OP1_ENCODER_1 and  button <= OP1_ENCODER_4):			
			if(value == 0x1):
				self.io[button].rotate(10)
			elif(value == 0x7f):
				self.io[button].rotate(-10)
		# If it's an encoder press
		elif(mode == 0xb0 and button >= OP1_ENCODER_BUTTON_1 and  button <= OP1_ENCODER_BUTTON_4):
			self.io[button-0x3F].toggleState()
		# Button press
		elif(mode == 0xb0):
			self.io[button].toggleState()

			if(button == OP1_MODE_1_BUTTON and value == 0x0):
				self.io["SCREEN"].append("Mode 1")
				self.mode = OP1_MODE_1_BUTTON
			elif(button == OP1_MODE_2_BUTTON and value == 0x0):
				self.io["SCREEN"].append("Mode 2")
				self.mode = OP1_MODE_2_BUTTON
			elif(button == OP1_MODE_3_BUTTON and value == 0x0):
				self.io["SCREEN"].append("Mode 3")
				self.mode = OP1_MODE_3_BUTTON
			elif(button == OP1_MODE_4_BUTTON and value == 0x0):
				self.io["SCREEN"].append("Mode 4")
				self.mode = OP1_MODE_4_BUTTON

		if(self.mode == OP1_MODE_2_BUTTON):
			self.pHue.processCommand(mode, button, value)

		# Keyboard key press
		elif(mode == 0x90 or mode == 0x80):
			self.io[button].toggleState()

if(__name__ == "__main__"):
	app = QtWidgets.QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())