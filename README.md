# Electoral Systems Analsis

Conjunto de funciones asociadas al reparto de representantes de un sistema electoral, dentro del marco implementado por la constitución española de 1978.  

## Cómo comenzar
Las funciones que contiene este paquete están desarroladas utilizando `Python 3.8`.

### Requirements
Los paquetes que utiliza estas funciones son: 
- [Pandas](https://pandas.pydata.org/)

### Instalación
```
pip install electoral-system-analysis
```

## Contenido

Las funciones dentro del paquete `electoral-systems-analysis` se dividen en tres grupos.

### Limpia de datos

Dentro de `clean_electoral_data.py` se pueden encontrar las diferentes funciones usadas para limpiar los datos de las elecciones generales sacados del [ministerio de interior](https://infoelectoral.interior.gob.es/opencms/es/elecciones-celebradas/area-de-descargas/).

Cada proceso electoral tiene su función propia debido a que cada proceso tiene una estructura de datos distinta. Además en muchos casos se ha tenido que hacer un preprocesamiento manual posterior a los resultados de la limpia.

- 2023 Julio: https://docs.google.com/spreadsheets/d/1caYOQNjlfU5ygxCR9EK3ZSCCrGlS7mJxNXMVLWhybzg/edit#gid=1260496320
- 2019 Noviembre: https://docs.google.com/spreadsheets/d/16hnM4m8h453KBpRzQB0FYljixHatGQsvJxLzrKHt16c/edit#gid=838017858

### Distribución de escaños por region

En `distribution_regions.py` encontramos diferentes maneras de repartir los escaños entre las regiones. Por defecto el sistema utiliza la metodología de [LOREG](http://www.juntaelectoralcentral.es/cs/jec/ley?idContenido=23758&p=1379062388933&template=Loreg/JEC_Contenido).

## Distribución de escaños por partído

En `distribution_formulas` podemos encontrar diferentes fórmulas de reparto de escaños entre partidos como:
- Ley de D'Hondt `dhondt`: https://es.wikipedia.org/wiki/Sistema_D%27Hondt
- Sainte-Laguë`sainte_lague` y `sainte_lague_modificado`: https://es.wikipedia.org/wiki/M%C3%A9todo_Sainte-Lagu%C3%AB
- Cociente de Hare`hare`: https://es.wikipedia.org/wiki/Cociente_Hare
- Cociente de Droop `droop`: https://es.wikipedia.org/wiki/Cociente_Droop
- Cociente de Imperiali`imperiali`: https://es.wikipedia.org/wiki/Cuota_Imperiali
- Cociente de Hagenbach-Bischoff `hagenbach`: https://es.wikipedia.org/wiki/Cuota_Hagenbach-Bischoff

Podemos acceder a los diferentes métodos a traves de la función `get_distribution_formula` mediante las keys que aparecen arriba.

### Score de Proporcionalidad
Para medir la proporcionalidad del sistema se ha creado una función que suma el valor absoluto de la diferencia del porcentaje de votos de cada partido y su porcentaje de representantes. Esta suma se la resta a 1, de tal manera que un sistema en el que coincida el porcentaje de votos y de escaños obtendrá una porporcionalidad del 100%.
```commandline
score_proportionality = 1 - SUM(ABS(votes_percent - representatives_percents))
```

Este score sirve para poder comparar y detectar aquellos sistemas electorales en donde haya menos relación entre el porcentaje de representantes con los de votos.

## Autor

  - **Santiago Arran Sanz**
    ([santhiperbolico](https://github.com/santhiperbolico/))
