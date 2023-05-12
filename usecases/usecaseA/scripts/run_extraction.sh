{ 
	for i in `cat $1`;
	do 
	
		python row_factory.py $i >> $2;

	done
} &

