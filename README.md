# GreenHash

> **Criptomoneda educativa para incentivar el reciclaje**

---

## 1. Equipo

### 1.1 Miembros

| # | GitHub |
|---|--------|
| 1 | [@yuliu18](https://github.com/yuliu18) |
| 2 | [@sgwb1re19](https://github.com/sgwb1re19) |
| 3 | [@sgwb2fe34](https://github.com/sgwb2fe34) |
| 4 | [@sgwb2kk30](https://github.com/sgwb2kk30) |
| 5 | [@sgwb1yy10](https://github.com/sgwb1yy10) |
| 6 | [@sgwi2](https://github.com/sgwi2) |
| 7 | [@alexjandro9834](https://github.com/alexjandro9834) |
| 8 | [@sgwb1mj22](https://github.com/sgwb1mj22) |

### 1.2 Capacidades y conocimientos

El equipo cuenta con formación en:

- Programación en C y Python
- Programación segura e ingeniería del software seguro
- Bases de datos
- Seguridad en aplicaciones web
- Seguridad en servicios y protocolos de Internet
- Criptografía, identidad digital y privacidad
- Probabilidad y estadística

Estas capacidades habilitan al equipo para implementar el sistema base obligatorio y desarrollar un caso de uso realista centrado en la seguridad y la auditabilidad del programa de incentivos.

---

## 2. Proyecto

### 2.1 Producto: problema a resolver y solución propuesta

#### Problema

En programas de reciclaje con incentivos (puntos, descuentos o recompensas) suelen aparecer dificultades que reducen su eficacia y confianza:

- **Baja motivación inmediata:** el beneficio por reciclar es poco tangible y la participación es irregular.
- **Falta de transparencia:** el usuario no puede verificar fácilmente cómo se asignan las recompensas.
- **Riesgo de fraude y abuso:** doble contabilización de entregas, suplantación o manipulación de recompensas.
- **Barrera tecnológica y de adopción:** si el sistema es complejo, disminuye el uso.
- **Impactos no deseados:** incentivos mal calibrados pueden generar comportamiento oportunista o problemas operativos.

#### Solución propuesta

Desarrollar una criptomoneda educativa basada en el sistema base obligatorio (protocolo común) y aplicarla al ámbito del reciclaje mediante un programa de recompensas canjeables.

La propuesta contempla:

- Usuarios con wallets (clave pública) que reciben recompensas en criptomoneda por entregas en puntos autorizados.
- Recompensas canjeables por productos reciclados u otras recompensas ofrecidas por entidades colaboradoras.
- Registro verificable de la asignación y uso de recompensas a través de transacciones válidas del sistema.

#### Visión

Si la aplicación existiera, reciclar sería una acción cotidiana con retorno inmediato y verificable: los usuarios obtendrían recompensas transparentes por su contribución y podrían canjearlas en un catálogo de beneficios sostenibles, fomentando un circuito local de economía circular.

---

### 2.2 Utilidad para ingenieros de software o de seguridad

**Para ingenieros de software:**

- Caso de uso completo con actores, flujos y reglas verificables sobre un sistema transaccional.
- Diseño consistente de datos y operaciones (monedas, transacciones y validación) en un escenario realista de recompensas.

**Para ingenieros de seguridad:**

- Análisis y tratamiento de amenazas típicas: fraude en recompensas, suplantación y abuso del sistema.
- Necesidad de trazabilidad, integridad y auditabilidad para reforzar la confianza del programa.
- Consideración explícita de privacidad y reticencias de adopción.

**Ventajas colaterales:**

- Concienciación ambiental mediante incentivos medibles y visibles.
- Transparencia del programa y mejora de confianza para usuarios y colaboradores.
- Valor social: fomento de hábitos sostenibles y apoyo a productos basados en materiales reciclados.

---

### 2.3 Viabilidad técnica y de recursos

**Viabilidad técnica:**

- El núcleo se basa en el sistema base obligatorio, incluyendo transacciones TRANSFER, SPLIT y MERGE, comisión al Estado y validación (firmas, no doble gasto, conservación de valor y límite de 100 monedas por wallet).
- El programa de recompensas se integra como escenario de uso: asignación de recompensas y gasto posterior mediante transacciones del sistema.
- La demostración puede realizarse en un entorno controlado (laboratorio/campus) con puntos autorizados simulados si no hay hardware real.

**Riesgos a considerar:**

- Reticencia al uso por complejidad de wallets y gestión de claves.
- Privacidad: posible correlación de actividad si se asocian wallets a personas o ubicaciones.
- Fraude/abuso: doble contabilización o colusión entre usuario y punto autorizado.
- Eficiencia operativa: gestión de puntos autorizados, verificación y posibles cuellos de botella.
- Gaming del sistema por incentivos mal calibrados.

---

### 2.4 Estado del arte: productos similares y características diferenciales

**Sistemas similares:**

- Programas de puntos y recompensas por reciclaje (apps o tarjetas).
- Esquemas de depósito y retorno (incentivo económico por envases).
- Máquinas de devolución (reverse vending) con recompensas asociadas.
- Soluciones digitales de trazabilidad/incentivos, incluyendo propuestas basadas en blockchain a nivel conceptual.

**Carencias habituales detectadas:**

- Gestión de recompensas opaca y difícil de auditar por el usuario.
- Controles antifraude limitados o poco explicables.
- Baja integración entre participación (entrega) y uso de recompensas con trazabilidad completa.

**Características diferenciales de nuestra propuesta:**

- Uso de una criptomoneda educativa con reglas explícitas y verificables para gestionar incentivos.
- Transparencia y auditabilidad del reparto y gasto de recompensas.
- Enfoque centrado en seguridad aplicada (fraude, abuso, privacidad) desde el planteamiento del caso de uso.
- Alineación con economía circular: recompensas orientadas a productos/beneficios sostenibles.

---

### 2.5 Restricciones e información adicional

**Limitaciones y dependencias:**

- Cumplimiento estricto del sistema base obligatorio (incluyendo bloque génesis común y reglas obligatorias).
- Necesidad de definir y mantener consistentes los formatos de datos del sistema (transacciones, monedas, bloques) dentro del equipo.
- Dependencia de un mecanismo de firma/verificación para autenticar transacciones.
- Alcance limitado por disponibilidad del equipo y calendario académico.

**Organización del equipo:**

- Por motivos de disponibilidad de algunos miembros, las reuniones se realizarán por norma general de forma online, ya que algunos compaginan los estudios con su trabajo.
