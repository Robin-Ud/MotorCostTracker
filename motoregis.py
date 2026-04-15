"""
MotoRegis - Motor Cost Tracker
---------------------------------------------------------
Manifesto de Desenvolvimento:
1. KISS (Keep It Simple, Stupid): Priorize a simplicidade. 
   Se uma lógica pode ser resolvida com menos linhas e menos pacotes, faça-o.
2. DRY (Don't Repeat Yourself): Funções de captura e validação devem ser genéricas.
3. Baixa Fricção: O fluxo deve ser otimizado para uso rápido via Termux.
4. Portabilidade: Dados em CSV para garantir que o usuário seja dono da informação.
5. Agnosticismo de Interface: A lógica de validação deve ser isolada da captura
   de input, facilitando futura migração para TUI/GUI.

Desenvolvido por: @Robin-Ud
Licença: GNU GPLv3
---------------------------------------------------------
"""

import json
import csv
import os
from datetime import datetime


# ==========================================
# ZONA 1: MOTORES DE DADOS (JSON e CSV)
# Funções burras. Elas só leem e escrevem, não tomam decisões.
# ==========================================

# ==========================================
# ZONA 2: VALIDADORES (As fundações)
# Garantem que o usuário não digite letras onde vai número, etc.
# ==========================================

def select_index(msg, range_max):
    while True:
        try:
            # O input e a conversão precisam estar DENTRO do try
            buffer = int(input(msg))
            
            # range(1, 5) vai de 1 a 4. 
            # Se você quer incluir o range_max, use range_max + 1
            if buffer in range(0, range_max + 1):
                return buffer
            else:
                print(f'❌ Digite apenas valores de 0 a {range_max}')
        except ValueError:
            print('❌ Por favor, digite apenas números inteiros')

def get_float(msg):
    while True:
        # 1. Captura a string primeiro
        entrada = input(msg).strip().replace(',', '.')
        try:
            # 2. Tenta converter
            valor = float(entrada)
            if valor >= 0:
                return valor
            else:
                print('❌ Digite apenas valores maiores ou iguais a 0')
        except ValueError:
            print('❌ Digite apenas numerais')            
            




# ==========================================
# ZONA 3: FLUXOS / ORQUESTRAÇÃO
# Juntam as validações e mandam salvar nos motores.
# ==========================================


# ==========================================
# ZONA 4: INTERFACE (O Menu Principal)
# Onde o script começa a rodar de verdade.
# ==========================================


