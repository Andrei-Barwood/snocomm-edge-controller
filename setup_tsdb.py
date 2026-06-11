import sys
import yaml
from influxdb_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError

def main():
    with open('config_industrial.yaml', 'r') as f:
        config = yaml.safe_load(f)
        
    url = config['influxdb']['url']
    token = config['influxdb']['token']
    org = config['influxdb']['org']
    bucket_name = config['influxdb']['bucket']
    
    print(f"Configuring InfluxDB at {url}")
    print(f"Org: {org}, Bucket: {bucket_name}")
    print("Ensure InfluxDB 2.x is running and the token is valid.")
    
    client = InfluxDBClient(url=url, token=token, org=org)
    
    try:
        buckets_api = client.buckets_api()
        buckets = buckets_api.find_buckets().buckets
        bucket_exists = any(b.name == bucket_name for b in buckets)
        
        if not bucket_exists:
            print(f"Creating bucket '{bucket_name}'...")
            # We need org id
            orgs_api = client.organizations_api()
            orgs = orgs_api.find_organizations(org=org)
            if not orgs:
                print(f"Organization '{org}' not found! Please create it via InfluxDB UI.")
                return
            org_id = orgs[0].id
            buckets_api.create_bucket(bucket_name=bucket_name, org_id=org_id)
            print("Bucket created successfully.")
        else:
            print(f"Bucket '{bucket_name}' already exists. Setup complete.")
    except InfluxDBError as e:
        print(f"Error connecting to InfluxDB: {e}")
        print("Tip: Start InfluxDB using 'docker run -p 8086:8086 influxdb:2.7.1' or similar.")
    finally:
        client.close()

if __name__ == "__main__":
    main()
