import os
import logging
import re
from azure.identity.aio import ManagedIdentityCredential, AzureCliCredential, ChainedTokenCredential
from azure.keyvault.secrets.aio import SecretClient as AsyncSecretClient
from azure.identity import ManagedIdentityCredential, AzureCliCredential, ChainedTokenCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError

##########################################################
# KEY VAULT 
##########################################################

async def async_get_secret(secretName):
    try:
        keyVaultName = os.environ["AZURE_KEY_VAULT_NAME"]
        KVUri = f"https://{keyVaultName}.vault.azure.net"
        async with ChainedTokenCredential(
                ManagedIdentityCredential(),
                AzureCliCredential()
            ) as credential:
            async with AsyncSecretClient(vault_url=KVUri, credential=credential) as client:
                retrieved_secret = await client.get_secret(secretName)
                value = retrieved_secret.value
        return value    
    except KeyError:
        logging.info("Environment variable AZURE_KEY_VAULT_NAME not found.")
        return None
    except ClientAuthenticationError:
        logging.info("Authentication failed. Please check your credentials.")
        return None
    except ResourceNotFoundError:
        logging.info(f"Secret '{secretName}' not found in the Key Vault.")
        return None
    except Exception as e:
        logging.info(f"An unexpected error occurred: {e}")
        return None


def get_secret(secretName):
    try:
        keyVaultName = os.environ["AZURE_KEY_VAULT_NAME"]
        KVUri = f"https://{keyVaultName}.vault.azure.net"
        
        # Create the chained credential using synchronous classes.
        credential = ChainedTokenCredential(
            ManagedIdentityCredential(),
            AzureCliCredential()
        )
        
        # Create and use the SecretClient within a context manager.
        with SecretClient(vault_url=KVUri, credential=credential) as client:
            retrieved_secret = client.get_secret(secretName)
            value = retrieved_secret.value
            
        return value
        
    except KeyError:
        logging.info("Environment variable AZURE_KEY_VAULT_NAME not found.")
        return None
    except ClientAuthenticationError:
        logging.info("Authentication failed. Please check your credentials.")
        return None
    except ResourceNotFoundError:
        logging.info(f"Secret '{secretName}' not found in the Key Vault.")
        return None
    except Exception as e:
        logging.info(f"An unexpected error occurred: {e}")
        return None
