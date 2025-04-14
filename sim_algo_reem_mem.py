#!/usr/bin/env python

marcos_libres = [0x0,0x1,0x2]
reqs = [ 0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A ]
segmentos =[ ('.text', 0x00, 0x1A),
             ('.data', 0x40, 0x28),
             ('.heap', 0x80, 0x1F),
              ('.stack', 0xC0, 0x22),
             ]

def procesar(segmentos, reqs, marcos_libres):
    paginas = {}  
    lru = []  
    resultados = []

    for req in reqs:
        segmento_actual = None

        for nombre, base, limite in segmentos:
            if base <= req < base + limite:
                segmento_actual = (nombre, base, limite)
                break

        if segmento_actual is None:
            resultados.append((req, 0x1FF, "Segmention Fault"))
            continue

        nombre, base, limite = segmento_actual
        pagina_logica = (req - base) // 16
        offset = (req - base) % 16
        clave = (nombre, pagina_logica)

        if clave in paginas:
            marco = paginas[clave]
            if clave in lru:
                lru.remove(clave)
            lru.append(clave)
            resultados.append((req, marco * 16 + offset, "Marco ya estaba asignado"))
        else:
            if marcos_libres:
                marco = marcos_libres.pop(0)
                paginas[clave] = marco
                lru.append(clave)
                resultados.append((req, marco * 16 + offset, "Marco libre asignado"))
            else:
                reemplazado = lru.pop(0)
                marco = paginas[reemplazado]
                del paginas[reemplazado]
                paginas[clave] = marco
                lru.append(clave)
                resultados.append((req, marco * 16 + offset, "Marco asignado"))

    return resultados
    
def print_results(results):
    for result in results:
        print(f"Req: {result[0]:#0{4}x} Direccion Fisica: {result[1]:#0{4}x} Acción: {result[2]}")

if __name__ == '__main__':
    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)

