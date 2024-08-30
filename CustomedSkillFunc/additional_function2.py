import logging
import azure.functions as func

bp = func.Blueprint()

@bp.function_name("AdditionalHTTPFunction")
@bp.route(route="brandnewroute")
def test_function(req:func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    return func.HttpResponse("wow hello this worked!!!", status_code=200)


# def main(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')

#     try:
#         logging.info(f"Request: {req}")
#         req_body = req.get_json()
#         logging.info(f"Request Body: {req_body}")
#         logging.info(f"length of values: {len(req_body['values'])}")

#         if 'values' not in req_body or len(req_body['values']) == 0:
#             logging.error("Reqeust body does not contain 'values' or 'values' is empty")
#             return func.HttpResponse(
#                 "Invalid request body",
#                 status_code=400
#             )

#         final_data = {"values":[]}

#         for record in req_body['values']:
#             if 'recordId' not in record or 'data' not in record:
#                 logging.error("record does not contain 'recordId" or 'data')
#                 return func.HttpResponse(
#                     "Invalid request body: missing 'recordId' or 'data'",
#                     status_code=400
#                 )
            
#             recordId = record['recordId']
#             data = record['data']

#             # 
#             persons = data.get('persons',[])
#             logging.info(f"Persons: {persons}")

#             #
#             locations = data.get('locations',[])
#             logging.info(f"locations: {locations}")

#             organizations = data.get('organizations',[])
#             logging.info(f"Organizations: {organizations}")

#             quantities = data.get('quantities',[])
#             logging.info(f"quantities: {quantities}")

#             dateTimes = data.get('dateTimes',[])
#             logging.info(f"dateTimes: {dateTimes}")

#             urls = data.get('urls',[])
#             logging.info(f"urls: {urls}")

#             emails = data.get('emails',[])
#             logging.info(f"emails: {emails}")

#             personTypes = data.get('personTypes',[])
#             logging.info(f"personTypes: {personTypes}")

#             events = data.get('events',[])
#             logging.info(f"events: {events}")

#             products = data.get('products',[])
#             logging.info(f"Products: {products}")

#             skills = data.get('skills',[])
#             logging.info(f"skills: {skills}")

#             addresses = data.get('addresses',[])
#             logging.info(f"events: {addresses}")

#             ipAddresses = data.get('ipAddresses',[])
#             logging.info(f"ipAddresses: {ipAddresses}")

#             merged_text = persons + locations + organizations + quantities + dateTimes + urls + emails + personTypes + events + products + skills + addresses + ipAddresses 
#             meta_data = {'mergedText': merged_text}

#             final_data["values"].append({"recordId":recordId,"data":meta_data})

#         logging.info(f"Final Data: {final_data}")

#         return func.HttpResponse(
#             json.dumps(final_data),
#             status_code=200,
#             mimetype="application/json"
#         )

#     except Exception as e:
#         logging.error(f"Error: {e}")
#         return func.HttpResponse(
#             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
#             status_code=200
#     )
