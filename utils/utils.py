import re

# funcion para realizar escape de string
def escapar_caracteres_especiales(text):
    caracteres_reservados = r'|!.-[]()~`<>#+={}'
    for char in caracteres_reservados:
        text = text.replace(char, '\\' + char)
    return text

# funcion para eliminar caracteres especiales de una palabra para que no se rompa el nombre del archivo
def dropEspecialCaracters(text):
    caracteres_reservados = r'|?!.-[]()~`<>#+={}¿'
    for char in caracteres_reservados:
        text = text.replace(char, '')
    return text

# funcion para validar si un texto contiene caracteres reservados
def contiene_caracteres_especiales(text):
    caracteres_reservados = r'|!.-[]()~`<>#+={}'
    return(bool(re.search(caracteres_reservados, text)))