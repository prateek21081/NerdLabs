import csv

print("INSERT INTO review VALUES")
with open('/tmp/review.csv') as csvfile:
    records = csv.reader(csvfile)
    for rec in records:
        print(tuple(rec), ',')