import json

# This is our MOCK Customer Relationship Management (CRM) database.
MOCK_CRM_DB = {
    "global tech inc.": {
        "account_id": "acc-12345",
        "key_contacts": [
            {"name": "Jane Doe", "title": "CTO", "email": "jane.doe@globaltech.example.com"},
            {"name": "John Smith", "title": "Director of IT", "email": "john.smith@globaltech.example.com"}
        ],
        "open_opportunities": [
            {"name": "Project Titan Cloud Migration", "stage": "Proposal Sent", "value": 450000},
            {"name": "Analytics Platform Expansion", "stage": "Initial Discussion", "value": 120000}
        ]
    },
    "another company llc": {
        "account_id": "acc-67890",
        "key_contacts": [{"name": "Emily White", "title": "CEO"}],
        "open_opportunities": []
    }
}

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")

    response_body = {}
    status_code = 200

    try:
        request_body = json.loads(event.get('body', '{}'))
        parameters = request_body.get('properties', [])

        company_name_param = next((p for p in parameters if p['name'] == 'companyName'), None)
        contact_name_param = next((p for p in parameters if p['name'] == 'contactName'), None)

        customer_data = None

        if company_name_param:
            # Logic for when the company name is provided directly
            company_name = company_name_param.get('value', '').lower()
            print(f"Looking up data for company: {company_name}")
            customer_data = MOCK_CRM_DB.get(company_name)

        elif contact_name_param:
            # NEW LOGIC: If contact name is provided, find their company
            contact_name = contact_name_param.get('value', '')
            print(f"Searching for contact: {contact_name}")
            for company, data in MOCK_CRM_DB.items():
                for contact in data.get('key_contacts', []):
                    if contact.get('name', '').lower() == contact_name.lower():
                        print(f"Found contact {contact_name} at company {company}")
                        customer_data = data
                        break
                if customer_data:
                    break
        
        if customer_data:
            response_body = customer_data
        else:
            status_code = 404
            response_body = {"error": "Could not find a matching company or contact."}

    except Exception as e:
        print(f"Error: {e}")
        status_code = 500
        response_body = {"error": "An internal error occurred."}
        
    final_response = {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get('actionGroup', ''),
            "apiPath": event.get('apiPath', ''),
            "httpMethod": event.get('httpMethod', ''),
            "httpStatusCode": status_code,
            "responseBody": {
                "application/json": {
                    "body": json.dumps(response_body)
                }
            }
        }
    }

    return final_response