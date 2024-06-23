import asyncio
from dataclasses import dataclass, fields

from fastapi import HTTPException
from google.cloud import secretmanager

from app.core.environment import environment_variables


@dataclass
class ProcessedEnvironmentVariables:
    INSTANCE_CONNECTION_NAME: str
    DATABASE_IAM_USER: str
    DATABASE_NAME: str
    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: str
    AUTH0_ISSUER: str
    AUTH0_ALGORITHMS: str


processed_environment_variables: ProcessedEnvironmentVariables = ProcessedEnvironmentVariables(
    INSTANCE_CONNECTION_NAME="",
    DATABASE_IAM_USER="",
    DATABASE_NAME="",
    AUTH0_DOMAIN="",
    AUTH0_API_AUDIENCE="",
    AUTH0_ISSUER="",
    AUTH0_ALGORITHMS="",
)


async def get_secret(secret_name: str, project_id: str, client_async) -> str:
    """Fetch a single secret asynchronously."""
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = await client_async.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


async def process_environment_variables():
    """Fetch all secrets in parallel and cache the responses."""
    loop = asyncio.get_event_loop()
    client_async = secretmanager.SecretManagerServiceAsyncClient()

    mapped_environment_variables = ProcessedEnvironmentVariables(
        INSTANCE_CONNECTION_NAME=environment_variables.INSTANCE_CONNECTION_NAME_REF,
        DATABASE_IAM_USER=environment_variables.DATABASE_IAM_USER_REF,
        DATABASE_NAME=environment_variables.DATABASE_NAME_REF,
        AUTH0_DOMAIN=environment_variables.AUTH0_DOMAIN_REF,
        AUTH0_API_AUDIENCE=environment_variables.AUTH0_API_AUDIENCE_REF,
        AUTH0_ISSUER=environment_variables.AUTH0_ISSUER_REF,
        AUTH0_ALGORITHMS=environment_variables.AUTH0_ALGORITHMS_REF,
    )

    try:
        tasks = {
            field.name: loop.create_task(
                get_secret(
                    getattr(mapped_environment_variables, field.name),
                    environment_variables.GCP_PROJECT,
                    client_async
                )
            )
            for field in fields(mapped_environment_variables)
        }
        secrets = await asyncio.gather(*tasks.values())
        secrets_dict = {
            field: resolved_secret
            for field, resolved_secret in zip(tasks.keys(), secrets)
        }

        global processed_environment_variables

        processed_environment_variables = ProcessedEnvironmentVariables(**secrets_dict)
    except Exception as e:
        print(f"Error fetching secrets: {e}")
        raise HTTPException(status_code=500, detail="Error fetching secrets")


def get_processed_environment_variables() -> ProcessedEnvironmentVariables:
    """Dependency to get cached secrets."""
    global processed_environment_variables

    if processed_environment_variables.INSTANCE_CONNECTION_NAME == "":
        raise HTTPException(status_code=500, detail="Secrets not yet fetched")

    return processed_environment_variables








# import asyncio
# from typing import List
#
# from fastapi import HTTPException
# from google.cloud import secretmanager
#
# from app.core.environment import environment_variables
#
# # Global variable for caching responses
# _cached_secrets = None
# _lock = asyncio.Lock()
#
# clientAsync = secretmanager.SecretManagerServiceAsyncClient()
#
#
# async def get_secret(secret_name: str, project_id: str) -> str:
#     """Fetch a single secret asynchronously."""
#     name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
#     response = await clientAsync.access_secret_version(request={"name": name})
#     return response.payload.data.decode("UTF-8")
#
#
# async def get_secrets_once() -> List[str]:
#     """Fetch all secrets in parallel and cache the responses."""
#     global _cached_secrets
#
#     async with _lock:  # Ensure async thread-safety
#         if _cached_secrets is None:
#             try:
#                 print('Fetching secrets.........................')
#                 secrets = [
#                     "LOCAL_INSTANCE_CONNECTION_NAME",
#                     "LOCAL_DATABASE_IAM_USER",
#                     "LOCAL_DATABASE_NAME",
#                     "LOCAL_AUTH0_DOMAIN",
#                     "LOCAL_AUTH0_API_AUDIENCE",
#                     "LOCAL_AUTH0_ISSUER",
#                     "LOCAL_AUTH0_ALGORITHMS",
#                 ]
#                 tasks = [get_secret(secret, environment_variables.GCP_PROJECT) for secret in secrets]
#                 _cached_secrets = await asyncio.gather(*tasks)
#             except Exception as e:
#                 print(f"Error fetching secrets: {e}")
#                 _cached_secrets = [{"error": str(e)}] * len(secrets)
#
#     return _cached_secrets
#
#
# def get_secrets() -> List[str]:
#     """Return the cached secrets or fetch them if not already cached."""
#     loop = asyncio.get_event_loop()
#
#     with _lock:  # Synchronous lock for thread-safety
#         if _cached_secrets is None:
#             future = asyncio.run_coroutine_threadsafe(get_secrets_once(), loop)
#             return future.result()
#
#     return _cached_secrets
#
#
# def get_cached_secrets():
#     """Dependency to get cached secrets."""
#     global _cached_secrets
#
#     # if _cached_secrets is None:
#     #     raise HTTPException(status_code=500, detail="Secrets not yet fetched")
#
#     return _cached_secrets
