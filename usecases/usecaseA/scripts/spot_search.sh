#
# Script for querying the availability of SPOT images 
# through the Sentinel-Hub API.
# 
#
#	Argument $1: CSV file containing DATE;BBOX metadata for the SSL4EO-S12 dataset.
#	Argument $2: Output file to generate with ID;ACQUISITIONID;DATETIME metadata for available SPOT images.
#
# NOTE: Expects a text file called 'credentials' with 2 rows that include Sentinel-Hub credentials.
#
#	First row is USERID
# 	Second row is USERKEY
#
#	e.g.
#		abcdfe
#		xXx$3!xxxxXx^
#


URL="https://services.sentinel-hub.com/api/v1/dataimport/search";
get_token() {
	curl -s -X POST\
		--url https://services.sentinel-hub.com/oauth/token\
		-H "content-type: application/x-www-form-urlencoded"\
		-d "grant_type=client_credentials&client_id=$(sed '1q;d' credentials)"\
		--data-urlencode "client_secret=$(sed '2q;d' credentials)"
}

end=$(date +%s)

if [[ -z $SHTOKEN ]] || [[ $((end-SHTOKENSTART)) -ge $SHTOKENEXPIRESIN ]];
then
	token_response=$(get_token);
	export SHTOKEN=$(echo $token_response | grep -oP "(?<=\"access_token\":\").*(?=\",)");
	export SHTOKENEXPIRESIN=$(echo $token_response | grep -oP "(?<=\"expires_in\":)\d*");
	export SHTOKENSTART=$(date +%s);
fi

request () {

	QUERY=("{
		
		\"provider\": \"AIRBUS\",
		\"bounds\": {
			\"properties\": { \"crs\": \"http://www.opengis.net/def/crs/EPSG/0/4326\" },
			\"bbox\": $1
			},
		\"data\": [
			{
			\"constellation\": \"SPOT\",
			\"dataFilter\": {
				\"timeRange\": {
					\"from\": \"$2\",
					\"to\": \"$3\"
					}
				}
			}
		]
			
		}")
	
	curl -s -X POST\
		-H 'accept: application/json'\
      		-H "Content-Type: application/json"\
 		-H "Authorization: Bearer $SHTOKEN"\
 		-d "$QUERY" "$URL";
	}

end=$(date +%s);


closest_date() {
	
	min=9999999
	i=0
	for date in $@;
	do
		datediff=$((($(date --date "$date" +%s) - $(date --date $datestr +%s))))
		
		if [[ datediff -lt $min ]]
		then
			min=$datediff
			index=$i
		fi

		((i++));

	done;

	echo $index

}


while IFS= read -r row;
do
	datestr=${row%%;*};
	bboxstr=${row##*;};
	from=$(date --date "$datestr -3 days" +%Y-%m-%dT00:00:00Z);
	to=$(date --date "$datestr +3 days" +%Y-%m-%dT00:00:00Z);
	
	response=$(request "$bboxstr" $from $to)
	# response=$(request "$3" $from $to)

	totalResults="totalResults: $(echo $response | grep -oP "(?<=\"totalResults\":)\d*")"
	
	read -a ids < <(echo $response |
		 	grep -oP "(?<=\"id\":)\"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}\"" |
		 	sed s/\"//g | sed -z "s/\n/ /g")
	
	read -a acq_ids < <(echo $response |
        	  	    grep -oP "(?<=\"acquisitionIdentifier\":)\"\w*\"" |
			    sed s/\"//g | sed -z "s/\n/ /g")
	
	read -a dates < <(echo $response |
                          grep -oP "(?<=\"acquisitionDate\":)\"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\"" |
                          sed s/\"//g | sed -z "s/\n/ /g")	
	
	read -a centres < <(echo $response |
                            grep -oP "(?<=\"geometryCentroid\":)\[[0-9\.\,\-]*\]" | sed -z "s/\n/ /g")

	# echo $response
	# echo $totalResults
	
	# declare -p dates
	# declare -p ids
	# declare -p acq_ids
	# declare -p centres
	
	c=$(closest_date ${dates[@]})

	echo "${ids[$c]};${acq_ids[$c]};$datestr;${dates[$c]}" >> $2

	end=$(date +%s);
	if [[ $((end-SHTOKENSTART)) -ge $SHTOKENEXPIRESIN ]]
	then
		token_response=$(get_token)
		export SHTOKEN=$(echo $token_response | grep -oP "(?<=\"access_token\":\").*(?=\",)");
		export SHTOKENEXPIRESIN=$(echo $token_response | grep -oP "(?<=\"expires_in\":)\d*");
		export SHTOKENSTART=$(date +%s);
	fi

done < $1;


