from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

def get_resource_group_details(subscription_id, resource_group_name):
    # Authenticate using DefaultAzureCredential
    credential = DefaultAzureCredential()

    # Create a ResourceManagementClient instance
    resource_client = ResourceManagementClient(credential, subscription_id)

    # Get the resource group details
    resource_group = resource_client.resource_groups.get(resource_group_name)

    # Print resource group details
    print("Resource Group Details:")
    print(f"Name: {resource_group.name}")
    print(f"Location: {resource_group.location}")
    print(f"ID: {resource_group.id}")
    print(f"Tags: {resource_group.tags}")
    print(f"Properties: {resource_group.properties}")

    return resource_group

# Example usage
if __name__ == "__main__":
    subscription_id = 'your_subscription_id'
    resource_group_name = 'your_resource_group_name'
    get_resource_group_details(subscription_id, resource_group_name)
