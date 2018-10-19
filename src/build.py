import sys
import os
import subprocess
import json
from collections import OrderedDict

def git_info() -> OrderedDict:
	# HEAD のコミット情報を取得
	format = '--pretty=format:%H%n%s%n%ai%n%aI%n%at'
	result = subprocess.run(['git', 'show', '--no-patch', format],
		check=True, stdout=subprocess.PIPE)
	outline = result.stdout.decode(sys.stdout.encoding)
	hash, subject, date, date_iso8601, date_unix, *rest = outline.split('\n')

	head = OrderedDict()
	head['hash'] = hash
	head['subject'] = subject
	head['date'] = date
	head['date_iso8601'] = date_iso8601
	head['date_unix'] = date_unix

	# data/ の最新のコミット情報を取得
	format = '--pretty=format:%H%n%s%n%ai%n%aI%n%at'
	result = subprocess.run(['git', 'log', '-n1', format, '--', '../data'],
		check=True, stdout=subprocess.PIPE)
	outline = result.stdout.decode(sys.stdout.encoding)

	data = OrderedDict()
	data['hash'] = hash
	data['subject'] = subject
	data['date'] = date
	data['date_iso8601'] = date_iso8601
	data['date_unix'] = date_unix

	return { 'version': { 'repository': head, 'data': data } }

# 1つの JSON ファイルにまとめる
def merge_all(files: list, outfile: str):
	merged = OrderedDict()
	merged.update(git_info())
	for file_name in files:
		with open(file_name, 'r') as f:
			print('Processing...', file_name)
			# ファイルを1つ読んでパースする
			part = json.load(f, object_pairs_hook=OrderedDict)
			for k, v in part.items():
				# キーが既にある場合は値の配列を合成する
				if k in merged:
					merged[k].extend(part[k])
				# 無い場合は新たに追加する
				else:
					merged[k] = part[k]
	print('Version info')
	print(json.dumps(merged['version']))
	print('Writing...', outfile)
	with open(outfile, 'w') as f:
		json.dump(merged, f, separators=(',', ':'), ensure_ascii=False)
	print('complete!')

# 圧縮する
def compress(file_in: str, file_out: str):
	# 最高圧縮率で zip する
	# 出力はリダイレクトせずそのまま流す
	print('Run zip...')
	subprocess.run(['zip', '-9', file_out, file_in], check=True)
	print('complete!')

def main(argv: list):
	# スクリプトの場所を起点に dist ディレクトリを作成して移動する
	dist_dir = os.path.join(os.path.dirname(__file__), '../dist')
	os.makedirs(dist_dir, exist_ok=True)
	os.chdir(dist_dir)

	# ソースファイルリスト
	srcs = [
		'../data/formats/formats.json',
		'../data/sets/sets.json',
		'../data/types/types.json',
	]
	for i in range(0x100):
		srcs.append('../data/cards/{:02x}.json'.format(i))

	# 出力ファイル
	merged_file = 'mtgdb.json'
	compressed_file = 'mtgdb.zip'

	merge_all(srcs, merged_file)
	compress(merged_file, compressed_file)

# entry point
main(sys.argv)
