import sys
import os
import subprocess
import json
from collections import OrderedDict
import zipfile

def git_info() -> OrderedDict:
	"""git コマンドでバージョン情報を取得する"""
	# HEAD のコミット情報を取得
	format = '--pretty=format:%H%n%s%n%ai%n%aI%n%at'
	result = subprocess.run(['git', 'show', '--no-patch', format],
		check=True, stdout=subprocess.PIPE)
	outline = result.stdout.decode(sys.stdout.encoding)
	hash, subject, date, date_iso8601, date_unix, *rest = outline.split('\n')

	# 直近のタグ-タグからのコミット数-'g'hash-dirty?
	# git describe --dirty --tags --always
	result = subprocess.run(
		['git', 'describe', '--dirty', '--tags', '--always'],
		check=True, stdout=subprocess.PIPE)
	outline = result.stdout.decode(sys.stdout.encoding)
	describe, *rest = outline.split('\n')

	head = OrderedDict()
	head['describe'] = describe
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
	hash, subject, date, date_iso8601, date_unix, *rest = outline.split('\n')

	data = OrderedDict()
	data['hash'] = hash
	data['subject'] = subject
	data['date'] = date
	data['date_iso8601'] = date_iso8601
	data['date_unix'] = date_unix

	result = OrderedDict()
	result['repository'] = head
	result['data'] = data
	return OrderedDict([('version', result)])

def merge_all(version: OrderedDict, files: list, outfile: str, verfile: str):
	"""1つの JSON ファイルにまとめる"""
	merged = OrderedDict()
	merged.update(version)
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
	# git バージョン情報の表示と書き出し
	print('Version info:', verfile)
	print(json.dumps(merged['version']))
	with open(verfile, 'w') as f:
		json.dump(version, f, indent='\t', ensure_ascii=False)
	# コンパクトファイルの書き出し
	print('Writing...', outfile)
	with open(outfile, 'w') as f:
		json.dump(merged, f, separators=(',', ':'), ensure_ascii=False)
	print('complete!')

def compress(file_in: str, file_out: str):
	"""圧縮する"""
	# 最高圧縮率で zip する
	# 出力はリダイレクトせずそのまま流す
	print('Create zip...', file_out)
	with zipfile.ZipFile(file_out, 'w', compression=zipfile.ZIP_DEFLATED) as zip:
		zip.write(file_in)
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
	version_file = 'version.json'
	compressed_file = 'mtgdb.zip'

	version = git_info()
	merge_all(version, srcs, merged_file, version_file)
	compress(merged_file, compressed_file)

# entry point
main(sys.argv)
