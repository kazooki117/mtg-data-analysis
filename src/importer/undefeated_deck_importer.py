import csv

def read_decks(file):
    counts = []
    first = True
    for row in csv.reader(file):
        if first:
            first = False
            continue

        counts.append([int(x) for x in row[1:]])

    return counts

def read_legend(file):
    names = []
    first = True
    for row in csv.reader(file):
        if first:
            first = False
            continue

        names.append(row[1])

    return names




if __name__ == '__main__':
    with open('raw_data_from_contributor/three_zero_trophy_hype/grn_3_0_raw_legend.csv') as f:
        names = read_legend(f)
    with open('raw_data_from_contributor/three_zero_trophy_hype/grn_3_0_raw_deck.csv') as f:
        counts = read_decks(f)


    for deck in counts:
        assert len(names) == len(deck)
        assert sum(deck) >= 40

        print('Deck:')
        for (count, name) in zip(deck, names):
            if count > 0:
                print(f'  {count}x {name}')
        print()
