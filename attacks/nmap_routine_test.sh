#!/bin/bash

# Configuração
declare -a TARGET_IPS=("192.168.1.1" "192.168.1.10" "192.168.1.11")

# Loop infinito para que o script continue rodando
while true; do
  ### 1. Calcular o tempo de espera aleatório
  # (dentro do intervalo [10min,1h])

  # 5 minutos = 300 segundos
  # 1 hora = 3600 segundos
  # O intervalo (range) é 3600 - 300 = 3300 segundos

  # Gera um número aleatório de 0 a 3300, e então soma 300
  # Isso garante um resultado entre 300 (5 min) e 3600 (1 hora)
  RANGE=3301
  MIN_TIME=600
  RANDOM_TIME=$(($RANDOM % $RANGE + $MIN_TIME))

  echo "[INFO] Próximo scan em $RANDOM_TIME segundos (Aprox. $(($RANDOM_TIME / 60)) minutos)."
  sleep $RANDOM_TIME

  ### 2. Escolher um IP aleatório do array ###
  NUM_IPS=${#TARGET_IPS[@]}
  RANDOM_INDEX=$(($RANDOM % $NUM_IPS))
  TARGET_IP=${TARGET_IPS[$RANDOM_INDEX]}

  ### 3. Executar o Nmap Scan ###
  echo "[INFO] $(date): Executando Nmap Null Scan (-sN) em $TARGET_IP..."
  sudo nmap -sN $TARGET_IP

  echo "[INFO] Scan em $TARGET_IP concluído."
  echo "-----------------------------------"

done
