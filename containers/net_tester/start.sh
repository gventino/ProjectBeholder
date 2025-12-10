#!/bin/bash

./scanner.sh &
./attacker.sh &

# Espera qualquer processo sair
wait -n

# Sai com o status do processo que terminou primeiro
exit $?
