from azure.identity import InteractiveBrowserCredential
import requests

def get_signed_in_user_object_id():
    # Initialize the InteractiveBrowserCredential
    credential = InteractiveBrowserCredential(client_id='YOUR_CLIENT_ID')

    # Get an access token
    token = credential.get_token('https://graph.microsoft.com/.default')

    # Prepare the request headers with the access token
    headers = {
        'Authorization': f'Bearer {token.token}',
        'Accept': 'application/json'
    }

    # Make a request to the /me endpoint to get the signed-in user's details
    response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        user = response.json()
        object_id = user.get('id')
        return object_id
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    user_object_id = get_signed_in_user_object_id()
    print(f"The signed-in user's object ID is: {user_object_id}")
