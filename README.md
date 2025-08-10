Bienvenido 👋  
<b>RemindEnBot</b> es un proyecto de Bot en Telegram que te ayuda a recordar palabras en <b>inglés</b>, <b>español</b>, <b>portugués</b>, <b>francés</b> o <b>italiano</b>, <i>1 vez a la semana</i>. El día será aleatorio en este rango de tiempo. <br>

Para usar este proyecto localmente, se debe realizar los siguientes pasos:

1. ### Clonar el repositorio:
   ``` bash 
    git clone  https://github.com/luismrios1602/ReminderEnBot.git
   ```
2. ### Montar el entorno de desarrollo 
   El proyecto trabaja con venv por lo que es necesario realizar los siguientes pasos para correr el proyecto:
   * #### Crear el entorno virtual de python 
     ``` bash 
     python3 -m venv venv
     ```
   * #### Activar el entorno virtual
       <i> Linux </i>

       ``` bash
       source venv/bin/activate
       ```
        
     <i> Windows (Powershell) </i>

     ``` bash
     venv\Scripts\Activate.ps1
     ```
        
   * #### Instalar las dependencias del proyecto en el entorno virtual
     ``` bash
     pip install -r requirements.txt 
     ```
   
   * #### Crear archivo de variables de entorno
     ``` bash
     mkdir .env.local
     ```
     
   * #### Asignar variables de entorno en el archivo <i>.env.local</i>
     ``` text
     TELEGRAM_TOKEN = "[AQUI TU TOKEN DEL BOT]"
     MY_CHAT_ID = [AQUI EL NUMERO DE TU CHAT ID EN TELEGRAM PARA COSAS DE ADMIN QUE REQUIERAS QUE SOLO VEAS TÚ EN EL BOT]
     MYSQL_HOST = "[HOST ex: localhost]"
     MYSQL_USERNAME = "[USERNAME DE LA CONEXION A MYSQL]"
     MYSQL_PASSWORD = "[PASSWORD DE LA CONEXION A MYSQL]"
     MYSQL_DATABASE = "[NOMBRE DE LA BASE DE DATOS PARA ALMACENAR LAS PALABRAS ex: reminden]"
     MYSQL_PORT = "[TU PUERTO DE MYSQL ex: 3306]"
     HORA_MORNING = [HORA EN LA QUE SE EMPEZARAN A ENVIAR LOS MENSAJES ex: 8]
     HORA_NIGHT = [HORA EN LA QUE SE DEJARAN DE ENVIAR LOS MENSAJES ex: 22 ]
     ```
     Importante: Reemplazar [TEXTO] por los valores reales, manteniendo las comillas donde se requiera.

3. ### Base de datos
    Se debe crear la base datos (El nombre de preferencia, aunque sugerido que sea reminden).
    Luego creamos las tablas ubicadas en la carpeta ./SQL.

4. ### Desplegar el proyecto
    Dentro del venv ejecutamos el siguiente comando: 
    ``` bash 
    python bot.py --l 
    ```
   
    - <b>python</b>: Debe ser el python ubicado en venv/bin/python3. Si ya se encuentra dentro del venv no es necesario especificarlo completo.
    - <b>bot.py</b>: El main del proyecto. Asegúrese estar ubicado en la carpeta ReminderEnBot de la shell donde se ejecute.
    - <b>--l</b>: Entorno en el que se ejecutará el proyecto (l de local)
      - Puede crear otros archivos .env.otro y agregar la lógica en el método getEnv() del archivo <i>classes/ConfigClass.py</i>