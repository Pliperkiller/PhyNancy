from tools import credential_manager


if __name__ == '__main__':

    credentials = credential_manager.CredentialsManager()
    pg_credentials = credential_manager.PgCredentialsManager(credentials)

    print(credentials.credentials_path)