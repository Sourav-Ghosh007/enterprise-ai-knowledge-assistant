from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

key_vault_url = "https://enterprise-rag-kv-2026.vault.azure.net/"

credential = DefaultAzureCredential()

client = SecretClient(
    vault_url=key_vault_url,
    credential=credential
)

secret = client.get_secret("AZURE-OPENAI-API-KEY")

print("Secret retrieved successfully!")
print("Secret name:", secret.name)