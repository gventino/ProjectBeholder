#!/bin/bash
declare -a TARGET_IPS=("192.168.1.1" "192.168.1.10" "192.168.1.11")

while true; do
  RANGE=601
  MIN_TIME=30
  RANDOM_TIME=$(($RANDOM % $RANGE + $MIN_TIME))

  echo "[NMAP-SCAN] Próximo scan em $RANDOM_TIME segundos."
  sleep $RANDOM_TIME

  NUM_IPS=${#TARGET_IPS[@]}
  RANDOM_INDEX=$(($RANDOM % $NUM_IPS))
  TARGET_IP=${TARGET_IPS[$RANDOM_INDEX]}

  echo "[NMAP-SCAN] $(date): Executando Nmap Null Scan (-sN) em $TARGET_IP..."
  nmap -sN $TARGET_IP

  echo "[NMAP-SCAN] Scan em $TARGET_IP concluído."
  echo "-----------------------------------"
done
