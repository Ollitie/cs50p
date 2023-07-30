from azure.identity import DefaultAzureCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import TagsPatchResource
import os
import sys
import re
from datetime import datetime
from tabulate import tabulate


# Set credentials using DefaultAzureCredential class and get subsciription id from environment variable
credentials = DefaultAzureCredential()
subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
# Initialize objects to interact with Azure Resource Manager
resource_client = ResourceManagementClient(credentials, subscription_id)
subscription_client = SubscriptionClient(credentials)


def main():
    # Commands available in the program main menu stored in a dict
    commands = {
        "list groups": list_groups,
        "check existence": check_existence,
        "create": create_resource_group,
        "manage tags": manage_tags,
        "list resources": list_resources,
        "delete": delete,
        "exit": exit,
        }

    print("\nWith this program you can manage Azure resource groups.")

    # Loop to prompt for a command. Get commands from a dictionary
    while True:
        try:
            available_commands(commands)
            command = input("Enter a command: ").strip().lower()
            if command in commands:
                result = commands[command]()
                log_result(result)
                print(result)
            else:
                print("> Unknown command. Try again.")
        # Offer ability to exit program with ctrl + d and ctrl + c
        except (EOFError, KeyboardInterrupt):
            sys.exit("\nExiting program...")


def available_commands(commands):
    # A function to print available commands
    print("\nAvailable commands: ", end="")
    for key in commands:
        print(key, end=" | ")
    print()


def log_result(result):
    # A Function that logs some of this programs actions to a logfile
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime('%Y-%m-%d %H.%M.%S')
    with open("log_file.log", "a") as log_file:
        log_file.write(f"{timestamp} - {result}\n")


def list_groups():
    # Function to retrieve resource group objects, add them to a list and and print using Tabulate
    group_list = resource_client.resource_groups.list()
    group_data = [[group.name, group.location, group.tags] for group in group_list]
    # Print the list using tabulate
    print(tabulate(group_data, headers=["Name", "Location", "Tags"], tablefmt="rounded_outline"))
    return f"> Printed resource groups in the subscription."


def validate_resource_group_name(name):
    # Function to validate resource group name input according to Azure rules
    if re.search(r"^(?!.*\.$)[A-Za-z0-9_()\-\.]{1,90}$", name):
        return True
    else:
        return False


def get_locations():
    # Function to return available location names in a subscription
    locations = subscription_client.subscriptions.list_locations(subscription_id)
    return [location.name for location in locations]


def print_locations():
    # Function to print available location names in a subscription
    available_locations = get_locations()
    for location in available_locations:
        print(location, end=", ")
    print("\n-------------")


def create_resource_group():
    # A function to create a new resource group. Checks available locations, existing names, rg name validity etc, and creates a new rg to Azure
    while True:
        available_locations = get_locations()
        location = input('Provide location for the resource group (to show a list of available locations, type "list"): ').strip().lower()
        if location == "list":
            print_locations()
        elif location not in available_locations:
            print("> Location you entered is not available. Available locations (regions) for the subscription:")
            print_locations()
        else:
            while True:
                print('Provide name for the group. Recommended name format is "rg-<app or service name>-<subscription purpose>-<###>"')
                resource_group_name = input("Enter name: ").strip()
                if not validate_resource_group_name(resource_group_name):
                    print("> Invalid resource group name. Resource group name can be between 1 and 90 characters long, contain alphanumerics, underscores, parentheses, hyphens, periods, and can't end with period.")
                elif resource_client.resource_groups.check_existence(resource_group_name):
                    print(f'> Resource group "{resource_group_name} already exists. Give another name.')
                else:
                    try:
                        resource_client.resource_groups.create_or_update(resource_group_name, {'location': location})
                        return f'> Resource group "{resource_group_name}" created succesfully'
                    except Exception as e:
                        return f"> An error occurred while creating the resource group: {e}"


def check_existence():
    # Check resource group name existence in the subscription
    while True:
        try:
            name_to_check = input("Which resource group name do you want to check? ").strip()
            if resource_client.resource_groups.check_existence(name_to_check):
                return f'> Check result: resource group name "{name_to_check}" is in use'
            else:
                return f'> Check result: resource group name "{name_to_check}" is not in use'
        except Exception as e:
            return f"> An error occurred while checking the existence: {e}"


