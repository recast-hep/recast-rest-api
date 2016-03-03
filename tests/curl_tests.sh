#!/bin/sh

set -x
ORCID_ID="0000-0001-7618-844X"
#TOKEN="0dcf5b6b-db8f-4c0b-a87b-b363c6a52d2d"
TOKEN="e350ff99-f7f9-469c-8dc4-855bf690e06a"


echo "Testing GET methods: "

curl -u ${ORCID_ID}:${TOKEN} -H "Content-Type: application/json" -H "Accept: application/json" -X GET http://recast-rest-api.herokuapp.com/users/1

printf "\n \n \n \n"
curl -u ${ORCID_ID}:${TOKEN} -H "Accept: application/json" http://recast-rest-api.herokuapp.com/analysis

printf "\n \n \n \n"
curl -u ${ORCID_ID}:${TOKEN} -H "Accept: application/json" http://recast-rest-api.herokuapp.com/requests

printf "\n \n \n \n"
echo "POST Methods"
printf "\n \n \n \n"
curl -u ${ORCID_ID}:${TOKEN} -H "Content-Type: application/json" -X POST -d '{"name":"xyz","email":"xyz@example.com"}' http://recast-rest-api.herokuapp.com/users

printf "\n \n \n \n"

curl -u ${ORCID_ID}:${TOKEN} -H "Content-Type: application/json" -X POST -d '{"title":"API title test", "collaboration":"ATLAS", "e_print":"test API", "journal":"test API", "doi":"test API", "inspire_URL":"test API", "description": "API POST test description"}' http://recast-rest-api.herokuapp.com/analysis

printf "\n \n \n \n"

curl -u ${ORCID_ID}:${TOKEN} -H "Content-Type: application/json" -X POST -d '{"name": "API test", "description": "API description test"}' http://recast-rest-api.herokuapp.com/run_conditions

printf "\n \n \n \n"

curl -u ${ORCID_ID}:${TOKEN} -H "Content-Type: application/json" -X POST -d '{"description_of_model": "API test model description", "reason_for_request": "API test reason for request", "additional_information": "API test additional information"}' http://recast-rest-api.herokuapp.com/requests

printf "\n \n \n \n"

curl -u ${ORCID_ID}:${TOKEN} -H "Content-Type: application/json" -X POST -d '{"number_of_events": 100, "reference_cross_section": 10, "conditions_description": 10}' http://recast-rest-api.herokuapp.com/basic_requests

printf "\n \n \n \n"

curl -u ${ORCID_ID}:${TOKEN} -H "Content-Type: application/json" -X POST -d '{"title": "API test title", "value":10.2}' http://recast-rest-api.herokuapp.com/parameter_points

printf "\n \n \n \n"

curl -u ${ORCID_ID}:${TOKEN} -H "Content-Type: application/json" -X POST -d '{"file_name": "API_file.txt", "path": "www.apitest.com/API_file.txt"}' http://recast-rest-api.herokuapp.com/lhe_files

printf "\n \n \n \n"

curl -u ${ORCID_ID}:${TOKEN} -H "Content-Type: application/json" -X POST -d '{"lumi_weighted_efficiency": 20.1, "log_likelihood_at_reference": 1.1}' http://recast-rest-api.herokuapp.com/point_responses

printf "\n \n \n \n"

curl -u ${ORCID_ID}:${TOKEN} -H "Content-Type: application/json" -X POST -d '{"overall_efficiency": 23.2, "nominal_luminosity": 12.2, "log_likelihood_at_reference": 12.1, "reference_cross_section": 12.1}' http://recast-rest-api.herokuapp.com/basic_responses

printf "\n \n \n \n"

curl -u ${ORCID_ID}:${TOKEN} -H "Content-Type: application/json" -X POST -d '{"file_name": "API_histo_example.root", "file_path": "/home/path/to/file/from/API", "histo_name": "example_API", "histo_path": "/api/path/to/histo"}' http://recast-rest-api.herokuapp.com/histograms
