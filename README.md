# 🛡️ Cliente Vault com Python e Arquitetura Limpa

Este projeto é um guia prático para construir uma aplicação Python robusta e segura que consome segredos do HashiCorp Vault. Ele utiliza o método de autenticação **AppRole** e é estruturado com os princípios da **Arquitetura Limpa** para garantir um código testável, desacoplado e de fácil manutenção.

## ✨ Tabela de Conteúdos

* [Começando](#-começando)
  * [Pré-requisitos](#-pré-requisitos)
  * [Instalação](#-instalação)
* [Configuração](#-configuração)
  * [Parte A: Administrador do Vault](#parte-a-administrador-do-vault)
  * [Parte B: Aplicação Python](#parte-b-aplicação-python)
* [Executando a Aplicação](#-executando-a-aplicação)
* [Princípios Aplicados](#-princípios-aplicados)
* [Licença](#-licença)

---

## 🚀 Começando

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### 📋 Pré-requisitos

* **Python** (versão 3.9 ou superior)
* **HashiCorp Vault** (CLI e servidor)
* Um terminal com suporte a `bash`

### 🔧 Instalação

1. **Clone o repositório** (ou crie a estrutura de pastas e arquivos).

2. **Crie e ative um ambiente virtual**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate