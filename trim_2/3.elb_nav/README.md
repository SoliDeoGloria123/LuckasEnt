# 🎉 Bienvenido a LuckasEnt 🎉

## ¿Qué es LuckasEnt?

**LuckasEnt** 🚀 es una plataforma que permite comparar precios de la canasta familiar en diferentes supermercados de Colombia, ayudando a los consumidores a tomar decisiones informadas y ahorrar dinero en sus compras. Su misión es empoderar a los compradores, y su visión es convertirse en la plataforma líder en comparación de precios. Ofrece una interfaz amigable para encontrar ofertas y descuentos, facilitando el ahorro de tiempo y dinero al comparar los precios de más de 1000 productos diariamente. El 70% de los colombianos utiliza este servicio para optimizar sus compras.

## Pasos para clonar el repositorio

1.  Clonar el repositorio:

    ```bash
    git clone https://github.com/SoliDeoGloria123/LuckasEnt.git
    ```
2.  Preferiblemente te recomendamos usar la terminal de WSL para mayor rapidez y no tener que trabajar con máquinas virtuales. Si no sabe cómo instalarlo, recomendamos ver este short:

    [https://youtube.com/shorts/IyHBfXNJwI4?si=1D8sngf\_sId7sv-Z](https://youtube.com/shorts/IyHBfXNJwI4?si=1D8sngf_sId7sv-Z)

## Instalación de Docker

Una vez instalado WSL, es hora de instalar Docker. Si no sabe cómo instalarlo, recomendamos este video:

[https://youtu.be/ZO4KWQfUBBc?si=cpTl\_nNCQGxCR9UF](https://youtu.be/ZO4KWQfUBBc?si=cpTl_nNCQGxCR9UF)

Link de Instalación de Docker Desktop Aqui:
[https://docs.docker.com/get-started/get-docker/](https://docs.docker.com/get-started/get-docker/)

Si no sabe qué es Docker, vea este video:

[https://youtu.be/SMqdC6g6Y2o?si=-Zd1wAyTfCIgRxdx](https://youtu.be/SMqdC6g6Y2o?si=-Zd1wAyTfCIgRxdx)

### ¿Para qué utilizamos Docker?

Utilizamos Docker para correr todo el sistema sin necesidad de una máquina virtual. Docker permite crear contenedores que encapsulan la aplicación y todas sus dependencias, asegurando que funcione de manera consistente en cualquier entorno.

## Configuración del Proyecto

Una vez instalado Docker y clonado el repo:

1.  Escribe en tu terminal WSL (Ubuntu o la que usted quiera) donde clonó el repo:
    ```bash
    ls
    ```
    para ver si se clonó correctamente el repo.
2.  Da clic izquierdo sobre la terminal para pegar esto:
    ```bash
    cd LuckasEnt/trim_2/3.elb_nav/
    ```
    y dele enter, que permitirá acceder a la ubicación del proyecto.
3.  Escribe el comando:
    ```bash
    code .
    ```
    y de clic en enter en su teclado para abrir VS Code en base a la ubicación del proyecto.
4.  Cuando aparezca VS Code, ejecute el comando en VS Code para abrir una nueva terminal para mayor comodidad, o también puede seguir usando la terminal con la que abrió VS Code.
5.  Una vez que haya abierto la terminal, por favor dentro de VS Code, busque en la barra exploradora un archivo llamado `.env.example` donde encontrará la estructura de un archivo `.env`, el cual sirve para no colocar directamente las claves de Google ni del cluster de Mongo, cosas que son muy delicadas.
6.  Ejecute los siguientes comandos para crear un archivo `.env`:
    ```bash
    touch .env
    ```

    o

    ```bash
    cp .env.example .env
    ```

    o también puede crear el archivo manualmente en la barra exploradora de VS Code, pero asegúrese de que se llame `.env` y no `.env.txt` o algo así. Si no ve el archivo `.env`, es porque no tiene activada la opción de ver archivos ocultos. Para ello, presione `Ctrl + Shift + P` y busque "Toggle Hidden Files" y dele enter.


7. Una vez creado, tiene que estar el archivo al nivel del `README.md`, del `dockerfile`, y del `requirements.txt`. Reemplace, copie el contenido:

    ```properties
    MONGO_URI=your_mongo_uri
    SENDER_EMAIL=your_email
    SENDER_PASSWORD=your_password
    SECRET_KEY=your_secret_key
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    ```

    **OJO AQUÍ:** Debe pedir a los administradores del proyecto las claves (por ejemplo, todo lo que está en minúscula: `your_mongo_uri`) y debe pegar el contenido proporcionado de los admins sin espacios al `=`, sin usar comillas.
    
8.  Después de haber instalado WSL, instalado Docker para WSL, clonado el repo en la terminal de WSL, y tenido el archivo `.env` con sus claves, por favor, cree un archivo llamado `client_secret.json`, el cual le permitirá recordar cuáles son los accesos a Google OAuth, así como se ve en el archivo `client_secret_example.json`, y rellene los campos que le piden que empiecen con la palabra `your`. Tendrá que pedirle al admin que le dé credenciales para colocar los datos en ese JSON.

## Ejecución del Proyecto

Después de eso, para ver la parte bonita, el frontend corriendo, ejecute los siguientes comandos en la terminal:

```bash
docker build -t luckasent .
docker run -p 5001:5001 --network=host -v $(pwd)/SRC:/app/SRC luckasent
```

Si no le funciona el anterior, corra este:
```bash
docker run -p 5001:5001 -v $(pwd)/SRC:/app/SRC luckasent
```

## Comandos Útiles de Docker
Es importante que esté familiarizado con los comandos de Docker.

-Con esto elimina la imagen:
```bash
docker image rmi -f luckasent
```


Si tiene dudas, contacte a el siguiente correo: **luckas.entorno@gmail.com**