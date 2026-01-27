# ProjectBeholder

Ferramentas para geração de datasets de IDS (Intrusion Detection System) domésticos.

> **Documentação Oficial**: Detalhes completos sobre a concepção, metodologia e resultados deste projeto encontram-se no arquivo [PG02_GustavoVentino_2026.pdf](PG02_GustavoVentino_2026.pdf).

Este projeto visa criar um ambiente controlado para geração de tráfego de rede legítimo e maliciosos, capturando dados para análise e treinamento de modelos de detecção de intrusão.

## Estrutura do Projeto

*   **`src/`**: Scripts Python para geração de tráfego simulado.
*   **`attacks/`**: Scripts e ferramentas para validar e executar ataques de rede.
*   **`containers/`**: Configurações Docker para serviços alvo (vulneráveis) e ferramentas de teste.
*   **`samples/`**: Amostras de datasets gerados (arquivos CSV).
*   **`images/`**: Diretório para armazenamento de imagens geradas ou utilizadas na análise.
*   **`ProjectBeholder.ipynb`**: Jupyter Notebook para exploração e análise dos dados coletados.

## Funcionalidades

### 1. Geração de Tráfego (`src/`)

O projeto inclui scripts para simular diferentes perfis de comportamento:

*   **Tráfego Baseline** (`src/baseline_traffic.py`): Simula o uso comum da rede (navegação, downloads) utilizando protocolos como HTTP, FTP e DNS de forma assíncrona.
*   **Tráfego IoT** (`src/iot_traffic.py`): Simula o comportamento de comunicação periódica típico de dispositivos IoT.

### 2. Simulação de Ataques (`attacks/`)

O projeto suporta a execução automatizada de diversos vetores de ataque para coleta de assinaturas:

*   **Slowloris**: Ataque de Negação de Serviço (DoS) que tenta manter muitas conexões abertas com o servidor alvo.
*   **Nmap**: Varredura de portas, detecção de versões de serviços e sistema operacional.
*   **KickThemOut**: Ferramenta para executar ataques de ARP Spoofing, desconectando dispositivos da rede local.

Os ataques podem ser orquestrados através do `Makefile` presente no diretório.

### 3. Ambiente de Testes (`containers/`)

A infraestrutura é baseada em Docker, simulando uma rede doméstica (macvlan) com diversos serviços:

*   **Web Scraper**: Um serviço web simples.
*   **Echo API**: API de eco para testes de conectividade e requisições.
*   **Echo Vulnerable**: Versão propositalmente vulnerável da API Echo.
*   **Net Tester**: Container utilitário com ferramentas de rede (scanner, attacker).

## Como usar

### Pré-requisitos
*   Docker
*   Python 3+
*   Permissões de root/sudo para manipulação de interfaces de rede.

### Configuração de Rede

O script `virtual_interface.sh` configura uma interface virtual no host para permitir comunicação com os containers na rede macvlan (que por padrão isola o host).

```bash
bash virtual_interface.sh
```

### Gerenciando o Ambiente (Containers)

Navegue até a pasta `containers/` e use o `Makefile` para gerenciar o ciclo de vida do ambiente:

```bash
cd containers
make network  # Cria a rede Docker macvlan (ajuste a interface pai 'parent=enp7s0' se necessário)
make up       # Constrói e inicia os serviços
make down     # Para e remove os containers
```

### Executando Ataques

Navegue até a pasta `attacks/` para executar rotinas de teste pré-definidas:

```bash
cd attacks
make slowloris  # Executa teste do Slowloris
make nmap       # Executa varredura Nmap
```

## Datasets

As amostras de dados capturados encontram-se em `samples/`. A nomenclatura sugere a origem e a duração da captura:
*   `GEN_*`: Dados gerados sinteticamente.
*   `REAL_*`: Dados de tráfego real.
*   `*_1H`, `*_24H`: Janelas de tempo da captura.
