# Script to deploy row_factory.py over input list of ssl4eo-s12 directories.

for i in `cat $1`;
do 

	python row_factory.py $i >> $2;
	
done;

