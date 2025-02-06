import os
import json

class CredentialsManager:
    def __init__(self,folder_name = 'keys',file_name = 'keys.json'):
        self._folder_name = folder_name
        self._file_name = file_name
        self.credentials_path = self.read_credentials() if self.read_credentials else print('No credentials')
        self.credentials_list = self.get_credentials()


    def read_credentials(self):
        folder_name, file_name = self._folder_name, self._file_name
        dir_path = os.path.dirname(os.getcwd())
        folders = [folder for folder in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, folder))]

        for folder in folders:
            if folder == folder_name:
                folder_path = os.path.join(dir_path, folder)
                files = [file for file in os.listdir(folder_path)]
                for file in files:
                    if file==file_name:
                        return os.path.join(folder_path,file_name)

        return None

    def get_credentials(self):
        json_path = self.credentials_path
        with open(json_path, "r") as file:
            data = json.load(file)

        return data


    def get_service_credentials(self,service_name,group="passwords"):
            passwords = self.credentials_list.get(group, [])
            for entry in passwords:
                if entry["service"] == service_name:
                    return entry
                
            return None
    
class CredentialsManagerBase:
    def __init__(self, manager: CredentialsManager, service_name: str, required_keys: list):
        self._manager = manager.get_service_credentials(service_name)
        self.required_keys = required_keys
        self.set_credentials()

    def set_credentials(self):
        try:
            for key in self.required_keys:
                setattr(self, key, self._manager[key])
            
            print('Credentials set')
        
        except KeyError as e:
            print(f"Missing key in credentials: {e}")
        except Exception as e:
            print(f"Error setting credentials: {e}")

class BinanceCredentialsManager(CredentialsManagerBase):
    def __init__(self, manager: CredentialsManager, service_name='FuturesTestnet'):
        required_keys = ['api_key', 'api_secret']
        super().__init__(manager, service_name, required_keys)

class PgCredentialsManager(CredentialsManagerBase):
    def __init__(self, manager: CredentialsManager, service_name='pgcurrencies'):
        required_keys = ['hostname', 'database', 'port', 'username', 'password']
        super().__init__(manager, service_name, required_keys)



