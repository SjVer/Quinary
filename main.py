from svgutils.transform import SVGFigure, fromfile
from typing import List, Tuple, Literal, Optional
from dataclasses import dataclass
from json import load

FILE_FORMAT = "segments/{digit}/{digit}-{part}{conn}.svg"
OUTPUT_FORMAT = "out/{number}.svg"
HEIGHT = 100
MARGIN = 20
FILL = "blue"
DIGITS = "012345"

CONNECTIONS_MAPPING = None

@dataclass
class Segment:
	digit: str
	part: Literal['l', 'm', 'r']
	"""
	conn = 'b': e.g. 1->1, bottom (horizontal)
	conn = 't': e.g. 2->4, top (horizontal)
	conn = 'z': e.g. 0->2, zero (double top)
	conn = 'c': e.g. 1->2, cut off to merge better
	conn = None: normal
	"""
	conn: Optional[Literal['t', 'b', 'z', 'n', 'm']]

def conns_between(l_digit: str, r_digit: str) -> Tuple[str, str]:
	global CONNECTIONS_MAPPING
	if not CONNECTIONS_MAPPING:
		with open("connections.json", "r") as f:
			CONNECTIONS_MAPPING = load(f)

	return CONNECTIONS_MAPPING[l_digit][r_digit]

def dec_to_quin(n: int) -> str:
	if n == 0: return DIGITS[0]

	digits = []
	while n:
		digits.append(DIGITS[n % 6])
		n = n // 6

	digits.reverse()
	return ''.join(digits)

def select_segments(digits: str) -> List[Segment]:
	segments: List[Segment] = []

	while digits:
		digit = digits[0]
		digits = digits[1:]

		if not segments:
			# first digit
			curr_l_conn = 'n'
		else:
			# set connection of right segment of last digit
			prev_r_conn, curr_l_conn = conns_between(segments[-1].digit, digit)
			segments[-1].conn = prev_r_conn

		# set segments of current digit
		segments.append(Segment(digit, 'l', curr_l_conn))
		segments.append(Segment(digit, 'm', 'n'))
		segments.append(Segment(digit, 'r', 'n'))

	for s in segments: print(s)
	return segments

def render(number: str, segments: List[Segment]):
	# get segment figures
	seg_figs: List[SVGFigure] = []
	for seg in segments:
		if seg.conn:
			seg_figs.append(fromfile(FILE_FORMAT.format(
				digit = seg.digit,
				part = seg.part,
				conn = "-" + seg.conn if seg.conn != 'n' else ''
			)))

	# find total width	
	width = 0
	for seg in seg_figs:
		width += int(seg.width.removesuffix("mm"))

	# create the final figure
	fig = SVGFigure()
	fig.set_size([f"{width + 2 * MARGIN}mm", f"{HEIGHT + 2 * MARGIN}mm"])
	fig.root.attrib["viewBox"] = f"0 0 {width + 2 * MARGIN} {HEIGHT + 2 * MARGIN}"

	# add all segments
	x = MARGIN
	for seg in seg_figs:
		root = seg.getroot()
		root.root.attrib["fill"] = "blue"
		root.moveto(x, MARGIN)
		fig.append(root)
		x += int(seg.width.removesuffix("mm")) - 0.15

	fig.save("out.svg")
	print("saved to: out.svg")
	# fig.save(OUTPUT_FORMAT.format(number = number))
	# print("saved to:", OUTPUT_FORMAT.format(number = number))

def main():
	# get input (and convert to quinary if needed)
	digits = input("value (start with '0q' for quinary): ")
	if digits.startswith("0q"):
		for c in digits[2:]:
			if c not in DIGITS:
				print(f"invalid quinary digit '{c}'")
				exit(1)
		digits = digits[2:]
	else:
		digits = dec_to_quin(int(digits))
		print(f"converted to quinary: 0q{digits}")

	# select svg segments
	segments = select_segments(digits)

	# render final svg
	render(digits, segments)

if __name__ == "__main__":
  main()