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


# ==========================================
# ZONA 3: FLUXOS / ORQUESTRAÇÃO
# Juntam as validações e mandam salvar nos motores.
# ==========================================


# ==========================================
# ZONA 4: INTERFACE (O Menu Principal)
# Onde o script começa a rodar de verdade.
# ==========================================


