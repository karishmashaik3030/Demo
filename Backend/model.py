class Demo():
  def fetch_code_from_repo():
    return "fetching code"
import os
from azure.identity import ClientSecretCredential
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.resource import SubscriptionClient
import os
from kubernetes import client, config
from azure.identity import ClientSecretCredential
from azure.mgmt.containerservice import ContainerServiceClient
from kubernetes.client.rest import ApiException
from dotenv import load_dotenv
import os
from azure.identity import ClientSecretCredential
from azure.mgmt.containerservice import ContainerServiceClient
from kubernetes import client, config
import yaml
from datetime import datetime, timezone

load_dotenv()

class KubernetesModel:
    def __init__(self):
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.subscription_id = os.getenv("SUBSCRIPTION_ID")

        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise EnvironmentError("Azure credentials not set in environment variables.")

        self.credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        # Use the credentials to create a ContainerServiceClient to interact with AKS
        self.container_client = ContainerServiceClient(self.credential, subscription_id=self.subscription_id)
    
    

    def list_aks_clusters(self):
        sub_client = SubscriptionClient(self.credential)
        aks_clusters = []

        for sub in sub_client.subscriptions.list():
            subscription_id = sub.subscription_id
            client = ContainerServiceClient(self.credential, subscription_id)

            for cluster in client.managed_clusters.list():
                print(cluster)
                aks_clusters.append({
                "name": cluster.name,
                "resourceGroup": cluster.id.split("/")[4],
                "location": cluster.location,
                "kubernetesVersion": cluster.kubernetes_version,
                "dnsPrefix": cluster.dns_prefix,
                "nodeResourceGroup": cluster.node_resource_group,
                "provisioningState": cluster.provisioning_state,
                "tags": cluster.tags or {},
                "fqdn": cluster.fqdn,
                "privateCluster": cluster.api_server_access_profile.enable_private_cluster if cluster.api_server_access_profile else None,
                "identityType": cluster.identity.type if cluster.identity else None,
                "aadEnabled": cluster.aad_profile.managed if cluster.aad_profile else None,
                "networkPlugin": cluster.network_profile.network_plugin if cluster.network_profile else None
            })
            response = {
                "datamap": {
                    "table": aks_clusters,
                    "table_keys": ["name","resourceGroup","location","kubernetesVersion","dnsPrefix","nodeResourceGroup","provisioningState",
                    "tags","fqdn","privateCluster","identityType","aadEnabled","networkPlugin"]
                }
            }


        return response
    
    def convert_cpu_to_cores(self,cpu_usage):
        # Convert CPU usage from nanocores (n) to cores
        return float(cpu_usage.replace("n", "")) / 1_000_000_000

    def convert_memory_to_mb(self,memory_usage):
        # Convert Memory usage from KiB to MB
        return float(memory_usage.replace("Ki", "")) / 1024

    def calculate_percentage(self,usage, total):
        # Calculate percentage usage
        return (usage / total) * 100 if total > 0 else 0
    
    def _parse_kubeconfig(self, kubeconfig_str):
        """Helper function to parse the kubeconfig YAML string into a dictionary."""
        return yaml.safe_load(kubeconfig_str) 

    def get_aks_cluster_credentials(self, cluster_name):
        try:
            # Replace any unwanted characters from the cluster name if needed
            cluster_name = cluster_name

            # Define the resource group name (replace with your actual resource group name)
            resource_group_name = "KUBERNETESTEST"  # Update with your actual resource group name


            # Fetch the cluster user credentials
            credentials = self.container_client.managed_clusters.list_cluster_admin_credentials(
                resource_group_name=resource_group_name,resource_name=cluster_name
            )

            # Get the kubeconfig and decode it
            kubeconfig = credentials.kubeconfigs[0].value.decode('utf-8')

            # Load Kubernetes configuration directly from the kubeconfig string
            config.load_kube_config_from_dict(self._parse_kubeconfig(kubeconfig))


            # Return the Kubernetes CoreV1Api client
            return client.CoreV1Api()

        except Exception as e:
            raise Exception(f"Error fetching credentials for AKS cluster {cluster_name}: {str(e)}")


    def get_node_usage(self, cluster_name):
        print(cluster_name)
        # cluster_name = cluster_name.replace('<', '').replace('>', '')
        print(cluster_name)
        try:
            # Get specific cluster's API context
            core_api = self.get_aks_cluster_credentials(cluster_name)
            metrics_api = client.CustomObjectsApi()
            print(core_api)
            nodes = core_api.list_node()
            usage_data = []
            
            for node in nodes.items:
                node_name = node.metadata.name
                node_labels = node.metadata.labels
                
                # Check if the node is a master node or worker node based on the label
                node_role = "worker"  # Default assumption
                if "kubernetes.io/role" in node_labels and node_labels["kubernetes.io/role"] == "master":
                    node_role = "master"

                # Fetch metrics for the node
                metrics = metrics_api.get_cluster_custom_object(
                    group="metrics.k8s.io",
                    version="v1beta1",
                    plural="nodes",
                    name=node_name
                )

                # Fetch the total capacity for CPU and memory from the node's status
                total_cpu_capacity = float(node.status.capacity['cpu'])  # Total CPU in cores
                total_memory_capacity = float(node.status.capacity['memory'].replace("Ki", "")) / 1024  # Total memory in MB

                # Convert and calculate usage for CPU and memory
                cpu_usage = self.convert_cpu_to_cores(metrics['usage']['cpu'])
                memory_usage = self.convert_memory_to_mb(metrics['usage']['memory'])

                # Calculate the percentage usage for CPU and memory
                cpu_percentage = self.calculate_percentage(cpu_usage, total_cpu_capacity)
                memory_percentage = self.calculate_percentage(memory_usage, total_memory_capacity)

                # Append the result to the usage data list
                usage_data.append({
                    "node": node_name,
                    "nodeRole": node_role,  # Include the role (master/worker)
                    "cpuUsageInCores": cpu_usage,
                    "cpuUsagePercentage": cpu_percentage,
                    "memoryUsageInMB": memory_usage,
                    "memoryUsagePercentage": memory_percentage
                })
                response = {
                "datamap": {
                    "table": usage_data,
                    "table_keys": ["node","nodeRole","cpuUsageInCores","cpuUsagePercentage","memoryUsageInMB","memoryUsagePercentage"]
                }
            }

            return response
        except ApiException as e:
            raise Exception(f"Error fetching node usage for cluster {cluster_name}: {e}")
        

    def parse_cpu(self, cpu_str):
        """
        Parse CPU values into cores, handles millicores (m), nanocores (n), and cores (without m).
        Converts nanocores and millicores to cores (float).
        """
        try:
            if cpu_str.endswith('m'):  # For millicores (e.g., 500m)
                return float(cpu_str[:-1]) / 1000.0  # Convert millicores to cores
            elif cpu_str.endswith('n'):  # For nanocores (e.g., 148771043n)
                return float(cpu_str[:-1]) / 1000000000.0  # Convert nanocores to cores
            else:
                return float(cpu_str)  # Return cores as float (e.g., "1" for 1 core)
        except ValueError:
            raise ValueError(f"Invalid CPU value: {cpu_str}")

    def parse_memory(self, mem_str):
        """
        Parse memory values into KiB (Kibibytes).
        Converts memory to KiB based on the unit suffix (Ki, Mi, Gi, Ti, M).
        """
        units = {"Ki": 1, "Mi": 1024, "Gi": 1024 * 1024, "Ti": 1024 * 1024 * 1024, "M": 1024}  # Add 'M' for MiB
        try:
            for unit in units:
                if mem_str.endswith(unit):
                    value = float(mem_str[:-len(unit)])  # Remove the unit suffix and convert to float
                    return int(value * units[unit])  # Return value in KiB
            return int(mem_str)  # If no unit suffix, return the value as is (assumed to be in KiB)
        except ValueError:
            raise ValueError(f"Invalid memory value: {mem_str}")

    def get_cpu_summary(self, cluster_name):
        """
        Get the CPU usage, requests, limits, allocated capacity, and total capacity for each node in the AKS cluster.
        """
        try:
            core_api = self.get_aks_cluster_credentials(cluster_name)
            metrics_api = client.CustomObjectsApi()
            nodes = core_api.list_node()
            usage_data = []

            for node in nodes.items:
                node_name = node.metadata.name
                metrics = metrics_api.get_cluster_custom_object(
                    group="metrics.k8s.io",
                    version="v1beta1",
                    plural="nodes",
                    name=node_name
                )

                # Fetch the total capacity for CPU from node's status
                total_cpu_capacity = self.parse_cpu(node.status.capacity['cpu'])  # Total CPU in cores

                # Calculate CPU usage from metrics (current usage)
                cpu_usage = self.parse_cpu(metrics['usage']['cpu'])

                # Fetch pod information for requests and limits
                total_requests = 0
                total_limits = 0
                total_allocated_capacity = 0

                # Get CPU requests, limits, and allocated capacity based on pod containers
                pods = core_api.list_pod_for_all_namespaces()
                for pod in pods.items:
                    for container in pod.spec.containers:
                        resources = container.resources
                        if resources.requests and 'cpu' in resources.requests:
                            total_requests += self.parse_cpu(resources.requests['cpu'])
                        if resources.limits and 'cpu' in resources.limits:
                            total_limits += self.parse_cpu(resources.limits['cpu'])
                
                # Allocated CPU is the sum of all requests
                total_allocated_capacity += total_requests
                

                # Calculate percentage usage
                cpu_usage_percentage = self.calculate_percentage(cpu_usage, total_cpu_capacity)
                allocated_percentage = self.calculate_percentage(total_allocated_capacity, total_cpu_capacity)
                

                cpu_usage_percentage = self.calculate_percentage(cpu_usage, total_cpu_capacity)
                allocated_percentage = self.calculate_percentage(total_allocated_capacity, total_cpu_capacity)
                available_cpu = total_cpu_capacity - total_allocated_capacity
                overcommit_ratio = round(total_requests / total_cpu_capacity, 2) if total_cpu_capacity else 0.0

                # Node status and pressure
                node_ready_status = "Unknown"
                cpu_pressure_status = "None"
                for condition in node.status.conditions:
                    if condition.type == "Ready":
                        node_ready_status = condition.status
                    if condition.type in ["MemoryPressure", "PIDPressure", "DiskPressure"]:
                        if condition.status == "True":
                            cpu_pressure_status = condition.type
                
                # Append the result to the usage data list
                usage_data.append({
                "node": node_name,
                "cpuUsageInCores": round(cpu_usage, 2),
                "cpuUsagePercentage (%)": round(cpu_usage_percentage, 2),  # Add percentage symbol
                "cpuRequestsInCores": round(total_requests, 2),
                "cpuLimitsInCores": round(total_limits, 2),
                "allocatedCPUInCores": round(total_allocated_capacity, 2),
                "cpuTotalCapacityInCores": round(total_cpu_capacity, 2),
                "allocatedCPUPercentage (%)": round(allocated_percentage, 2),  # Add percentage symbol
                "availableCPUInCores": round(available_cpu, 2),
                "cpuOvercommitRatio": overcommit_ratio,
                "nodeStatus": node_ready_status,
                "cpuPressure": cpu_pressure_status,
                })
                response = {
                "datamap": {
                    "table": usage_data,
                    "table_keys": ["node","cpuUsageInCores","cpuUsagePercentage%","cpuRequestsInCores",
                    "cpuLimitsInCores","allocatedCPUInCores","cpuTotalCapacityInCores","allocatedCPUPercentage%",
                    "cpuOvercommitRatio","nodeStatus","cpuPressure"]
                }
            }

            return response
        except ApiException as e:
            raise Exception(f"Error fetching CPU usage for cluster {cluster_name}: {e}")
        



    def get_memory_summary(self, cluster_name):
        """
        Get the memory usage, requests, limits, allocated capacity, and total capacity for each node in the AKS cluster.
        """
        try:
            core_api = self.get_aks_cluster_credentials(cluster_name)
            metrics_api = client.CustomObjectsApi()
            nodes = core_api.list_node()
            usage_data = []

            for node in nodes.items:
                node_name = node.metadata.name
                metrics = metrics_api.get_cluster_custom_object(
                    group="metrics.k8s.io",
                    version="v1beta1",
                    plural="nodes",
                    name=node_name
                )

                # Fetch the total capacity for memory from node's status
                total_memory_capacity = self.parse_memory(node.status.capacity['memory'])  # Total Memory in KiB
                print(node.status.capacity['memory'])
                print(metrics['usage']['memory'])

                # Calculate memory usage from metrics (current usage)
                memory_usage = self.parse_memory(metrics['usage']['memory'])  # Memory in KiB

                # Fetch pod information for requests and limits
                total_requests = 0
                total_limits = 0
                total_allocated_capacity = 0

                # Get memory requests, limits, and allocated capacity based on pod containers
                pods = core_api.list_pod_for_all_namespaces()
                for pod in pods.items:
                    for container in pod.spec.containers:
                        resources = container.resources
                        if resources.requests and 'memory' in resources.requests:
                            total_requests += self.parse_memory(resources.requests['memory'])
                        if resources.limits and 'memory' in resources.limits:
                            total_limits += self.parse_memory(resources.limits['memory'])
                    # Allocated memory is the sum of all requests
                    total_allocated_capacity += total_requests

                # Convert values to MiB for the response
                memory_usage_in_mi = round(memory_usage / 1024, 2)  # Convert KiB to MiB
                total_memory_capacity_in_mi = round(total_memory_capacity / 1024, 2)
                total_requests_in_mi = round(total_requests / 1024, 2)
                total_limits_in_mi = round(total_limits / 1024, 2)
                total_allocated_capacity_in_mi = round(total_allocated_capacity / 1024, 2)

                # Calculate percentage usage for memory
                memory_usage_percentage = self.calculate_percentage(memory_usage_in_mi, total_memory_capacity_in_mi)
                allocated_percentage = self.calculate_percentage(total_allocated_capacity_in_mi, total_memory_capacity_in_mi)

                # Append the result to the usage data list
                usage_data.append({
                    "node": node_name,
                    "memoryUsageInMi": memory_usage_in_mi,
                    "memoryUsagePercentage%": round(memory_usage_percentage, 2),
                    "memoryRequestsInMi": total_requests_in_mi,
                    "memoryLimitsInMi": total_limits_in_mi,
                    "allocatedMemoryInMi": total_allocated_capacity_in_mi,
                    "memoryTotalCapacityInMi": total_memory_capacity_in_mi,
                    "allocatedMemoryPercentage%": round(allocated_percentage, 2),
                })

            return {
                "datamap": {
                    "table": usage_data,
                    "table_keys": ["node","memoryUsageInMi","memoryUsagePercentage%","memoryRequestsInMi","memoryLimitsInMi",
                        "allocatedMemoryInMi","memoryTotalCapacityInMi","allocatedMemoryPercentage%",
                    ]
                }
            }
        
        except ApiException as e:
            raise Exception(f"Error fetching memory summary for cluster {cluster_name}: {e}")
