# Informe final de entrega — SmartRoute AI (Fase 1, MVP académico)

**UPN · Capstone 2026-II · Grupo 2 · Corte 25/11/2026**

**Integrantes:** Julio César Córdova Díaz; Jorge Armando De la Cruz López; Flavio César García Izquierdo; Diego Alonso Olivera Rosas.

## 1. Declaración de entrega
Se entrega el **MVP académico de SmartRoute AI**, integrado en la rama `main` por el [PR #84](https://github.com/JuliusCordova/SmartRoute_AI/pull/84). Contempla operador web, aplicación Android del repartidor, seguimiento simplificado del cliente US-016, API/Gateway/Firestore, optimización OR-Tools, mapas y pruebas de integración. Las verificaciones corresponden a **staging y emulador**, no a operación productiva ni a mediciones reales de ahorro.

## 2. Alcance y control de cambios
- **Dentro de Fase 1:** gestión de pedidos, rutas, asignación, consulta de rutas, comparativa estimada US-011, autenticación y seguimiento por enlace temporal US-016 sin ETA obligatoria.
- **Fuera de Fase 1 / Fase 2:** Gemini US-012 (5 puntos); offline US-013/014 (8); piloto de campo US-015 (5); deshacer entrega, semáforo de puntualidad, exportación y mejoras de ETA.
- Base histórica **71 puntos**; recorte aprobado **18 puntos**; denominador nominal **53 puntos**. **No se publica porcentaje global ponderado certificado**, porque falta reconciliar el numerador e historia por historia. El 63,7 % es del alcance anterior; el 85,3 % es referencia aritmética no certificada, por lo que **no debe utilizarse como cierre académico**.

## 3. Evidencia de aceptación
| Frente | Resultado |
| --- | --- |
| Repositorio | PR #84 fusionado, commit `1c9104f`; CI y QA Automation del head aprobados |
| Operador | Panel Cloud Run staging; 23 pedidos y 4 rutas sintéticas, 82,4 % efectividad, 14,8 % mejora global **estimada** |
| Comparación visual US-011 | Línea base gris esquemática y optimizada vial estimada superpuestas en mapa; [evidencia](../evidence/US011_COMPARACION_VISUAL_VALIDADA_2026-11-25.md) |
| DEF-01 | Tiempos exactos en segundos, cálculo de mejora coherente, distancia/tiempo diferenciados; **19,43 % histórico excluido de resultados auditados** |
| Cliente US-016 | Estado y progreso de pedido desde enlace temporal sin cuenta del operador; ETA opcional, sin valor inventado; datos sintéticos |
| Android | APK debug compilado (33 070 890 bytes), instalado en emulador `emulator-5554`, lista y detalle de ruta comprobados. 5/5 paradas atendidas = 4 entregadas + 1 fallida |
| SEC-01 | Revocación Firebase QA registrada; token previo dio 403 por RBAC y su reutilización tras revocación recibió HTTP 401 en Gateway staging. [Evidencia](../evidence/SEC01_REVOCACION_REAL_STAGING_2026-11-25.md) |
| Capturas y APK | Capturas versionadas en `docs/evidence/android/`, `operator/`, `customer/`; [APK en Release](https://github.com/JuliusCordova/SmartRoute_AI/releases/tag/Smart_route) |

## 4. Resultados cuantitativos: exclusivamente estimados
| Ruta | Base (segundos) | Optimizada (segundos) | Ahorro de tiempo estimado |
| --- | ---: | ---: | ---: |
| `21e3de4b` | 3818 | 3350 | 12,26 % |
| `681f7f60` | 1895 | 1526 | 19,47 % |
| `aec305db` | 2178 | 1833 | 15,84 % |
| `fb413b71` | 4284 | 3659 | 14,59 % |

Fórmula: `100 * (segundos_base - segundos_optimizados) / segundos_base`. Los minutos son de presentación y pueden redondearse; no recalcular el porcentaje con minutos redondeados. Las cifras no son ahorros observados en campo.

## 5. Riesgos residuales y transferencia a Fase 2
- [#85 GPS-ORIGIN-01](https://github.com/JuliusCordova/SmartRoute_AI/issues/85): verificar procedencia GPS, diferenciar emulador/simulación/dispositivo.
- [#86 IAM](https://github.com/JuliusCordova/SmartRoute_AI/issues/86): inventariar y auditar posibles bindings duplicados / grants efectivos; **si se encuentra exceso de permisos, es bloqueante para producción**.
- [#87 ETA](https://github.com/JuliusCordova/SmartRoute_AI/issues/87): ETA fiable, con fuente, privacidad y evaluación de precisión.
- Seguridad ampliada: latencia/coste de revocación y verificación independiente de API privada; hardening, límites de solicitudes y observabilidad antes de operación real.
- PR [#80](https://github.com/JuliusCordova/SmartRoute_AI/pull/80) y [#83](https://github.com/JuliusCordova/SmartRoute_AI/pull/83): **cerrados administrativamente**, sin nueva fusión; trazabilidad conservada.

## 6. Conclusión
**Fase 1 integrada y funcionalmente demostrada para fines académicos**, bajo reservas explícitas. La firma de aceptación corresponde a cada integrante, mediante el acta separada. Ninguna firma ni aprobación ha sido simulada.

### Enlaces de entrega
- [Repositorio](https://github.com/JuliusCordova/SmartRoute_AI)
- [Release APK](https://github.com/JuliusCordova/SmartRoute_AI/releases/tag/Smart_route)
- [Operador](../evidence/operator/)
- [Cliente](../evidence/customer/)
- [Android](../evidence/android/)
