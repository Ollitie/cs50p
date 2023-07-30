# AZURE RESOURCE GROUP MANAGER

## Description:

This is a "final project" made to the [Harvard CS50's Introduction to programming with Python course](https://cs50.harvard.edu/python/2022/).

The **Azure Resource Group Manager** is a simple command-line program written in Python (with help of Azure SDK for Python) that allows users to manage Microsoft Azure resource groups within their Azure subscription. The program interacts with the Azure Resource Manager API to perform various operations, such as listing resource groups, creating new resource groups, managing resource groups' tags, listing resources within a group, and deleting resource groups.

The program uses for example logging to be able to review past actions and troubleshoot issues, different kinds of input validations e.g. on locations and names to ensure their validity in Azure, error handling to provide informative error messages to the user when needed, ability to cancel current operations and confirmations to prevent for example accidental deletions.

## Functions:

The program consists of a single Python script, and the following is a brief description of the main functions and their purpose:

1. **`main()`**: The main function that serves as the entry point of the program. It presents the user with a command-line interface to choose from various commands and continuously loops until the user decides to exit the program.

2. **`log_result()`**: A function used to log the result of program actions to a log file with a timestamp.

3. **`list_groups()`**: Lists all the resource groups in the Azure subscription. It retrieves the resource groups using the Azure Resource Management API and prints the results using the `tabulate` library for a nice output.

4. **`create_resource_group()`**: Allows the user to create a new resource group by providing the name and location. The function ensures that the entered location is valid by retrieving available Azure locations/regions in the subscription, and that the resource group name are in line with Azure naming rules. Used regex to validate names.

5. **`check_existence()`**: Allows the user to check if a resource group name already exists in the subscription. Used existing Azure SDK for Python methods to do the check.

6. **`manage_tags()`**: Enables the user to add or delete tags for a specific resource group. Tags are key-value pairs in Azure that can be used for organizing and categorizing resources. The function retrieves existing tags from Azure. Tag names and values are also validated with regex according to Azure rules.

## Video demo:
https://youtu.be/pTQsgUwJMAI

8. **`list_resources()`**: Lists and prints all the resources, e.g. virtual machines, within a specified resource group. If there are resources in a group, tabulate is used to do the printing.

9. **`delete()`**: Allows the user to delete a specified resource group and all its associated resources. The function confirms the deletion with the user before proceeding.

10. **`exit()`**: A function to exit the program.
