# Códigos de Respuestas (Google Sheets)

En Google Sheets, las preguntas de opción se guardan como enteros (`1`, `2`, `3`, ...), no como texto.

## Variables categóricas codificadas

### `sexo`
- `1` = Masculino
- `2` = Femenino
- `3` = Otro

### `filtro_mixto`
- `1` = Sí
- `2` = No
- `3` = Me da exactamente igual

### `horario`
- `1` = Madrugador
- `2` = Nocturno

### `lugar_estudio`
- `1` = En mi habitación en silencio total
- `2` = En la sala de estudio de la residencia
- `3` = En bibliotecas públicas o facultad
- `4` = Con música o ruido ambiente

### `fines_semana`
- `1` = Sí, casi siempre
- `2` = A veces
- `3` = No, suelo volver a mi casa familiar

### `actividades_extra`
- `1` = Muy importante, no paro en casa
- `2` = Intermedio
- `3` = Soy muy casero, disfruto mi tiempo en la habitación

### `ocio_interno`
- `1` = Torneos de E-sports
- `2` = Cenas temáticas
- `3` = Maratón de series-películas
- `4` = Tardes de juegos de mesa
- `5` = Otro

### `tabaco_vapeo`
- `1` = No, y me molesta que lo hagan en la habitación
- `2` = No, pero me da igual si el otro lo hace
- `3` = Sí, fumo o vapeo

### `visitas`
- `1` = Prefiero que sea un lugar privado solo para nosotros
- `2` = Está bien de vez en cuando, avisando antes
- `3` = Me encanta que haya gente, mi cuarto está siempre abierto

### `compartir_gastos`
- `1` = Prefiero que cada uno tenga lo suyo estrictamente
- `2` = Me gusta comprar a medias y compartir
- `3` = No me importa invitar o que me cojan cosas si hay confianza

### `temperatura`
- `1` = Muy friolero, prefiero ventana cerrada
- `2` = Neutro
- `3` = Muy caluroso, necesito ventilar y dormir fresco

## Variables numéricas (se guardan tal cual)

- `edad`: 17 a 35
- `socializacion`: 1 a 10
- `orden_limpieza`: 1 a 10
- `ruido_tolerancia`: 1 a 10
- `target_nota`: 0 a 10

## Campo libre

- `ocio_interno_otro`: texto libre cuando `ocio_interno = 5`.

## Columnas A/B

Cada variable se duplica para cada persona:
- Sufijo `_A`: respuestas del iniciador.
- Sufijo `_B`: respuestas del invitado.
