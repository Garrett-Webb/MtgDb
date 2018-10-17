import sys
import os
import subprocess
import json
from collections import OrderedDict

# 1つの JSON ファイルにまとめる
def merge_all(files: list, outfile: str):
	merged = OrderedDict()
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
	print('Writing...', outfile)
	with open(outfile, 'w') as f:
		json.dump(merged, f, separators=(',', ':'))
	print('complete!')

# 圧縮する
def compress(file_in: str, file_out: str):
	# not implemented
	pass

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

	merge_all(srcs, 'mtgdb.json')
	compress()

# entry point
main(sys.argv)
