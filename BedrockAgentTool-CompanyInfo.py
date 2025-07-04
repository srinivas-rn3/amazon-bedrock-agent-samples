import json

def lambda_handler(event, context):
    """
    This is the central handler for our agent's tools.
    This version includes robust, case- and space-insensitive lookups.
    """
    response_body = {}
    action_group = event.get('actionGroup', '')
    api_path = event.get('apiPath', '')

    # Route to the correct function based on the apiPath
    if api_path == '/get_user_status':
        parameters = event.get('parameters', [])
        user_id = next((p['value'] for p in parameters if p['name'] == 'user_id'), None)
        
        if user_id:
            mock_user_db = {
                "user100": "Active",
                "user200": "On-Leave",
                "user300": "Inactive"
            }
            status = mock_user_db.get(user_id, "User Not Found")
            response_body = {'status': status}
        else:
            response_body = {'error': 'user_id parameter is missing'}

    elif api_path == '/get_project_code':
        parameters = event.get('parameters', [])
        project_name_param = next((p for p in parameters if p['name'] == 'project_name'), None)
        
        if project_name_param:
            raw_project_name = project_name_param['value']
            
            # This is our mock project database
            mock_project_db = {
                "ProjectPhoenix": "PX-001",
                "ProjectTitan": "TN-550",
                "ProjectNebula": "NB-204"
            }
            
            # --- THE FIX IS HERE ---
            # Normalize the input from the agent to be lowercase and have no spaces.
            # "Project Titan" becomes "projecttitan"
            normalized_input = raw_project_name.lower().replace(" ", "")
            
            found_code = "Project Not Found"  # Default if we find no match
            
            # Loop through our database and normalize its keys in the same way before comparing
            for key, value in mock_project_db.items():
                normalized_key = key.lower().replace(" ", "") # "ProjectTitan" becomes "projecttitan"
                if normalized_key == normalized_input:
                    found_code = value
                    break # Found a match, no need to keep searching
            
            response_body = {'project_code': found_code}
        else:
            response_body = {'error': 'project_name parameter is missing'}
            
    else:
        response_body = {'error': f'Unknown API Path: {api_path}'}

    # The required response format for Bedrock Agents
    action_response = {
        'actionGroup': action_group,
        'apiPath': api_path,
        'httpMethod': event.get('httpMethod', 'GET'),
        'httpStatusCode': 200,
        'responseBody': {
            "application/json": {
                "body": json.dumps(response_body) 
            }
        }
    }
    
    return {
        'messageVersion': '1.0',
        'response': action_response
    }