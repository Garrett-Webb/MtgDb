import sys
import os
import subprocess
import json
import bisect
from collections import OrderedDict
from time import sleep
from operator import itemgetter
import urllib.request

def http_json(url: str) -> OrderedDict:
	"""HTTP GET して JSON オブジェクトにパースして返す"""
	req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	err_count = 0
	retry = True
	while retry:
		retry = False
		try:
			with urllib.request.urlopen(req) as res:
				# stdout を UTF-8 デコードして JSON パースして返す
				# 一応キーの順序は保存する
				src = res.read().decode('utf-8')
				return json.loads(src, object_pairs_hook=OrderedDict)
		except urllib.error.URLError:
			# 3秒待ってリトライする
			# 何回もエラーになるようなら例外をそのまま投げる
			retry = True
			err_count += 1
			if err_count >= 5:
				raise
			print('retry...')
			sleep(3)

def fetch_all_cards(page_max: int) -> list:
	"""100枚ずつ読んで cards 配列プロパティを1つの配列にして返す"""
	card_list = []

	# 空リストが返ってくるまで全ページ読む
	page = 1
	page_size = 100
	urlfmt = 'https://api.magicthegathering.io/v1/cards?page={}&pageSize={}'
	while page <= page_max:
		url = urlfmt.format(page, page_size)
		# cards プロパティからカード配列を取得
		page_json = http_json(url)
		list_in_page = page_json['cards']#.encode('utf-8')
		# 長さ0なら終了
		if len(list_in_page) == 0:
			break
		# card_list に追加
		card_list.extend(list_in_page)

		print('{}...'.format(page * page_size))
		page += 1

	return card_list

def cards_main():
	"""全カードリストを取得して保存"""
	all_cards = fetch_all_cards(0xffff)
	# id プロパティで全体をソート
	all_cards.sort(key=itemgetter('id'))

	saved_count = 0
	# 二分探索のため、id プロパティのみの配列を作る
	all_ids = [card['id'] for card in all_cards]
	# i = [0x00 - 0xff]
	for i in range(0x100):
		# 16進文字列化して辞書順での切れ目のインデックスを調べる
		# 'ff....' の右端は 'ff' よりも後ろの値で検索する
		hexstr = format(i, '02x')
		hexstr_next = format(i + 1, '02x')
		if i == 0xff:
			hexstr_next = 'gg'
		# [left, right)
		left = bisect.bisect_left(all_ids, hexstr)
		right = bisect.bisect_left(all_ids, hexstr_next)
		# 得たインデックスをカードリストに適用して抜き出す
		ranged_cards = all_cards[left:right]
		# 先頭2ケタのファイル名で保存
		with open('cards/{:02x}.json'.format(i), 'w', encoding="utf-8") as f:
			json.dump({'cards': ranged_cards}, f,
				indent='\t', ensure_ascii=False)
		saved_count += len(ranged_cards)
	# 総数が一致するか確認する
	assert saved_count == len(all_cards)

def formats_main():
	"""全フォーマットデータを取得して保存"""
	url = 'https://api.magicthegathering.io/v1/formats'
	formats_json = http_json(url)
	with open('formats/formats.json', 'w', encoding="utf-8") as f:
		json.dump(formats_json, f, indent='\t', ensure_ascii=False)

def sets_main():
	"""全カードセットデータを取得して保存"""
	url = 'https://api.magicthegathering.io/v1/sets'
	sets_json = http_json(url)
	with open('sets/sets.json', 'w', encoding="utf-8") as f:
		json.dump(sets_json, f, indent='\t', ensure_ascii=False)

def types_main():
	"""全カードタイプ(サブタイプ、特殊タイプを含む)を取得して保存"""
	url = 'https://api.magicthegathering.io/v1/types'
	types_json = http_json(url)
	url = 'https://api.magicthegathering.io/v1/subtypes'
	subtypes_json = http_json(url)
	url = 'https://api.magicthegathering.io/v1/supertypes'
	supertypes_json = http_json(url)

	merged = OrderedDict([
		('types',		types_json['types']),
		('subtypes',	subtypes_json['subtypes']),
		('supertypes',	supertypes_json['supertypes'])])
	with open('types/types.json', 'w', encoding="utf-8") as f:
		json.dump(merged, f, indent='\t', ensure_ascii=False)

def main(argv: list):
	# スクリプトの場所を起点に data ディレクトリに移動する
	os.chdir(os.path.join(os.path.dirname(__file__), '../data'))

	help_exit = 'help' in argv
	enable_types = (len(argv) <= 1 or 'types' in argv)
	enable_formats = (len(argv) <= 1 or 'formats' in argv)
	enable_sets = (len(argv) <= 1 or 'sets' in argv)
	enable_cards = (len(argv) <= 1 or 'cards' in argv)

	if help_exit:
		print('Usage: {} [task1 task2 ...]'.format(argv[0]))
		print('Tasks: types formats sets cards')
		print('If no tasks are specified, run all tasks')

	if enable_types:
		types_main()
	if enable_formats:
		formats_main()
	if enable_sets:
		sets_main()
	if enable_cards:
		cards_main()

# entry point
main(sys.argv)
