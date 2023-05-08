{ for i in `cat $1`; do ./row_factory.py $i >> $2; done } &
