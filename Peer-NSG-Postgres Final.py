from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.rdbms.postgresql import PostgreSQLManagementClient


def get_subscription_id(subscription_name):
    subscription_client = SubscriptionClient(
        credential=DefaultAzureCredential()
    )
    
    subscriptions = subscription_client.subscriptions.list()
    for subscription in subscriptions:
        if subscription.display_name == subscription_name:
            return subscription.subscription_id
    return None

def get_resource_group_name(subscription_id, vnet_name):
    resource_client = ResourceManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=subscription_id
    )
    
    resource_groups = resource_client.resource_groups.list()
    for group in resource_groups:
        resources = resource_client.resources.list_by_resource_group(group.name)
        for resource in resources:
            if resource.type == "Microsoft.Network/virtualNetworks" and resource.name == vnet_name:
                return group.name
    return None

def get_vnet_id(client, resource_group_name, vnet_name):
    try:
        vnet = client.virtual_networks.get(
            resource_group_name=resource_group_name,
            virtual_network_name=vnet_name
        )
        return vnet.id
    except:
        return None

def peering_exists(client, resource_group_name, vnet_name, peering_name):
    try:
        client.virtual_network_peerings.get(
            resource_group_name=resource_group_name,
            virtual_network_name=vnet_name,
            virtual_network_peering_name=peering_name
        )
        return True
    except:
        return False

def create_ssh_rule(network_client, nsg):
    try:
        rule = {
            "protocol": "Tcp",
            "source_port_range": "*",
            "destination_port_range": "22",
            "source_address_prefix": "xxx",
            "destination_address_prefix": "*",
            "access": "Allow",
            "priority": 1999,
            "direction": "Inbound",
            "name": "JSEU-SSH"
        }
        
        result = network_client.security_rules.begin_create_or_update(
            resource_group_name=nsg.id.split('/')[4],
            network_security_group_name=nsg.name,
            security_rule_name="JSEU-SSH",
            security_rule_parameters=rule
        ).result()
        
        print(f"SSH inbound rule created in the NSG {nsg.name}")
        return result
    except Exception as e:
        print(f"Error creating SSH rule in NSG {nsg.name}: {str(e)}")
        return None

def create_rdp_rules(network_client, nsg):
    try:
        rdp_rule_1 = {
            "protocol": "Tcp",
            "source_port_range": "*",
            "destination_port_range": "3389",
            "source_address_prefix": "xx",
            "destination_address_prefix": "*",
            "access": "Allow",
            "priority": 1999,
            "direction": "Inbound",
            "name": "JSEU-RDP"
        }
        
        rdp_rule_2 = {
            "protocol": "Tcp",
            "source_port_range": "*",
            "destination_port_range": "3389",
            "source_address_prefix": "xx",
            "destination_address_prefix": "*",
            "access": "Allow",
            "priority": 1998,
            "direction": "Inbound",
            "name": "GatewaysEU-RDP"
        }
        
        result1 = network_client.security_rules.begin_create_or_update(
            resource_group_name=nsg.id.split('/')[4],
            network_security_group_name=nsg.name,
            security_rule_name="JSEU-RDP",
            security_rule_parameters=rdp_rule_1
        ).result()
        
        result2 = network_client.security_rules.begin_create_or_update(
            resource_group_name=nsg.id.split('/')[4],
            network_security_group_name=nsg.name,
            security_rule_name="GatewaysEU-RDP",
            security_rule_parameters=rdp_rule_2
        ).result()
    
        print(f"RDP inbound rules created in the NSG {nsg.name}")
        return result1, result2
    except Exception as e:
        print(f"Error creating RDP rules in NSG {nsg.name}: {str(e)}")
        return None, None

