from config import AZURE_TENANT_ID, AZURE_SCOPE, AZURE_CLIENT_ID
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer

azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=AZURE_CLIENT_ID,
    tenant_id=AZURE_TENANT_ID,
    scopes={
        AZURE_SCOPE: 'xxx'
    }
)