#
# Script for querying the availability of SPOT images 
# through the Sentinel-Hub API.
# 

URL="https://services.sentinel-hub.com/api/v1/dataimport/search";

BBOX=$1;
DATE1=$2;
DATE2=$3;


get_token() {


	curl -X POST\
		--url https://services.sentinel-hub.com/oauth/token\
		-H "content-type: application/x-www-form-urlencoded"\
		-d "grant_type=client_credentials&client_id=$(sed '1q;d' credentials)"\
		--data-urlencode "client_secret=$(sed '2q;d' credentials)"

}


QUERY=(

	"{
	
	'provider': 'AIRBUS',
	'bounds': {

		'BBox': {
		
			'bbox': $BBOX,
			'crs': 4326
			
			}

		},
	'data': [
		{
		'constellation': 'SPOT',
		'dataFilter': {
			'timeRange': {
				'from': $DATE1,
				'to': $DATE2
				}
			}
		}
	]
		
	}"

)


echo $QUERY;

token_response=$(get_token)
token=$(echo $token_response | grep -oP "(?<=\"access_token\":\").*(?=\",)");
time=$(echo $token_response | grep -oP "(?<=\"expires_in\":)\d*");
start=$(date +%s);

sleep 2

end=$(date +%s);

echo $token $time $((end-start))

# curl -X POST -H 'accept: application/json'\
#      	-H "Content-Type: application/json"\
# 	-H "authorization: Bearer $token"\
# 	-d "$QUERY" "$URL";

