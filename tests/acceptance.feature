Feature: SmartRoute AI - aceptación funcional y seguridad (especificación, tests aún no automatizados)
  Background:
    Given existe un operador y un repartidor autenticables
    And un depósito y datos sintéticos de prueba

  Scenario: AC-001 RBAC de pedidos
    Given estoy autenticado como repartidor
    When consulto GET /api/v1/orders global
    Then recibo 403

  Scenario: AC-002 coordenadas inválidas
    Given estoy autenticado como operador
    When registro un pedido con latitud 200
    Then recibo 422
    And ningún pedido se persiste

  Scenario: AC-003 asignación duplicada
    Given un pedido está asignado a una ruta activa
    When intento asignarlo a otra ruta
    Then recibo 409

  Scenario: AC-004 visibilidad de ruta
    Given hay rutas activas de distintos repartidores
    When consulto mi ruta activa
    Then solo obtengo paradas de mi usuario

  Scenario: AC-005 y AC-016 idempotencia de entrega
    Given tengo un pedido asignado en tránsito
    When envío dos veces DELIVERED con la misma Idempotency-Key
    Then se escribe un único evento
    And la respuesta es estable

  Scenario: AC-006 GPS fuera de ruta
    Given mi ruta no está activa
    When envío GPS con consentimiento previo
    Then recibo 403
    And no se persiste ubicación

  Scenario: AC-007 indicador GPS caducado
    Given la última ubicación tiene más de 2 minutos
    When consulto la ubicación
    Then el estado se muestra STALE

  Scenario: AC-008 y AC-009 optimización válida
    Given una matriz de costos completa para 8 entregas
    When optimizo respecto al orden base
    Then recibo exactamente las 8 paradas una vez
    And el porcentaje de mejora coincide con fórmula determinista

  Scenario: AC-010 ruta imposible
    Given la matriz tiene un nodo inaccesible
    When solicito optimizar
    Then recibo 422 con código ROUTE_INFEASIBLE

  Scenario: AC-011 publicación
    Given una ruta válida PLANNED
    When el operador la activa
    Then el repartidor ve la secuencia publicada

  Scenario: AC-012 KPI reproducible
    Given una lista de eventos con tiempos conocidos
    When consulto el dashboard
    Then los KPI coinciden con los cálculos de referencia

  Scenario: AC-013 Gemini sin mejora
    Given la mejora calculada es cero o negativa
    When pido explicación
    Then no se afirma ningún ahorro inexistente

  Scenario: AC-014 Gemini no escribe
    Given solicito al asistente modificar un pedido
    When pido explicación
    Then action_taken es false
    And no cambia la base de datos

  Scenario: AC-015 exportación del piloto
    Given hay métricas etiquetadas como synthetic y observed
    When exporto resultados del piloto
    Then se informa n, fuente, método, fechas y limitaciones
    And no se mezclan ambas fuentes
