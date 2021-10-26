wget https://raw.githubusercontent.com/CYGNO-publications/airtable/master/authors.py
mkdir data                                                                          
cd data 
wget https://raw.githubusercontent.com/CYGNO-publications/airtable/master/data/authorlist.csv
cd -
python authors.py POSlatex --datafile data/authorlist.csv
