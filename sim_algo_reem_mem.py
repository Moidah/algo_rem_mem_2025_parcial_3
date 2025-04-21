#!/usr/bin/env python
from collections import OrderedDict

marcos_libres = [0x0,0x1,0x2]
reqs = [ 0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A ]
segmentos =[ ('.text', 0x00, 0x1A),
            ('.data', 0x40, 0x28),
            ('.heap', 0x80, 0x1F),
            ('.stack', 0xC0, 0x22),
           ]

from collections import OrderedDict

def procesar(segmentos, reqs, marcos_libres):
    paginas = {}  # Diccionario para mapear (nombre, pagina_logica) a marcos
    lru = OrderedDict()  # Lista para manejar el orden de uso de las páginas (LRU)
    resultados = []  # Lista para almacenar los resultados

    for req in reqs:
        segmento_actual = None

        # Buscar el segmento correspondiente
        for nombre, base, limite in segmentos:
            if base <= req < base + limite:
                segmento_actual = (nombre, base, limite)
                break

        if segmento_actual is None:
            resultados.append((req, 0x1FF, "Segmentation Fault"))
            continue

        nombre, base, limite = segmento_actual
        pagina_logica = (req - base) // 16  # Determina la página lógica
        offset = (req - base) % 16  # Determina el desplazamiento dentro de la página
        clave = (nombre, pagina_logica)  # La clave para identificar la página

        # Si la página ya está en memoria
        if clave in paginas:
            marco = paginas[clave]
            # Mueve la página a la posición más reciente en LRU
            lru.move_to_end(clave)
            resultados.append((req, marco * 16 + offset, "Marco ya estaba asignado"))
        else:
            # Si hay marcos libres, asignamos uno
            if marcos_libres:
                marco = marcos_libres.pop(0)  # Extraemos un marco libre
                paginas[clave] = marco  # Asignamos el marco a la página
                lru[clave] = True  # Añadimos a LRU como la más reciente
                resultados.append((req, marco * 16 + offset, "Marco libre asignado"))
            else:
                # Si no hay marcos libres, aplicamos el reemplazo LRU
                reemplazado, _ = lru.popitem(last=False)  # Extraemos la página menos recientemente utilizada
                marco_reemplazado = paginas[reemplazado]  # Obtenemos el marco de la página a reemplazar
                del paginas[reemplazado]  # Elimina la página reemplazada

                # Asignamos el marco del reemplazo a la nueva página
                paginas[clave] = marco_reemplazado
                lru[clave] = True  # Añadimos la nueva página a LRU
                resultados.append((req, marco_reemplazado * 16 + offset, "Marco asignado"))

    return resultados


def print_results(results):
    for result in results:
        print(f"Req: {result[0]:#0{4}x} Dirección Física: {result[1]:#0{4}x} Acción: {result[2]}")


if __name__ == '__main__':
    # Prueba del código con datos de ejemplo
    marcos_libres = [0x0, 0x1, 0x2]
    reqs = [0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A]
    segmentos = [
        ('.text', 0x00, 0x1A),
        ('.data', 0x40, 0x28),
        ('.heap', 0x80, 0x1F),
        ('.stack', 0xC0, 0x22),
    ]

    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)


