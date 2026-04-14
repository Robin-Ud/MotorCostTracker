
"""
otimo, então acho que deve dar pra fracionar as funções, seguindo o DRY a captura de valores pra coluna valor e litros/oque pode ser utilizado funções especificas

como estarei lidando com usuario final a validação de inputs é essencial, valores negativos, odo menor que o anterior, valores diferentes das opções nos menus de seleção devem sere re solicitados

a captura de inputs deve ser documentada e bem demarcada pra caso haja a migração da linha de comando para TUI ou GUI

e Keep It Simple Stupid
"""

import csv
import json
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


