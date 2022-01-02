from PIL import Image, ImageDraw #, ImageFont
from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser
import os
import itertools

# Represents the data for a family member
class FamilyMember():

	# Reads in an IndividualElement object
	def __init__(self, parser, element):
		self.element = element
		self.parser = parser
		self.cell_x = None
		self.cell_y = None
		self.drawing_pct_x = None
		self.drawing_pct_y = None
		if element is not None:
			(self.first, self.last) = self.element.get_name()

	# Inner rec function
	def __build_tree_list_rec(self, tree, MAX_GENS):
		print(self)
		if len(self.parser.get_parents(self.element)) == 0 or MAX_GENS >= 5:
			return tree
		else:
			if len(tree) == 0:
				tree = [('', self)]
			stem = tree[0][0]
			parents_obj = self.parser.get_parents(self.element)
			p1 = FamilyMember(gedcom_parser, parents_obj[0])
			if len(parents_obj) > 1:
				p2 = FamilyMember(gedcom_parser, parents_obj[1])
			else:
				p2 = None

			# Father is l; Mother is r
			if p1.element.get_gender() == 'F':
				l = p2
				r = p1
			else:
				l = p1
				r = p2
			ltree = [(stem + 'l', l)]
			rtree = [(stem + 'r', r)]
			if l is not None:
				ltree_rec = l.__build_tree_list_rec(ltree, MAX_GENS + 1)
				tree += ltree_rec
			if r is not None:
				rtree_rec = r.__build_tree_list_rec(rtree, MAX_GENS + 1)
				tree += rtree_rec
			return tree

	# Build tree
	def build_tree_list(self):
		return self.__build_tree_list_rec(list(), 0)

	# Print tree
	def print_tree_list(self, tree_list):
		for element in tree_list:
			s = '{}: {}'.format(element[0], element[1])
			print(s)
		return

	# Map ancestry_strings to cell_coordinates
	def ancestry_string_to_cell_coordinates(self, ancestry_string):
		y = len(ancestry_string)
		if len(ancestry_string) == 0:
			x = 0
		else:
			# Create list of all possibilities for that length
			possibilities = list()
			for i in range(len(ancestry_string) + 1):
				num_l = i
				num_r = len(ancestry_string) - num_l
				unsorted_str = ''
				for j in range(num_l):
					unsorted_str += 'l'
				for k in range(num_r):
					unsorted_str += 'r'
				possibilities += list(itertools.permutations(unsorted_str))
			possibilities = sorted(["".join(possibility) for possibility in list(set(possibilities))])
			x = possibilities.index(ancestry_string)
		self.cell_x = x
		self.cell_y = y
		return (x, y)

	# Map cell_coordinates to drawing_coordinates
	def cell_coordinates_to_drawing_coordinates_pcts(self, max_cells_up):
		max_cells_across = 2 ** self.cell_y
		x = 1.0 * (self.cell_x + 1) / (max_cells_across + 1)
		y = 1 - 1.0 * (self.cell_y + 1) / (max_cells_up + 1)
		self.drawing_pct_x = x
		self.drawing_pct_y = y
		return (x, y)

	# Prints details about person
	def __str__(self):
        # Print the first and last name of the found individual
		return str(self.first + " " + self.last + " (" + str(self.element.get_birth_year()) + ")")

	# Draw person on canvas
	def drawMe(self, center_x, center_y):

		# Derive the dimensions of the page
		page_width = center_x / self.drawing_pct_x
		page_height = center_y / self.drawing_pct_y

		max_cells_up = (1.0 * (self.cell_y + 1)) / (1 - self.drawing_pct_y) - 1
		max_cells_across = 2 ** self.cell_y

		# Define specs for each box
		border_length_x = BORDER_LENGTH_X
		border_length_y = BORDER_LENGTH_Y
		origin_x = center_x - 0.5 * border_length_x
		origin_y = center_y - 0.5 * border_length_y
		text_pad_x = 10
		text_pad_y = 10
		top = [(origin_x, origin_y), (origin_x + border_length_x, origin_y)]
		left = [(origin_x, origin_y), (origin_x, origin_y + border_length_y)]
		bottom = [(origin_x, origin_y + border_length_y), (origin_x + border_length_x, origin_y + border_length_y)]
		right = [(origin_x + border_length_x, origin_y), (origin_x + border_length_x, origin_y + border_length_y)]  

		# Derive info for connector lines
		top_center = (origin_x + 0.5 * border_length_x, origin_y)
		bottom_center = (origin_x + 0.5 * border_length_x, origin_y + border_length_y)

		width_between_next_centroid_pct = 1.0 / (max_cells_across + 1)
		width_between_next_centroid = width_between_next_centroid_pct * page_width

		height_between_next_centroid_pct = 1.0 / (max_cells_up + 1)
		height_between_next_centroid = height_between_next_centroid_pct * page_height - border_length_y

		BRACKET_W1 = width_between_next_centroid / 2
		BRACKET_H1 = height_between_next_centroid / 2

		# Draw box and fill in details
		d.line(top, fill =1, width = 0)
		d.line(left, fill =1, width = 0)
		d.line(bottom, fill =1, width = 0)
		d.line(right, fill =1, width = 0)
		d.multiline_text(
			(
				origin_x + text_pad_x, origin_y + text_pad_y
			), 
			"{}\n{}\n{}".format(
				self.first, 
				self.last,
				self.element.get_birth_year()
			), fill=(0, 0, 0)
		)

		# Draw connector lines
		if (self.cell_y != 0): # is not root
			d.line((bottom_center, (bottom_center[0], bottom_center[1] + BRACKET_H1)), fill=1, width = 0)
			if (self.cell_x % 2): # is a righthand cell
				d.line(
					((bottom_center[0], bottom_center[1] + BRACKET_H1), (bottom_center[0] - BRACKET_W1, bottom_center[1] + BRACKET_H1)), 
					fill=1, 
					width = 0
				)
				d.line(
					((bottom_center[0] - BRACKET_W1, bottom_center[1] + BRACKET_H1), (bottom_center[0] - BRACKET_W1, bottom_center[1] + 2 * BRACKET_H1)),
					fill=1, 
					width = 0
				)
			else:
				d.line(
					((bottom_center[0], bottom_center[1] + BRACKET_H1), (bottom_center[0] + BRACKET_W1, bottom_center[1] + BRACKET_H1)), 
					fill=1, 
					width = 0
				)
				d.line(
					((bottom_center[0] + BRACKET_W1, bottom_center[1] + BRACKET_H1), (bottom_center[0] + BRACKET_W1, bottom_center[1] + 2 * BRACKET_H1)),
					fill=1, 
					width = 0
				)

		return (top_center, bottom_center)