def main():
    try:
        print("WELCOME TO THE AZURE PEERING TOOL FOR EU CUSTOMERS")
        print("THIS SCRIPT VERSION SHOULD BE USED ONLY FOR EU CUSTOMERS, PLEASE DOUBLE CHECK CUSTOMER'S REGION!")
        print ()
        subscription_name = input("Enter customer's subscription full name (case sensitive): ")
        print ()
        print ("Loading, please wait...")
        print ()

        vnet_name = "xxx-VNet"
        peering_name = "xxx-VNet_to_ManagementEU"
        
        subscription_id = get_subscription_id(subscription_name)
        
        if subscription_id:
            resource_group_name = get_resource_group_name(subscription_id, vnet_name)
            
            if resource_group_name:
                network_client = NetworkManagementClient(
                    credential=DefaultAzureCredential(),
                    subscription_id=subscription_id,
                )

                resource_client = ResourceManagementClient(
                credential=DefaultAzureCredential(),
                subscription_id=subscription_id
                )
                postgres_client = PostgreSQLManagementClient(
                credential=DefaultAzureCredential(),
                subscription_id=subscription_id
                )
                
                #Inbound rules creation:

                # Get a list of all resource groups in the subscription
                resource_groups = resource_client.resource_groups.list()

                # Iterate over each resource group
                for resource_group in resource_groups:
                    nsgs = list(network_client.network_security_groups.list(resource_group.name))

                    # Create inbound rules on each NSG found
                    for nsg in nsgs:
                        if nsg.name.lower().endswith("platform-nsg"):
                            # Create the SSH inbound rule in each "platform-nsg"
                            create_ssh_rule(network_client, nsg)
        
                        if nsg.name.lower().endswith("developer-nsg"):
                            # Create the RDP inbound rules in each "developer-nsg"
                            create_rdp_rules(network_client, nsg)

                # PostgreSQL servers set firewall rule.

                    # Get a list of all PostgreSQL servers in the resource group
                    postgres_servers = list(postgres_client.servers.list_by_resource_group(resource_group.name))

                    # Create firewall rule on each PostgreSQL server found
                    for server in postgres_servers:
                        try:
                            posgresql_reponse = postgres_client.firewall_rules.begin_create_or_update(
                                resource_group.name,
                                server.name,
                                firewall_rule_name="azure_js_ue",
                                # Use JS publc IP
                                parameters={"properties": {"endIpAddress": "xxx", "startIpAddress": "xxx"}},
                            ).result()
                            
                            # Print the message indicating the firewall rule creation
                            print(f"Firewall rule created in {server.name}")
                        except Exception as e:
                            print(f"An error occurred while creating firewall rule in {server.name}: {str(e)}")
                    
                    customer_Vnet_ID = get_vnet_id(network_client, resource_group_name, vnet_name)

                # Peerings creation:

                if customer_Vnet_ID:
                    if peering_exists(network_client, resource_group_name, vnet_name, peering_name):
                        print("Peering 'xxx-VNet_to_ManagementEU' ALREADY EXISTED.")
                    else: 
                        response = network_client.virtual_network_peerings.begin_create_or_update(
                            resource_group_name=resource_group_name,
                            virtual_network_name=vnet_name,
                            virtual_network_peering_name="xxx-VNet_to_ManagementEU",
                            virtual_network_peering_parameters={
                                "properties": {
                                    "allowForwardedTraffic": True,
                                    "allowGatewayTransit": False,
                                    "allowVirtualNetworkAccess": True,
                                    "remoteVirtualNetwork": {
                                        "id": "/subscriptions/9ad893cf-6xxxxxd92f48f8e18/resourceGroups/xxx/providers/Microsoft.Network/virtualNetworks/xxx-Vnet"
                                    },
                                    "useRemoteGateways": False,
                                }
                            },
                        ).result()
                        if response.provisioning_state == "Succeeded":
                            print("Peering on the customer created successfully.")
                        else:
                            print("Peering on the customer OPERATION FAILED.")                    

                        # Sign out on first subscription
                        del network_client

                        # Open a new session in subscription "xxx - Management"
                        subscription_id_management = "9ad893cxxxf8e18"
                        client_management = NetworkManagementClient(
                            credential=DefaultAzureCredential(),
                            subscription_id=subscription_id_management,
                        )

                        # Get the first 4 characters of the subscription name
                        shortened_subscription_name = subscription_name[:4]

                        response2 = client_management.virtual_network_peerings.begin_create_or_update(
                            resource_group_name="ManagementEU",
                            virtual_network_name="ManagementEU-Vnet",
                            virtual_network_peering_name=f"ManagementEU-Vnet_to_xxx-VNet-{shortened_subscription_name}",
                            virtual_network_peering_parameters={
                                "properties": {
                                    "allowForwardedTraffic": True,
                                    "allowGatewayTransit": False,
                                    "allowVirtualNetworkAccess": True,
                                    "remoteVirtualNetwork": {
                                        "id": customer_Vnet_ID
                                    },
                                    "useRemoteGateways": False,
                                }
                            },
                        ).result()

                        if response2.provisioning_state == "Succeeded":
                            print("Peering on ManagementEU Vnet created successfully.")
                        else:
                            print("Peering on ManagementEU Vnet FAILED.")
                else:
                    print(f"VNet '{vnet_name}' NOT FOUND in '{subscription_name}'.")
            else:
                print(f"VNet '{vnet_name}' NOT FOUND in '{subscription_name}'.")
        else:
            print(f"Subscription '{subscription_name}' NOT FOUND.")
    except Exception as e:
        print(f"SOMETHING FAILED:")
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    main()
    print ()
    print ("REMEMBER TO CHECK MESSAGES FOR ERRORS!!!")
    print ()
    input("Press any key to close and enjoy your day :)")