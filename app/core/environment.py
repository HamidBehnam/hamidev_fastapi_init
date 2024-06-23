from pydantic_settings import BaseSettings
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
clientAsync = secretmanager.SecretManagerServiceAsyncClient()


class EnvironmentVariables(BaseSettings):
    GCP_PROJECT: str
    INSTANCE_CONNECTION_NAME_REF: str
    DATABASE_IAM_USER_REF: str
    DATABASE_NAME_REF: str
    AUTH0_DOMAIN_REF: str
    AUTH0_API_AUDIENCE_REF: str
    AUTH0_ISSUER_REF: str
    AUTH0_ALGORITHMS_REF: str

    class Config:
        env_file = ".env"


environment_variables = EnvironmentVariables()


# class SettingsResolved:
#     def __init__(self):
#         self.auth0_domain = SettingsResolved.get_secret(environmentVariables.AUTH0_DOMAIN_REF)
#         self.auth0_api_audience = SettingsResolved.get_secret(environmentVariables.AUTH0_API_AUDIENCE_REF)
#         self.auth0_issuer = SettingsResolved.get_secret(environmentVariables.AUTH0_ISSUER_REF)
#         self.auth0_algorithms = SettingsResolved.get_secret(environmentVariables.AUTH0_ALGORITHMS_REF)
#         self.instance_connection_name = SettingsResolved.get_secret(environmentVariables.INSTANCE_CONNECTION_NAME_REF)
#         self.database_iam_user = SettingsResolved.get_secret(environmentVariables.DATABASE_IAM_USER_REF)
#         self.database_name = SettingsResolved.get_secret(environmentVariables.DATABASE_NAME_REF)
#
#     @staticmethod
#     def get_secret(secret_name: str):
#         project_id = environmentVariables.GCP_PROJECT
#         name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
#         response = client.access_secret_version(request={"name": name})
#         return response.payload.data.decode("UTF-8")
#
#     @staticmethod
#     async def get_secret_async(secret_name: str):
#         project_id = environmentVariables.GCP_PROJECT
#         name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
#         response = await clientAsync.access_secret_version(request={"name": name})
#         return response.payload.data.decode("UTF-8")
#
#
# settings = SettingsResolved()
