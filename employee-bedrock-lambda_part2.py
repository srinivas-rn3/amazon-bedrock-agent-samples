import json

def lambda_handler(event, context):
    """
    Lambda handler for a function defined WITHOUT an OpenAPI schema.
    The event structure is simpler.
    """
    # The 'event' object is different and simpler in this mode.
    # It directly tells you which function to run.
    function_to_run = event.get('function', '')
    parameters = event.get('parameters', [])
    
    print(f"Function to run: {function_to_run}")
    print(f"Parameters received: {parameters}")

    response_body = {}

    if function_to_run == 'get_employee_details':
        # Extract the employee_id from the parameters list
        employee_id = next((p['value'] for p in parameters if p['name'] == 'employee_id'), None)

        if employee_id:
            # In a real app, you'd query a database. Here's our mock employee DB.
            mock_employee_db = {
                "E123": {"full_name": "Alice Johnson", "department": "Engineering"},
                "E456": {"full_name": "Bob Williams", "department": "Marketing"},
                "E789": {"full_name": "Charlie Brown", "department": "Engineering"}
            }
            details = mock_employee_db.get(employee_id, {"error": "Employee ID not found"})
            response_body = details
        else:
            response_body = {'error': 'employee_id parameter is missing'}
    else:
        response_body = {'error': f'Unknown function: {function_to_run}'}

    # The response format back to Bedrock is IDENTICAL to the OpenAPI method.
    # This structure does NOT change.
    action_response = {
        'response': {
            "actionGroup": event.get('actionGroup', ''),
            "function": function_to_run,
            "functionResponse": {
                "responseBody": {
                    "TEXT": { # The content type must be TEXT for this simplified method
                        "body": json.dumps(response_body)
                    }
                }
            }
        }
    }
    
    # Final return object for the Lambda
    return {
        'messageVersion': '1.0',
        'response': action_response['response']
    }