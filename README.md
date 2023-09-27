**Azure-Peer**

This Python script creates inbound rules in network security groups (NSGs) and firewall rules in PostgreSQL servers. It also creates virtual network peerings between two virtual networks.

**Features:**

* Creates inbound rules in NSGs to allow traffic from specific IP addresses or ranges.
* Creates firewall rules in PostgreSQL servers to allow traffic from specific IP addresses or ranges.
* Creates virtual network peerings between two virtual networks to allow traffic to flow between them.

**Contributing guidelines:**

The code can be much more efficient. It was written quickly to solve a specific problem in which time was more important than efficiency.

If you would like to contribute to this project, please fork this repository and create a pull request. Please make sure to add tests for any changes that you make.


------------

Example Usage:

WELCOME TO THE AZURE PEERING TOOL FOR EU CUSTOMERS
THIS SCRIPT VERSION SHOULD BE USED ONLY FOR EU CUSTOMERS, PLEASE DOUBLE CHECK CUSTOMER'S REGION!

Enter customer's subscription full name (case sensitive): <subscription_name>

Loading, please wait...

RDP inbound rules created in the NSG <nsg_name>
Firewall rule created in <server_name>
Peering on the customer created successfully.
Peering on ManagementEU Vnet created successfully.

REMEMBER TO CHECK MESSAGES FOR ERRORS!!!

Press any key to close and enjoy your day :)

------------------

Code Analysis:
Inputs
subscription_name: The full name of the customer's subscription.

Flow
Get the subscription ID using the get_subscription_id function.
Get the resource group name using the get_resource_group_name function.
Create a NetworkManagementClient and a ResourceManagementClient using the obtained subscription ID.
Iterate over each resource group and get a list of NSGs.
Create SSH inbound rule in NSGs with names ending in "platform-nsg" using the create_ssh_rule function.
Create RDP inbound rules in NSGs with names ending in "developer-nsg" using the create_rdp_rules function.
Get a list of PostgreSQL servers in the resource group.
Create a firewall rule on each PostgreSQL server using the begin_create_or_update method of PostgreSQLManagementClient.
Get the ID of the customer's virtual network using the get_vnet_id function.
Check if the peering between the customer's virtual network and the "ManagementEU-Vnet" already exists.
If the peering does not exist, create it using the begin_create_or_update method of NetworkManagementClient.
Sign out of the current subscription and sign in to the "ManagementEU" subscription.
Create a peering from the "ManagementEU-Vnet" to the customer's virtual network using the begin_create_or_update method of NetworkManagementClient.
Outputs
Messages indicating the creation of SSH inbound rules, RDP inbound rules, firewall rules, and virtual network peerings.


