# Desafío Técnico - Análisis de Datos con QvaPay API

## Contexto

**QvaPay** es una plataforma que permite a las personas enviar y recibir dinero en diferentes monedas. Dentro de esta plataforma, existe un sistema P2P ([peer-to-peer](https://qvapay.com/p2p)) donde los usuarios pueden comprar y vender saldo de QvaPay por otras monedas. Este desafío se centra en analizar los datos de la API de QvaPay P2P para obtener información económica relevante.

Un **market maker** es un usuario que continuamente publica ofertas tanto para comprar como para vender, lo que permite mantener liquidez en el mercado. El **spread** es la diferencia entre el precio de compra (bid) y el precio de venta (ask) en un mercado.

## Tarea

### Requisitos del Ejercicio

1. **Fork del Repositorio**  
   - Crea un fork de este repositorio en tu cuenta de GitHub.
   - Crea una rama nueva con tu nombre para trabajar en la solución.

2. **Cargar y Analizar los Datos**  
   - Usa la API de QvaPay para obtener los datos del sistema P2P (API: [QvaPay API](https://qvapay.com/api/p2p)).
   - Identifica a los usuarios que son market makers.
   - Representa en una gráfica el promedio diario del **spread** de los market makers para una moneda específica (la moneda debe ser parametrizable).

3. **Volumen de Oferta y Demanda**  
   - Calcula el volumen diario de oferta (suma de las cantidades vendidas) y el volumen diario de demanda (suma de las cantidades compradas) para la moneda seleccionada.
   - Determina si la demanda supera consistentemente a la oferta o viceversa.

4. **Insights Adicionales (Opcional)**  
   - Cualquier análisis adicional que consideres relevante será valorado positivamente.

### Entrega

- Una vez finalizado el ejercicio, haz un pull request desde la rama con tu nombre.
- Documenta tu solución en el pull request, explicando:
  - Cómo ejecutar tu solución para ver los resultados. 
  - Cómo identificaste a los market makers.
  - Cómo calculaste el spread diario y representaste los datos gráficamente.
  - Cómo calculaste el volumen diario de oferta y demanda.
  - Cualquier análisis adicional que hayas realizado.

### Evaluación

Se evaluará tu capacidad para:
- Trabajar con APIs y manejar datos dinámicos.
- Implementar análisis y generar visualizaciones claras y precisas.
- Documentar tu proceso de forma efectiva y profesional.
- Presentar insights relevantes y bien fundamentados.


### Fecha Límite

Por favor, completa este desafío y envía tu pull request antes del **[jueves 16 de enero de 2025]**.

---

## Preguntas

Si tienes alguna pregunta o encuentras algún problema técnico, no dudes en contactarme.

¡Buena suerte y esperamos tus ideas innovadoras!
