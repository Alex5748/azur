import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

def validate_resource_group(resource_group_name):
    # Retrieve subscription ID from environment variable
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

    # Authenticate using DefaultAzureCredential
    credential = DefaultAzureCredential()

    # Create a ResourceManagementClient instance
    resource_client = ResourceManagementClient(credential, subscription_id)

    try:
        # Get the resource group details
        resource_group = resource_client.resource_groups.get(resource_group_name)
        
        # Check if the resource group name is 'VPXRG'
        if resource_group.name == "VPXRG":
            print(f"The resource group '{resource_group_name}' is a VPXRG (standard).")
            return True
        else:
            print(f"The resource group '{resource_group_name}' is not a VPXRG (standard).")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Example usage
if __name__ == "__main__":
    resource_group_name = 'your_resource_group_name'  # Replace with the actual resource group name
    is_vpxrg = validate_resource_group(resource_group_name)
    print(f"Is the resource group VPXRG: {is_vpxrg}")
