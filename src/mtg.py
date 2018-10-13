import sys
import os
import subprocess
import json
import bisect
import collections
from time import sleep
from operator import itemgetter

def fetch_all_cards(page_max):
	card_list = []

	# 空リストが返ってくるまで全ページ読む
	page = 1
	page_size = 100
	urlfmt = 'https://api.magicthegathering.io/v1/cards?page={}&pageSize={}'
	while page <= page_max:
		url = urlfmt.format(page, page_size)
		err_count = 0
		retry = True
		while retry:
			retry = False
			try:
				result = subprocess.run(['curl', url], check=True,
					stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
			except subprocess.CalledProcessError:
				retry = True
				err_count += 1
				if err_count >= 5:
					raise
				print('retry...')
				sleep(3)

		# JSON パースして cards プロパティからカード配列を取得
		# 一応キーの順序は保存する
		page_json = json.loads(result.stdout.decode('utf-8'),
			object_pairs_hook=collections.OrderedDict)
		list_in_page = page_json['cards']
		# 長さ0なら終了
		if len(list_in_page) == 0:
			break
		# card_list に追加
		card_list.extend(list_in_page)

		print('{}...'.format(page * page_size))
		page += 1

	return card_list

def main(argv):
	# スクリプトの場所を起点に data ディレクトリに移動する
	os.chdir(os.path.join(os.path.dirname(__file__), '../data/cards'))

	page_max = 0xffff
	if (len(argv) >= 2):
		page_max = int(argv[1])

	# 全カードリスト取得
	all_cards = fetch_all_cards(page_max)
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
		with open('{:02x}.json'.format(i), 'w') as f:
			json.dump({'cards': ranged_cards}, f, indent='\t')
		saved_count += len(ranged_cards)
	# 総数が一致するか確認する
	assert saved_count == len(all_cards)


main(sys.argv)
