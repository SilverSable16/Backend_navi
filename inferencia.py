def aplicar_inferencia(entrada, reglas):
    entrada = entrada.lower()
    for antecedente, consecuente in reglas:
        if antecedente in entrada:
            return consecuente
    return None