## Root person
ROOT_POINTER = '@I6000000030614622505@' 
ROOT_COORDS = (10, 40)

##### STEP 1 #####
## Read in GEDCOM file

# Path to your `.ged` file
file_path = ''

# Initialize the parser
gedcom_parser = Parser()

# Parse your file
# file_path = os.path.abspath('data/sample.ged')
file_path = os.path.abspath('data/geni_tree_2022_01_02.ged')

gedcom_parser.parse_file(file_path)

# Start at the root child
root_child = gedcom_parser.get_element_dictionary()[ROOT_POINTER]

##### STEP 2 #####
## Create list of dicts {pathcode, element}
print(FamilyMember(gedcom_parser, root_child))

# Recursively get all ancestors
tree_list = FamilyMember(gedcom_parser, root_child).build_tree_list()

FamilyMember(gedcom_parser, root_child).print_tree_list(tree_list)

# Assign cell coordinates to each element of treelist
for loc, element in tree_list:
	element.ancestry_string_to_cell_coordinates(loc)

# Get height and width of tree
metalist = [len(loc) + 1 for loc, element in tree_list]
height = max(metalist)
max_width = 2 ** (height - 1) 
print('Height = {}'.format(height))
print('Width = {}'.format(max_width))

# Transform cell coordinates to drawing coordinate pcts
for loc, element in tree_list:
	element.cell_coordinates_to_drawing_coordinates_pcts(height)

##### STEP 3 #####
## Prep drawing
# Prepare new Image object
BORDER_LENGTH_X = 120
BORDER_LENGTH_Y = 60

w, h = int(2.5 * BORDER_LENGTH_X * max_width), int(1.8 * BORDER_LENGTH_Y * height)
origin_x = ROOT_COORDS[0]
origin_y = ROOT_COORDS[1]

# Create empty image
out = Image.new("RGB", (w, h), (255, 255, 255))
d = ImageDraw.Draw(out)

print("**********")
# Add all people
for loc, element in tree_list:
	print("Drawing: {} at ({}, {})".format(element, element.drawing_pct_x * w, element.drawing_pct_y * h))
	element.drawMe(element.drawing_pct_x * w, element.drawing_pct_y * h)

out.show()

quit("Complete")

######
## TODO Roadmap
## - Siblings
## - Downwards from root
## - Backgrounds
## - More metadata per person
