import json
import sys
import os

kvstore = {}

def loadjson(merged_file):
    with open(merged_file, 'r', encoding="utf-8") as f:
        count = 0
        print('Processing...', merged_file)
        json_obj = json.load(f) # , object_pairs_hook=OrderedDict
        for k in json_obj["cards"]:
            #print(k["name"])
            if k["name"] in kvstore:
                kvstore[k["name"]].append(k)
            else:
                kvstore[k["name"]] = [k]
                #if (count % 1000 == 0):
                    #print(k["name"])
            count = count + 1
        return json_obj

def findimage(json_object, name):
    imagelist = []
    print(name + ":")
    if (name in kvstore):
        for x in kvstore[name]:
            if ("imageUrl" in x):
                imagelist.append(x["imageUrl"])
                #print(x["imageUrl"])
        print("\tadded URLs to list")
    print("\tdone with: " + name)
    return imagelist

def getdecklist():
    deck = []
    with open('DeckList') as f:
        for line in f:
            deck.append(line.strip())
    return deck

def main(argv: list):
    dist_dir = os.path.join(os.path.dirname(__file__), '../dist')
    try:
        os.chdir(dist_dir)
    except:
        print("Data does not exist")
        return

    merged_file = 'mtgdb.json'
    json_obj = loadjson(merged_file)
    decklist = getdecklist()
    print("Decklist: ")
    print(decklist)
    deckdict = {}

    #name = "Sphinx of the Final Word"
    #name = "Goblin King"
    for card in decklist:
        deckdict[card] = findimage(json_obj, card)
    print(deckdict)

# entry point
main(sys.argv)