def manage_tags():
    # Function to add or delete tags of a resource group.
    while True:
        print("Which resource group's tags do you want to manage? List resource groups with 'list' or cancel with 'cancel'.")
        resource_group_input = input("Enter resource group: ").strip()
        if resource_group_input == "list":
            list_groups()
            continue
        if resource_group_input == "cancel":
            return f'> Cancelled modifying tags'
        elif resource_client.resource_groups.check_existence(resource_group_input):
            while True:
                choice = input('Do you want to add or delete tags? ').strip().lower()
                if choice == "cancel":
                    return f'> Cancelled modifying tags'
                if choice == "add":
                    action = "Merge"
                elif choice == "delete":
                    action = "Delete"
                else:
                    print('> Invalid command. Enter "add" or "delete". You can also "cancel"')
                    continue
                # Retrieve existing tags
                existing_tags = get_tags(resource_group_input)
                edit_tags = {}
                while True:
                    # A loop to prompt for tag names and values, check input validity, and check if tags already exist. Add tag names and values into a dicionary
                    tag_name = input(f"Enter tag name: ").strip()
                    if tag_name == "taglist":
                        print(f'> Tags in resource group "{resource_group_input}": {existing_tags}')
                        continue
                    if tag_name == "cancel":
                        return f'> Cancelled modifying tags'
                    elif not validate_tag_name(tag_name):
                        print("> Invalid tag name. Tag names cannot contain <, >, %, &, \\, ?, / and should be at most 512 characters long.")
                        continue
                    elif choice == "add" and tag_name in existing_tags:
                        tag_value = input(f'Tag "{tag_name}" already exists with value "{existing_tags[tag_name]}". Update tag\'s value: ').strip()
                        if not validate_tag_value(tag_value):
                            print("> Invalid tag value. Tag names cannot contain <, >, %, &, \\, ?, / and should be at most 256 characters long.")
                            continue
                    elif choice == "add" and tag_name not in existing_tags:
                        tag_value = input(f"Enter tag value: ").strip()
                        if not validate_tag_value(tag_value):
                            print("> Invalid tag value. Tag names cannot contain <, >, %, &, \\, ?, / and should be at most 256 characters long.")
                            continue
                    elif choice == "delete" and tag_name not in existing_tags:
                        print(f'> Tag "{tag_name}" does not exist in resource group "{resource_group_input}". Provide existing tag name. To show existing tags, type "taglist"')
                        continue
                    elif choice == "delete" and tag_name in existing_tags:
                        tag_value = existing_tags[tag_name]
                    edit_tags[tag_name] = tag_value
                    another = input(f"Do you want to {choice} another tag? (y/n) ").strip().lower()
                    if another != "y":
                        break
                # Use Azure's classes and methods to add or delete tags in resource group
                tag_patch_resource = TagsPatchResource(
                operation=action,
                properties={'tags': edit_tags}
                )
                resource_group = resource_client.resource_groups.get(resource_group_input)
                try:
                    resource_client.tags.begin_update_at_scope(resource_group.id, tag_patch_resource)
                    return f'{choice.title()}d tags {tag_patch_resource.properties.tags} in resource group "{resource_group_input}"'
                except Exception as e:
                    return f"> An error occurred while trying to manage tags: {e}"
        else:
            print(f'> Could not find resource group "{resource_group_input}"')


def validate_tag_name(tag_name):
    # A function to validate tag names with regex
    if re.search(r"[^<>%&\\?\/]{1,512}$", tag_name):
        return True
    else:
        return False



def validate_tag_value(tag_value):
    # A function to validate tag values with regex
    if re.search(r"[^<>%&\\?\/]{1,256}$", tag_value):
        return True
    else:
        return False


def get_tags(resource_group_name):
    # Function to retrieve existing tags of a resource group
    resource_group = resource_client.resource_groups.get(resource_group_name)
    resource_group_tags = resource_client.tags.get_at_scope(resource_group.id)
    if resource_group_tags and resource_group_tags.properties and resource_group_tags.properties.tags:
        return resource_group_tags.properties.tags
    else:
        return {}


def list_resources():
    # Function to list and print resources in a resource group
    print("Here you can view a list of resources inside a resource group.")
    while True:
        # Retrieve the list of resources in a given resource group
        resource_group = input('Enter resource group name, "list" or "cancel": ').strip()
        if resource_group.lower() == "list":
            list_groups()
        elif resource_group.lower() == "cancel":
            return f'> Cancelled listing resources'
        # Check resource groups existence
        elif resource_client.resource_groups.check_existence(resource_group):
            try:
                # Retrieve resources of a group and add them into a list. The expand argument includes additional properties in the output.
                resource_list = resource_client.resources.list_by_resource_group(resource_group, expand = "createdTime,changedTime")
                list_data = [[resource.name, resource.type, resource.created_time, resource.changed_time] for resource in resource_list]
            except Exception as e:
                return f"> An error occurred while listing resources: {e}"
            else:
                # Print the list using tabulate if there are resources in the list_data
                if list_data:
                    print(tabulate(list_data, headers=["Name", "Type", "Created time", "Changed time"], tablefmt="rounded_outline"))
                    return f'> Printed resources in "{resource_group}"'
                else:
                    return f'> Found no resources in resource group "{resource_group}"'
        else:
            print(f'> Could not find resource group "{resource_group}". Enter an existing resource group name.')


def delete():
    # Function to delete a resource group
    while True:
        print("Which group do you want to delete? List resource groups with 'list' or go back with 'cancel': ")
        group_to_delete = input(f"Enter name: ").strip()
        if group_to_delete.lower() == "cancel":
            return("> Cancelled deleting resource group.")
        elif group_to_delete.lower() == "list":
            list_groups()
        # Check resource groups existence
        elif resource_client.resource_groups.check_existence(group_to_delete):
            # Confirm the deletion, as deletion cannot be undone
            confirm = input(f'Are you sure you want to delete resource group "{group_to_delete}" and all of its resources? Deleting cannot be undone (y/n): ').strip()
            if confirm.lower() == "y":
                try:
                    # Use Azure's begin_delete method to delete the group
                    print(f'> Proceeding to delete resource group "{group_to_delete}". This may take a while...')
                    resource_client.resource_groups.begin_delete(group_to_delete).result()
                    return f'> Deleted resource group "{group_to_delete}" succesfully.'
                except Exception as e:
                    return f"> An error occurred while deleting the resource group: {e}"
            else:
                return f'> Cancelling... Did not delete the resource group {group_to_delete}.'
        else:
            print(f'> Could not find resource group "{group_to_delete}". Please enter a existing group name. ')


def exit():
    # Function to exit the program
    sys.exit("> See you again!")


if __name__ == "__main__":
    main()