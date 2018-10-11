import subprocess
import json

card_list = []

# 空リストが返ってくるまで全ページ読む
page = 1
page_size = 100
urlfmt = 'https://api.magicthegathering.io/v1/cards?page={}&pageSize={}'
while True:
	url = urlfmt.format(page, page_size)
	result = subprocess.run(['curl', url],
		check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

	# JSON パースして cards プロパティからカード配列を取得
	page_json = json.loads(result.stdout.decode('utf-8'))
	list_in_page = page_json['cards']
	# 長さ0なら終了
	if len(list_in_page) == 0:
		break
	# card_list に追加
	card_list.extend(list_in_page)

	print('{}...\n'.format(page * page_size))
	page += 1

# id プロパティで全体をソート
card_list.sort(key=itemgetter('id'))

with open('all.json', 'w') as f:
	json.dump({'cards': card_list}, f)
