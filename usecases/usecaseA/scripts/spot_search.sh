#
# Script for querying the availability of SPOT images 
# through the Sentinel-Hub API.
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

while IFS= read -r row;
do
	datestr=${row%%;*};
	bboxstr=${row##*;};
	from=$(date --date "$datestr -2 days" +%Y-%m-%dT00:00:00Z);
	to=$(date --date "$datestr +2 days" +%Y-%m-%dT00:00:00Z);
	
	# response=$(request "$bboxstr" $from $to)
	response=$(request "$2" $from $to)

	totalResults="totalResults: $(echo $response | grep -oP "(?<=\"totalResults\":)\d*")"
	ids=$(echo $response | grep -oP nothing)
	
	echo $response |
	grep -oP "(?<=\"acquisitionDate\":)\"\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\dZ\"" |
	sed s/\"//g |
	read -a dates
	
	echo $response
	echo $totalResults
	echo ${dates[@]} ${dates[0]} ${dates[1]} ${#dates[@]}

	end=$(date +%s);
	if [[ $((end-SHTOKENSTART)) -ge $SHTOKENEXPIRESIN ]]
	then
		token_response=$(get_token)
		export SHTOKEN=$(echo $token_response | grep -oP "(?<=\"access_token\":\").*(?=\",)");
		export SHTOKENEXPIRESIN=$(echo $token_response | grep -oP "(?<=\"expires_in\":)\d*");
		export SHTOKENSTART=$(date +%s);
	fi

	break;

done < $1;


