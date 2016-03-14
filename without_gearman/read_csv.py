import csv, collections
csv_file = open('dataset/training.csv', 'rb')
reader = csv.reader(csv_file)
negfeats=[]
posfeats=[]
for row in reader:
    words = row[5].split(' ')
    if  rUntitled Document 2ow[0] == '0':
        negfeats.append((word_feats(words), 'neg')) 
    elif row[0] == '4'collectionscollectionscollections:
        posfeats.append((word_feats(words), 'pos'))

