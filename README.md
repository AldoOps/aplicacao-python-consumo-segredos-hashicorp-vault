# Cliente Vault com Python e AppRole

Um projeto de exemplo que demonstra a forma segura e moderna de uma aplicação Python se autenticar no **HashiCorp Vault** usando o método **AppRole** e consumir segredos seguindo o princípio do **privilégio mínimo**.

Este repositório é resultado de um guia passo a passo, evoluindo de uma conexão simples com token raiz para uma arquitetura de segurança mais robusta — ideal para ambientes de produção (com as devidas adaptações).

---
✨ **Tabela de Conteúdos**

- [Sobre o Projeto](#sobre-o-projeto)  
- [Começando](#começando)  
- [Pré-requisitos](#pré-requisitos)  
- [Instalação e Configuração](#instalação-e-configuração)  
  - [Parte A — Configuração do Vault (Admin)](#parte-a---configuração-do-vault-admin)  
  - [Parte B — Configuração da Aplicação (Usuário)](#parte-b---configuração-da-aplicação-usuário)  
- [Executando a Aplicação](#executando-a-aplicação)  
- [Princípios de Segurança Aplicados](#princípios-de-segurança-aplicados)  
- [Próximos Passos](#próximos-passos)  
- [Licença](#licença)

---

## 📖 Sobre o Projeto

O objetivo principal é fornecer um exemplo claro e prático de como integrar aplicações com o Vault, evitando práticas inseguras como o uso de tokens estáticos e de longa duração. A implementação foca em autenticação máquina-a-máquina (AppRole) e leitura de segredos com permissões mínimas.

**Tecnologias utilizadas**

- Python 3.9+  
- HashiCorp Vault (server + CLI)  
- HVAC — cliente Python para o Vault

---

## 🚀 Começando

Siga as instruções abaixo para configurar e executar o projeto em seu ambiente local. O guia está dividido entre ações de administrador do Vault (parte A) e ações do desenvolvedor/aplicação (parte B).

---

## 📋 Pré-requisitos

- Python 3.9 ou superior  
- HashiCorp Vault (servidor e CLI) instalado localmente ou acessível remotamente  
- Terminal com suporte a Bash (Linux, macOS, WSL no Windows)

---

## 🔧 Instalação e Configuração

### Parte A — Configuração do Vault (Função: Admin)

> **Atenção:** Os comandos abaixo usam `vault server -dev` para testes locais. **Não use o modo `-dev` em produção.**

1. **Inicie o servidor Vault (em um terminal separado para testes):**

```bash
vault server -dev
```

> ⚠️ Copie o *Root Token* exibido no início — você precisará dele para os comandos seguintes.

2. **Exporte variáveis de ambiente do Admin (para o CLI):**

```bash
export VAULT_ADDR="http://127.0.0.1:8200"
export VAULT_TOKEN="s.SEU_ROOT_TOKEN_AQUI"
```

3. **Habilite o método de autenticação AppRole:**

```bash
vault auth enable approle
```

4. **Crie a política mínima de acesso** (arquivo `myapp-policy.hcl`):

```hcl
# myapp-policy.hcl
# Permite apenas a leitura do segredo específico da nossa aplicação
path "secret/data/myapp/database" {
  capabilities = ["read"]
}
```

5. **Aplique a política no Vault:**

```bash
vault policy write myapp-policy myapp-policy.hcl
```

6. **Crie o AppRole e associe a política a ele:**

```bash
vault write auth/approle/role/myapp-role     token_policies="myapp-policy"     token_ttl="1h"     secret_id_ttl="10m"
```

7. **Obtenha o RoleID (público) e o SecretID (secreto):**

```bash
# RoleID (pode ser lido várias vezes)
vault read auth/approle/role/myapp-role/role-id

# SecretID (é gerado aqui; guarde-o — pode ser mostrado apenas uma vez quando escrito com -f)
vault write -f auth/approle/role/myapp-role/secret-id
```

8. **Crie um segredo para a aplicação ler (exemplo):**

```bash
vault kv put secret/myapp/database user="user_dinamico" password="SenhaSuperSecreta123!"
```

> 🔑 Guarde o `RoleID` e o `SecretID` gerados — eles serão usados pela aplicação para autenticar via AppRole.

---

### Parte B — Configuração da Aplicação Python (Usuário / Desenvolvedor)

1. **Clone este repositório** ou copie o arquivo exemplo `app_vault.py` para o seu projeto.

2. **Crie e ative um ambiente virtual:**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências:**

```bash
pip install hvac
```

> Opcional: crie um `requirements.txt` com `hvac` para controle de dependências.

4. **Exporte as variáveis de ambiente da aplicação:**

```bash
export VAULT_ADDR="http://127.0.0.1:8200"
export APPROLE_ROLE_ID="SEU_ROLE_ID_AQUI"
export APPROLE_SECRET_ID="SEU_SECRET_ID_AQUI"
```

> No Windows (PowerShell), use `setx` ou `$env:VAR="valor"` conforme sua preferência.

---

## ▶️ Executando a Aplicação

Com tudo configurado, execute o script Python (ex.: `app_vault.py`):

```bash
python app_vault.py
```

**Saída esperada** (exemplo):
```
Tentando autenticar com AppRole...
✅ Autenticação com AppRole bem-sucedida! Token de cliente foi definido.

Tentando ler o segredo em: 'secret/myapp/database'
✅ Segredo lido com sucesso!
   - Usuário do DB: user_dinamico
   - Senha do DB: SenhaSuperSecreta123!
```

Se ocorrer algum erro, verifique: variáveis de ambiente, se o Vault está em execução, se a política permite leitura do caminho correto e se `RoleID`/`SecretID` foram informados corretamente.

---

## 🛡️ Princípios de Segurança Aplicados

- **Autenticação máquina-a-máquina (AppRole):** método recomendando para aplicações se autenticarem sem usar tokens humanos.  
- **Princípio do menor privilégio:** a policy `myapp-policy` limita a aplicação a ler apenas `secret/data/myapp/database`.  
- **Credenciais de curta duração:** `SecretID` e tokens têm TTLs curtos (configuráveis), reduzindo a janela de risco.  
- **Zero segredos no código:** o código não contém `RoleID`/`SecretID`/tokens — tudo passa por variáveis de ambiente.  

---

## 💡 Próximos Passos (e melhorias sugeridas)

- **Entrega segura do SecretID**: estudar formas seguras de fornecer o `SecretID` à aplicação em produção (Kubernetes Secrets com RBAC, Vault Agent, HashiCorp Boundary, ou CI/CD seguro).  
- **Renovação automática de tokens**: implementar refresh automático antes do token expirar.  
- **Segredos dinâmicos**: migrar para o Database Secrets Engine do Vault para criar credenciais dinâmicas por tempo limitado.  
- **Observabilidade**: adicionar logging estruturado e métricas.  
- **Testes**: criar testes unitários e de integração que simulem o Vault (usar mocks ou um Vault de teste).

---

## 📝 Licença

Este projeto é fornecido sob a licença **MIT** — sinta-se à vontade para adaptar para uso pessoal ou empresarial, lembrando de seguir boas práticas de segurança em ambientes de produção.

---

## Contato

Se quiser, posso também: gerar o arquivo `requirements.txt`, adicionar um `app_vault.py` de exemplo baseado nas instruções que você forneceu, ou criar um `Dockerfile`/`docker-compose` para facilitar testes locais. Quer que eu adicione algum desses agora?
