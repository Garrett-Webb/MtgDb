import subprocess
import json
from time import sleep
from operator import itemgetter

card_list = []

# 空リストが返ってくるまで全ページ読む
page = 1
page_size = 100
urlfmt = 'https://api.magicthegathering.io/v1/cards?page={}&pageSize={}'
while True:
	url = urlfmt.format(page, page_size)
	err_count = 0
	retry = True
	while retry:
		retry = False
		try:
			result = subprocess.run(['curl', url],
				check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
		except subprocess.CalledProcessError:
			retry = True
			err_count += 1
			if err_count >= 5:
				raise
			print('retry...')
			sleep(3)

	# JSON パースして cards プロパティからカード配列を取得
	page_json = json.loads(result.stdout.decode('utf-8'))
	list_in_page = page_json['cards']
	# 長さ0なら終了
	if len(list_in_page) == 0:
		break
	# card_list に追加
	card_list.extend(list_in_page)

	print('{}...'.format(page * page_size))
	page += 1

# id プロパティで全体をソート
card_list.sort(key=itemgetter('id'))

with open('all.json', 'w') as f:
	json.dump({'cards': card_list}, f)
