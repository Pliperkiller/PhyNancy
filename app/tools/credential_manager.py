import os
import json
from abc import ABC, abstractmethod

### Credential reader

# Credential reader abstraction
class CredentialReader(ABC):
    @abstractmethod
    def read_credentials(self):
        pass

# Credential reader implementation for Json files
class JsonCredentialReader(CredentialReader):
    def __init__(self, folder_name='keys', file_name='keys.json'):
        self.folder_name = folder_name
        self.file_name = file_name

    def read_credentials(self):
        dir_path = os.path.dirname(os.getcwd())
        folder_path = os.path.join(dir_path, self.folder_name)
        file_path = os.path.join(folder_path, self.file_name)

        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        else:
            raise FileNotFoundError(f"No credentials found at {file_path}")

### Credential Manager

# Credential Manager
class CredentialsManager:
    def __init__(self, reader: CredentialReader):
        self.credentials:json = reader.read_credentials()

    def get_service_credentials(self, service_name, group="passwords"):
        services = self.credentials.get(group, [])
        for entry in services:
            if entry["service"] == service_name:
                return entry
        return None


### Service Credentials

# Service credentials for specific implementations
class ServiceCredentials:
    def __init__(self, credentials_manager: CredentialsManager, service_name: str, required_keys: list):
        self.credentials = credentials_manager.get_service_credentials(service_name)

        if not self.credentials:
            raise ValueError(f"No credentials found for service: {service_name}")

        missing_keys = [key for key in required_keys if key not in self.credentials]
        if missing_keys:
            raise KeyError(f"Missing keys in credentials: {missing_keys}")

        for key in required_keys:
            setattr(self, key, self.credentials[key])

# Implementation for Futures Tnet credentials
class BinanceCredentialsManager(ServiceCredentials):
    def __init__(self, credentials_manager: CredentialsManager, service_name='FuturesTestnet'):
        super().__init__(credentials_manager, service_name, ['api_key', 'api_secret'])

# Implementation for posgreSQL credentials
class PgCredentialsManager(ServiceCredentials):
    def __init__(self, credentials_manager: CredentialsManager, service_name='pgcurrencies'):
        super().__init__(credentials_manager, service_name, ['hostname', 'database', 'port', 'username', 'password'])
