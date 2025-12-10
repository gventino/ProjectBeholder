FROM python:3-slim

# 1. Instalar dependências de sistema (Nmap e Git)
RUN apt-get update && \
    apt-get install -y nmap git procps && \
    rm -rf /var/lib/apt/lists/*

# 2. Instalar o Slowloris do repositório gkbrk
# Clonamos o repo, tornamos executável e criamos um link simbólico para o PATH
RUN git clone https://github.com/gkbrk/slowloris.git /opt/slowloris && \
    chmod +x /opt/slowloris/slowloris.py && \
    ln -s /opt/slowloris/slowloris.py /usr/local/bin/slowloris

# 3. Configurar diretório de trabalho
WORKDIR /app

# 4. Copiar os scripts para dentro do container
COPY scanner.sh /app/scanner.sh
COPY attacker.sh /app/attacker.sh
COPY start.sh /app/start.sh

# 5. Dar permissão de execução aos scripts
RUN chmod +x /app/scanner.sh /app/attacker.sh /app/start.sh

# 6. Definir o entrypoint
CMD ["./start.sh"]
