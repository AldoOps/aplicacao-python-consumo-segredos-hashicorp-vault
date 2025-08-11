# Permite apenas a leitura de segredos no caminho 'secret/data/myapp/database'
# O 'data' é necessário porque a API do motor KV v2 adiciona este prefixo.
path "secret/data/myapp/database" {
  capabilities = ["read"]
}