import os
import random
from locust import HttpUser, task, between
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree

class NextcloudUser(HttpUser):
    auth = None
    user_name = None
    wait_time = between(2, 5)

    def on_start(self):
        user_idx = random.randrange(0, 30)
        self.user_name = f'user{user_idx}'
        self.auth = HTTPBasicAuth(self.user_name, 'ziyang1234!')

        # Generate files
        self.file_1gb = "./data/file_1gb"
        with open(self.file_1gb, "wb") as file:
            file.write(os.urandom(1024 * 1024 * 1024))  # 1GB

        self.file_1mb = "./test_data/file_1mb"
        if not os.path.exists(self.file_1mb):
            with open(self.file_1mb, "wb") as file:
                file.write(os.urandom(1024 * 1024))  # 1MB

        self.file_1kb = "./test_data/file_1kb"
        if not os.path.exists(self.file_1kb):
            with open(self.file_1kb, "wb") as file:
                file.write(os.urandom(1024))  # 1KB
    
    @task(5)
    def propfind(self):
        response = self.client.request("PROPFIND", f"/remote.php/dav/files/{self.user_name}/", auth=self.auth)
        print(f"PROPFIND status: {response.status_code}, content: {response.headers}")

    @task(5)
    def read_file(self):
        response = self.client.get(f"/remote.php/dav/files/{self.user_name}/Readme.md", auth=self.auth)
        response = print(f"GET status: {response.status_code}, content: {response.headers}")
    
    @task(5)
    def upload_file_1mb(self):
        remote_path = f"/remote.php/dav/files/{self.user_name}/1mb_file_{random.randrange(0, 10)}"
        with open(self.file_1mb, "rb") as file:
            response = self.client.put(remote_path, data=file, auth=self.auth)
        print(f"PUT 1MB status: {response.status_code}, content: {response.headers}")

    @task(10)
    def upload_file_1kb(self):
        remote_path = f"/remote.php/dav/files/{self.user_name}/1kb_file_{random.randrange(0, 10)}"
        with open(self.file_1kb, "rb") as file:
            response = self.client.put(remote_path, data=file, auth=self.auth)
        print(f"PUT 1KB status: {response.status_code}, content: {response.headers}")

    @task(1)
    def upload_file_1gb(self):
        remote_path = f"/remote.php/dav/files/{self.user_name}/1gb_file_{random.randrange(0, 10)}"
        with open(self.file_1gb, "rb") as file:
            response = self.client.put(remote_path, data=file, auth=self.auth)
        print(f"PUT 1GB status: {response.status_code}, content: {response.content}")
    
    
    @task(1)
    def delete_files(self):
        # Send a PROPFIND request to get a list of all files
        response = self.client.request("PROPFIND", f"/remote.php/dav/files/{self.user_name}/", auth=self.auth)
        if response.status_code == 207:
            # Parse the XML response
            tree = ElementTree.fromstring(response.content)

            # The XML namespace for DAV elements
            ns = {"d": "DAV:"}

            # Iterate over all "href" elements in the response
            for href in tree.findall(".//d:href", ns):
                # Get the file name from the href
                file_name = href.text.rsplit("/", 1)[-1]

                # If the file name starts with "1", delete it
                if file_name.startswith("1"):
                    response = self.client.delete(href.text, auth=self.auth)
                    print(f"DELETE {file_name} status: {response.status_code}, content: {response.headers}")
        
