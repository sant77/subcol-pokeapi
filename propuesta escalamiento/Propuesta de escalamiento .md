# 🚀Propuesta para el escalamiento de la aplicación en n8n + aws + python

Para escalar la solución y soportar un alto volumen de trabajo, es necesario migrar desde la arquitectura monolítica predeterminada de n8n hacia un modelo basado en colas (queue mode), el cual habilita el escalamiento horizontal tanto del motor de flujos (n8n) como del microservicio en Python.

## 🏗️ Arquitectura con colas y workers

El primer paso para lograr esta modularización es modificar el archivo docker-compose, agregando las variables de entorno necesarias para activar el queue mode de n8n. Esto permite separar los componentes en:

-	n8n Main: instancia responsable de la interfaz visual, el disparo de workflows y la comunicación con Redis.
-	n8n Workers: procesos independientes dedicados exclusivamente al procesamiento de tareas en paralelo.

Con estas consideraciones, la arquitectura queda de la siguiente manera:

1. **n8n Main**
-	Eje-cuta la interfaz visual.
-	Inicia los workflows.
	Realiza la primera fase del flujo: extracción y validación del documento.
-	Envía las tareas a Redis para su procesamiento asíncrono.
2. **Extracción previa (primer paso del flujo)**
La extracción del archivo se ejecuta antes de encolar la tarea.
Esto es crítico por varias razones:
-	Los documentos PDF ya llegan convertidos a JSON, por lo que la extracción es ligera.
-	Ahorrar peso en la cola (Redis) mejora el rendimiento del sistema, ya que Redis opera en memoria.
-	Se detectan errores temprano: si el JSON no es válido, el flujo se detiene sin ocupar workers ni saturar la cola.
-	Los workers procesan únicamente las partes más pesadas: API externa, lógica del servicio Python, comparación, etc.
Al encolar solo JSON limpio y validado, el sistema se vuelve más estable, rápido y escalable.

3. **Redis como motor de colas** 

Redis se utiliza como sistema de mensajes entre n8n Main y los n8n Workers.
Redis almacena:
-	tareas livianas listas para procesar
-	trabajos pendientes cuando los workers están ocupados
-	estado de ejecución de cada workflow
Redis no almacena PDF, ni binarios, sino únicamente los datos ya extraídos.
Esto garantiza un throughput alto, bajo consumo de memoria y mínima latencia.

4. **n8n Workers**
Son instancias dedicadas exclusivamente al procesamiento en paralelo:
-	consumen mensajes desde Redis
-	hacen llamadas a APIs externas (p. ej., Apoc API)
-	realizan la lógica de decisión
-	se comunican con el microservicio Python
Cada worker consume CPU y memoria, por lo que es necesario ajustar su número mediante pruebas de carga.
________________________________________
5. **Escalamiento del microservicio en Python**
El microservicio que procesa los Pokémon también puede escalar para evitar convertirse en un cuello de botella, por lo tanto se propone:

-	AWS Lambda: escalamiento inmediato a miles de invocaciones, pago por uso.

________________________________________
6. **Integración con un servicio de colas de AWS (opcional)**
Si se requiere una arquitectura aún más desacoplada, se puede incorporar AWS SQS entre n8n y Python.
Ventajas:
-	Persistencia garantizada (no depende de RAM)
-	Desacople total entre n8n y Python
-	Ideal para cargas masivas o sistemas distribuidos
En ese caso Redis se usa para los workers de n8n, y SQS para las tareas que van hacia Python.
Diagrama de arquitectura

7. **Diagrama de arquitectura**

 El diagrama de la solución es el siguiente:

[Diagrama de arquitectura](https://www.mermaidchart.com/d/a9611c24-418a-4b94-8348-1929a219e259)

## 📈 Escalamiento vertical y pruebas de carga
Aunque el escalado horizontal aumenta la capacidad de procesamiento, este depende de los recursos físicos disponibles en el servidor o entorno de despliegue. Cada worker de n8n consume CPU y memoria, por lo que se recomienda realizar pruebas de carga para determinar cuántos workers puede soportar la infraestructura sin degradación.
También debe considerarse el escalamiento vertical:
-	Más CPU = mayor capacidad para procesar flujos pesados (PDF, APIs, lógica).
-	Más RAM = mayor estabilidad con workers concurrentes.
En entornos productivos es común combinar escalado vertical + horizontal para obtener el mejor rendimiento posible.

## 🔁 Orquestador con retry automático

Para el seguimiento de las colas, además de lo mencionado anteriormente, es posible agregar una arquitectura para generar un orquestador que permita generar un re try automatico para controlar el alto flujo de entradas.

Esta arquetectura seria otro flujo independiente con colas creadas por redis. Se expone como un elemento separado porque a pesar de ser importante el flujo puede realizarse sin el orquestador y el re try se puede realizar con SQS. Sin embargo esta opción a pesar de agregar mayor complejidad permite un control total.

[Fuente para las opciones de escalamiento](https://www.youtube.com/watch?v=mJw4MJRGt24&t=1096s)

[Diagrama del orquestador](https://www.mermaidchart.com/d/afe178f7-fb31-4cb3-b430-7af3ffcf54ea)

## 🏷️Versionamiento y despliegue
Para mantener un control estructurado de versiones se propone utilizar un esquema estándar de etiquetado:
usuario-docker/nombre-servicio:1.0.0
Donde:
-	1 = versión mayor
-	0 = cambios importantes compatibles
-	0 = correcciones menores

Las imágenes deben subirse a un registro remoto, como Docker Hub o Amazon ECR, especialmente si la infraestructura opera en la nube.
El archivo docker-compose.yml debe mantenerse bajo control de versiones en GitHub. Además, se recomienda incluir un pipeline de CI/CD (con GitHub Actions, por ejemplo) que ejecute:
1.	Generación de la imagen Docker.
2.	Publicación en el registro remoto.
3.	Despliegue automático en la infraestructura (VPS, EC2, ECS, etc.).

Esto asegura reproducibilidad, trazabilidad y despliegues consistentes.

## 📜 Centralización de logs

Para mantener un registro claro y unificado del comportamiento del sistema, se propone centralizar los logs en un único servicio de observabilidad. Dado que la solución se apoya en AWS, la opción más adecuada es CloudWatch Logs, el cual se integra fácilmente con aplicaciones basadas en Docker.
Para ello puede instalarse y configurarse el AWS CloudWatch Agent en el servidor (o usar el driver de logs de Docker si todo se ejecuta en contenedores). Este agente recopila los logs generados por:
-	n8n Main
-	n8n Workers
-	Servicio Python
-	Redis (opcional)

y los envía a CloudWatch, donde pueden visualizarse, filtrarse y analizarse. Esto es esencial en arquitecturas distribuidas, ya que facilita identificar cuellos de botella, errores y picos de carga.

Es importate mencionar que esta opción no solo permite recolectar logs sino insight importantes como:

- Tiempos de ejecuión
-	Numero de workers en trabajo
- Número de entradas exitosas 
- Número de entradas fallidas 


## 🔐 IAM y seguridad
Se recomienda seguir el principio de Least Privilege:
-	Cada servicio debe tener solo los permisos estrictamente necesarios.
-	n8n solo debe leer/escribir en su cola (Redis o SQS).
-	Python solo debe poder consumir su propia cola y hacer sus llamadas externas.
-	Roles separados para despliegue, ejecución y logging.

Esto es una recomendación oficial de AWS y evita configuraciones peligrosas en producción.


