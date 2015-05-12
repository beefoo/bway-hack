import csv
import json
import math
import os
import re

SUBSCRIBERS_INPUT_FILE = 'data/subscribers.csv'
ZIPCODES_INPUT_FILE = 'data/new_york_zipcodes.csv'
SEATING_INPUT_FILE = 'data/seating_chart.csv'
OUTPUT_FILE = 'data/subscribers.json'
ZIPCODES_OUTPUT_FILE = 'data/zipcodes.json'

LAT1 = 40.906507
LNG1 = -74.161754
LAT2 = 40.594924
LNG2 = -73.747707

sections = []
subscribers = []
zipcodes = []

def findInList(list, key, value):
	found = False
	for index, item in enumerate(list):
		if item[key] == value:
			found = item
			break
	return found

def indexInList(list, key, value):
	found = -1
	for index, item in enumerate(list):
		if item[key] == value:
			found = index
			break
	return found
	
def is_int(s):
	try:
		int(s)
		return True
	except ValueError:
		return False

def getSeatLetter(_seat_letter):
	seat_letter = 0
	_seat_letter = _seat_letter.lower().replace('box','').replace('(w ch.)','').strip()
	
	# convert seat letter to number
	if is_int(_seat_letter):
		seat_letter = int(_seat_letter)
	else:
		for i, c in enumerate(_seat_letter):
			if i <= 0:
				seat_letter += ord(c) - 96
			else:
				seat_letter += 26
		if seat_letter < 0:
			seat_letter = 0
	
	return seat_letter
	
def getSeatPosition(section, subscriber):
	x = 0
	y = 0
	seat_letter = subscriber['seat_letter']
	seat_number = subscriber['seat_number']
	pos = section['position']
	sx = section['x']
	sy = section['y']
	sw = section['w']
	sh = section['h']
	max_letter = max(section['letters'])
	max_number = max(section['numbers'])
	
	x_percent = (1.0 * seat_number/ max_number)
	y_percent = (1.0 * seat_letter/ max_letter)
	
	if pos == 'left':
		x_percent = (1.0 - 1.0 * seat_letter/ max_letter)
		y_percent = (1.0 * seat_number/ max_number)
	elif pos == 'right':
		x_percent = (1.0 * seat_letter/ max_letter)
		y_percent = (1.0 * seat_number/ max_number)
	
	x = sx + x_percent * sw
	y = sy + y_percent * sh
	
	return {'x': x, 'y': y}

with open(SEATING_INPUT_FILE, 'rb') as f:
	r = csv.reader(f, delimiter=',')
	next(r, None) # remove header
	for _name, _position, _x, _y, _w, _h, _tw, _th in r:
		tw = float(_tw)
		th = float(_th)
		sections.append({
			'name': _name,
			'position': _position,
			'x': float(_x)/tw,
			'y': float(_y)/th,
			'w': float(_w)/tw,
			'h': float(_h)/th,
			'letters': [],
			'numbers': []
		})

with open(ZIPCODES_INPUT_FILE, 'rb') as f:
	r = csv.reader(f, delimiter=',')
	for _zip, _lat, _lng in r:
		lat_x = 1.0 * (LAT1 - float(_lat))/(LAT1 - LAT2)
		lng_y = 1.0 * (float(_lng) - LNG1)/(LNG2 - LNG1)
		index = len(zipcodes)
		if lat_x >= 0 and lng_y >= 0 and lat_x <= 1 and lng_y <= 1:
			zipcodes.append({
				'index': index,
				'code': _zip,
				'lat': lat_x,
				'lng': lng_y
			})

with open(SUBSCRIBERS_INPUT_FILE, 'rb') as f:
	r = csv.reader(f, delimiter=',')
	next(r, None) # remove header
	for _nternational_era_subscriber_book_id, _section, _seat_letter, _seat_number, _price, _requested_change, _year, _series, _standardized_series, _set, _final_address, _original_address, _interim_address_1, _interim_address_2, _interim_address_3, _interim_address_4, _interim_address_5, _interim_address_6, _n53, _n54, _n55, _n56, _n57, _n58, _n59, _n60, _n61, _n62, _n63, _n64, _n65, _n66, _n67, _n68, _n69, _n70, _n71, _n72, _n73, _n74, _n75, _n76, _series_1_first, _series_1_final, _series_1_interim_1, _series_1_interim_2, _series_1_interim_3, _series_1_interim_4, _series_1_interim_5, _series_1__killed_prior_to_the_final_year_of_subscription, _series_2_first, _series_2_final, _series_2_interim_1, _series_2_interim_2, _series_2_interim_3, _series_2_interim_4, _series_2_interim_5, _series_2__killed_prior_to_the_final_year_of_subscription, _series_3_first, _series_3_final, _series_3_interim_1, _series_3_interim_2, _series_3_interim_3, _series_3_interim_4, _series_3_interim_5, _series_3__killed_prior_to_the_final_year_of_subscription, _series_4_first, _series_4_final, _series_4_interim, _series_4_prior_to_the_final_year_of_subscription, _series_5_first, _series_5_final, _series_5_interim in r:
		# search for zipcode
		zipcode = False
		zipcode_match = re.search(r'.*(\d{5}(\-\d{4})?)$', _final_address)
		if zipcode_match != None:
			zipcode = findInList(zipcodes, 'code', zipcode_match.group(1))
			
		# check for box seats
		if "Boxes" in _section or "Loge" in _section and is_int(_seat_number):
			if int(_seat_number) % 2 == 0:
				_section += " right"
			else:
				_section += " left"
		
		# search for section
		section = False
		seat_letter = 0
		seat_number = 0
		section_i = indexInList(sections, 'name', _section)
		if section_i >= 0:
			section = sections[section_i]		
			# determine seat
			seat_letter = getSeatLetter(_seat_letter)
			if is_int(_seat_number):
				seat_number = int(_seat_number)	
			# add if zipcode and section is valid
			if zipcode and seat_letter > 0 and seat_number > 0:
				
				sections[section_i]['letters'].append(seat_letter)
				sections[section_i]['numbers'].append(seat_number)
				subscribers.append({
					'section_i': section_i,
					'seat_letter': seat_letter,
					'seat_number': seat_number,
					'zip_i': zipcode['index']
				})

print "Found "+str(len(subscribers))+" valid New York subscribers"

data = []


# Get x/y coordinates
for i, subscriber in enumerate(subscribers):
	
	# Determine seat locations
	section = sections[subscriber['section_i']]
	seat = getSeatPosition(section, subscriber)
	
	if seat['x'] >= 0 and seat['y'] >= 0 and seat['x'] <= 1 and seat['y'] <= 1:
		data.append({
			'x': round(seat['x'], 4),
			'y': round(seat['y'], 4),
			'z': subscriber['zip_i']
		})

with open(OUTPUT_FILE, 'w') as outfile:
	json.dump(data, outfile)
	print "Wrote to file: " + OUTPUT_FILE

# Output zipcode data
zipcode_data = []
for z in zipcodes:
	zipcode_data.append({
		'i': z['index'],
		'x': round(z['lng'], 4),
		'y': round(z['lat'], 4)
	})
	
with open(ZIPCODES_OUTPUT_FILE, 'w') as outfile:
	json.dump(zipcode_data, outfile)
	print "Wrote to file: " + ZIPCODES_OUTPUT_FILE

