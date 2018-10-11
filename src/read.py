import sys
import subprocess
import json
from operator import itemgetter

with open('all.json', 'r') as f:
	all_json = json.load(f)
	card_list = all_json['cards']
	card_list.sort(key=itemgetter('id'))

	for card in card_list:
		print(card['id'])
