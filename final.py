import os
import uuid
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.authorization.models import RoleAssignmentCreateParameters
from msgraph.core import GraphClient

# Function to get signed-in user's object ID
def get_signed_in_user_object_id():
    credential = InteractiveBrowserCredential(client_id='YOUR_CLIENT_ID')
    client = GraphClient(credential=credential)
    user = client.get('/me')
    object_id = user.json().get('id')
    return object_id

# Function to get resource group details
def get_resource_group_details(subscription_id, resource_group_name):
    credential = DefaultAzureCredential()
    resource_client = ResourceManagementClient(credential, subscription_id)
    resource_group = resource_client.resource_groups.get(resource_group_name)
    print("Resource Group Details:")
    print(f"Name: {resource_group.name}")
    print(f"Location: {resource_group.location}")
    print(f"ID: {resource_group.id}")
    print(f"Tags: {resource_group.tags}")
    print(f"Properties: {resource_group.properties}")
    return resource_group

# Function to validate resource group
def validate_resource_group(resource_group_name):
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    credential = DefaultAzureCredential()
    resource_client = ResourceManagementClient(credential, subscription_id)
    try:
        resource_group = resource_client.resource_groups.get(resource_group_name)
        if resource_group.name == "VPXRG":
            print(f"The resource group '{resource_group_name}' is a VPXRG (standard).")
            return True
        else:
            print(f"The resource group '{resource_group_name}' is not a VPXRG (standard).")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Function to check role assignment
def check_role_assignment(resource_group_name, principal_id, role_definition_name):
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    credential = DefaultAzureCredential()
    authorization_client = AuthorizationManagementClient(credential, subscription_id)
    role_assignments = authorization_client.role_assignments.list_for_scope(
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
    )
    role_definition_id = None
    role_definitions = authorization_client.role_definitions.list(
        scope=f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}",
        filter="roleName eq '{}'".format(role_definition_name)
    )
    for role in role_definitions:
        if role.role_name == role_definition_name:
            role_definition_id = role.id
            break
    if role_definition_id is None:
        print(f"Role definition '{role_definition_name}' not found.")
        return False
    for role_assignment in role_assignments:
        if role_assignment.principal_id == principal_id and role_assignment.role_definition_id == role_definition_id:
            print(f"Principal {principal_id} has the role '{role_definition_name}' in the resource group '{resource_group_name}'.")
            return True
    print(f"Principal {principal_id} does not have the role '{role_definition_name}' in the resource group '{resource_group_name}'.")
    return False

# Function to verify user membership
def verify_user_membership(user_id, group_id):
    credential = DefaultAzureCredential()
    client = GraphClient(credential=credential)
    endpoint = f"/groups/{group_id}/members/{user_id}/$ref"
    try:
        response = client.get(endpoint)
        if response.status_code == 204:
            print(f"User {user_id} is a member of the group {group_id}.")
            return True
        else:
            print(f"User {user_id} is not a member of the group {group_id}.")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Function to check SPN membership or ownership
def check_spn_membership_or_ownership(spn_id, group_id):
    credential = DefaultAzureCredential()
    client = GraphClient(credential=credential)
    membership_endpoint = f"/groups/{group_id}/members/{spn_id}/$ref"
    is_member = False
    try:
        membership_response = client.get(membership_endpoint)
        if membership_response.status_code == 204:
            print(f"SPN {spn_id} is a member of the group {group_id}.")
            is_member = True
        else:
            print(f"SPN {spn_id} is not a member of the group {group_id}.")
    except Exception as e:
        print(f"An error occurred while checking membership: {e}")
    ownership_endpoint = f"/groups/{group_id}/owners/{spn_id}/$ref"
    is_owner = False
    try:
        ownership_response = client.get(ownership_endpoint)
        if ownership_response.status_code == 204:
            print(f"SPN {spn_id} is an owner of the group {group_id}.")
            is_owner = True
        else:
            print(f"SPN {spn_id} is not an owner of the group {group_id}.")
    except Exception as e:
        print(f"An error occurred while checking ownership: {e}")
    return is_member, is_owner

# Function to get role definition ID
def get_role_definition_id(authorization_client, scope, role_name):
    role_definitions = authorization_client.role_definitions.list(
        scope=scope,
        filter=f"roleName eq '{role_name}'"
    )
    for role_definition in role_definitions:
        if role_definition.role_name == role_name:
            return role_definition.id
    return None

# Function to check and assign role
def check_and_assign_role(spn_id, resource_group_name, subscription_id, role_name):
    credential = DefaultAzureCredential()
    authorization_client = AuthorizationManagementClient(credential, subscription_id)
    resource_client = ResourceManagementClient(credential, subscription_id)
    resource_group = resource_client.resource_groups.get(resource_group_name)
    scope = resource_group.id
    role_definition_id = get_role_definition_id(authorization_client, scope, role_name)
    if not role_definition_id:
        print(f"Role definition '{role_name}' not found.")
        return False
    role_assignments = authorization_client.role_assignments.list_for_scope(scope)
    for role_assignment in role_assignments:
        if role_assignment.principal_id == spn_id and role_assignment.role_definition_id == role_definition_id:
            print(f"SPN {spn_id} already has the '{role_name}' role on the resource group '{resource_group_name}'.")
            return True
    role_assignment_id = str(uuid.uuid4())
    role_assignment_parameters = RoleAssignmentCreateParameters(
        role_definition_id=role_definition_id,
        principal_id=spn_id
    )
    authorization_client.role_assignments.create(scope, role_assignment_id, role_assignment_parameters)
    print(f"Assigned '{role_name}' role to SPN {spn_id} on resource group '{resource_group_name}'.")
    return True

# Function to assign roles to SPN
def assign_roles_to_spn(spn_id, subscription_id, target_resource_group, standard_resource_group):
    check_and_assign_role(spn_id, target_resource_group, subscription_id, "Contributor")
    check_and_assign_role(spn_id, standard_resource_group, subscription_id, "Reader")

# Main execution
if __name__ == "__main__":
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

    # Example for getting signed-in user object ID
    user_object_id = get_signed_in_user_object_id()
    print(f"The signed-in user's object ID is: {user_object_id}")

    # Example for getting resource group details
    resource_group_name = 'your_resource_group_name'
    get_resource_group_details(subscription_id, resource_group_name)

    # Example for validating resource group
    is_vpxrg = validate_resource_group(resource_group_name)
    print(f"Is the resource group VPXRG: {is_vpxrg}")

    # Example for checking role assignment
    principal_id = 'your_principal_id'
    role_definition_name = 'Contributor'
    has_role = check_role_assignment(resource_group_name, principal_id, role_definition_name)
    print(f"Role assignment check result: {has_role}")

    # Example for verifying user membership
    user_id = 'your_user_id'
    group_id = 'your_group_id'
    is_member = verify_user_membership(user_id, group_id)
    print(f"Membership verification result: {is_member}")

    # Example for checking SPN membership or ownership
    spn_id = 'your_spn_id'
    is_member, is_owner = check_spn_membership_or_ownership(spn_id, group_id)
    print(f"Membership check result: {is_member}")
    print(f"Ownership check result: {is_owner}")

    # Example for assigning roles to SPN
    target_resource_group = 'your_target_resource_group'
    standard_resource_group = 'your_standard_resource_group'
    assign_roles_to_spn(spn_id, subscription_id, target_resource_group, standard_resource_group)
