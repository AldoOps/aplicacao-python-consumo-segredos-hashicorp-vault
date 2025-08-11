import os
import hvac
from abc import ABC, abstractmethod
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# CAMADA DE DOMÍNIO (Entities)
# Representa as estruturas de dados centrais do seu negócio.
# ---------------------------------------------------------------------------

@dataclass
class DatabaseCredentials:
    """
    Uma entidade de domínio que representa as credenciais de um banco de dados.
    É uma estrutura de dados simples, sem lógica complexa.
    """
    user: str
    password: str

# ---------------------------------------------------------------------------
# CAMADA DE APLICAÇÃO (Use Cases & Interfaces)
# Contém a lógica de aplicação e define as "portas" (interfaces) para a
# camada de infraestrutura.
# ---------------------------------------------------------------------------

class SecretRepository(ABC):
    """
    Define um contrato (interface) para um repositório de segredos.
    A lógica de negócio não sabe *como* os segredos são obtidos (Vault, arquivo, etc.),
    apenas que pode pedi-los através deste contrato.
    """
    @abstractmethod
    def get_database_credentials(self, path: str) -> DatabaseCredentials:
        pass

class GetDatabaseCredentialsUseCase:
    """
    Este é o caso de uso principal. Ele orquestra a obtenção das credenciais.
    Ele depende da abstração (SecretRepository), não da implementação concreta.
    """
    def __init__(self, secret_repository: SecretRepository):
        self._repository = secret_repository

    def execute(self, secret_path: str) -> DatabaseCredentials:
        """Executa o caso de uso para buscar as credenciais."""
        print(f"INFO: Executando caso de uso para buscar credenciais em '{secret_path}'")
        return self._repository.get_database_credentials(secret_path)

# ---------------------------------------------------------------------------
# CAMADA DE INFRAESTRUTURA (Frameworks & Drivers)
# Implementa os detalhes técnicos: como falar com o Vault, como ler
# configurações e como apresentar os dados.
# ---------------------------------------------------------------------------

class VaultSecretRepository(SecretRepository):
    """
    Implementação concreta do repositório de segredos que usa o HVAC para
    se comunicar com o HashiCorp Vault.
    """
    def __init__(self, vault_addr: str, role_id: str, secret_id: str):
        print("INFO: Inicializando cliente Vault...")
        try:
            self._client = hvac.Client(url=vault_addr, verify=False)
            print("INFO: Tentando autenticar com AppRole...")
            hvac.api.auth_methods.AppRole(self._client.adapter).login(
                role_id=role_id,
                secret_id=secret_id,
            )
            if not self._client.is_authenticated():
                raise ConnectionError("Falha na autenticação com AppRole.")
            print("✅ Autenticação com AppRole bem-sucedida!")
        except Exception as e:
            # Encapsula a exceção original para não vazar detalhes da biblioteca
            raise ConnectionError(f"Erro ao conectar ou autenticar no Vault: {e}")

    def get_database_credentials(self, path: str) -> DatabaseCredentials:
        """Busca as credenciais do Vault e as converte para a entidade de domínio."""
        try:
            print(f"INFO: Lendo segredo do Vault no caminho: 'secret/{path}'")
            response = self._client.secrets.kv.v2.read_secret_version(
                mount_point='secret',
                path=path,
                raise_on_deleted_version=True,
            )
            secret_data = response['data']['data']
            
            # Converte o dicionário do Vault para a nossa entidade de domínio
            return DatabaseCredentials(
                user=secret_data.get('user'),
                password=secret_data.get('password')
            )
        except hvac.exceptions.Forbidden:
            raise PermissionError("Permissão negada. Verifique a política do Vault.")
        except hvac.exceptions.InvalidPath:
            raise FileNotFoundError(f"Caminho do segredo '{path}' não encontrado no Vault.")
        except Exception as e:
            raise RuntimeError(f"Erro inesperado ao ler o segredo: {e}")

class Config:
    """Classe responsável por carregar e validar as configurações do ambiente."""
    def __init__(self):
        self.vault_addr = os.getenv('VAULT_ADDR')
        self.role_id = os.getenv('APPROLE_ROLE_ID')
        self.secret_id = os.getenv('APPROLE_SECRET_ID')
        self._validate()

    def _validate(self):
        if not all([self.vault_addr, self.role_id, self.secret_id]):
            raise ValueError("As variáveis de ambiente VAULT_ADDR, APPROLE_ROLE_ID, e APPROLE_SECRET_ID devem ser definidas.")

def present_credentials(credentials: DatabaseCredentials):
    """Função de apresentação: exibe os dados no console."""
    print("\n--- Credenciais Obtidas com Sucesso ---")
    print(f"  Usuário do DB: {credentials.user}")
    print(f"  Senha do DB:   {credentials.password}")
    print("--------------------------------------")

# ---------------------------------------------------------------------------
# PONTO DE ENTRADA (main.py)
# Orquestra a criação e injeção de dependências.
# ---------------------------------------------------------------------------

def main():
    """
    Função principal que monta a aplicação, injeta as dependências
    e executa o caso de uso.
    """
    try:
        # 1. Carrega as configurações (Camada de Infraestrutura)
        config = Config()

        # 2. Cria a implementação do repositório (Camada de Infraestrutura)
        vault_repository = VaultSecretRepository(
            vault_addr=config.vault_addr,
            role_id=config.role_id,
            secret_id=config.secret_id
        )

        # 3. Cria o caso de uso, injetando a dependência (Camada de Aplicação)
        get_credentials_use_case = GetDatabaseCredentialsUseCase(
            secret_repository=vault_repository
        )

        # 4. Executa o caso de uso
        secret_path = 'myapp/database'
        credentials = get_credentials_use_case.execute(secret_path)

        # 5. Apresenta o resultado (Camada de Infraestrutura)
        present_credentials(credentials)

    except (ValueError, ConnectionError, PermissionError, FileNotFoundError, RuntimeError) as e:
        print(f"\n❌ ERRO: {e}")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO NA APLICAÇÃO: {e}")


if __name__ == "__main__":
    main()