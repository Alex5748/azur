from azure.identity import InteractiveBrowserCredential
from msgraph.core import GraphClient

def get_signed_in_user_object_id():
    # Initialize the InteractiveBrowserCredential
    credential = InteractiveBrowserCredential(client_id='YOUR_CLIENT_ID')

    # Initialize the GraphClient
    client = GraphClient(credential=credential)

    # Make a request to the /me endpoint to get the signed-in user's details
    user = client.get('/me')

    # Extract the object ID from the user's details
    object_id = user.json().get('id')
    
    return object_id

if __name__ == "__main__":
    user_object_id = get_signed_in_user_object_id()
    print(f"The signed-in user's object ID is: {user_object_id}")
