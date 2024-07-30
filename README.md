# fastapi_chatapp

Chat Room with FastAPI

## How to run app?

```shell
git clone https://github.com/mamad-zahiri/fastapi_chatapp.git

cd fastapi_chatapp

chmod +x run
```

### production mode

- on linux:

  - to build services and images:

    ```shell
    ./run pro up build
    ```

    next times:

  - to stop:

    ```shell
    ./run pro stop
    ```

  - to start:

    ```shell
    ./run pro start
    ```

### development mode

- on linux:

  - to build services and images:

    ```shell
    ./run dev up build
    ```

    next times:
  
  - to stop:

    ```shell
    ./run dev stop
    ```

  - to start:

    ```shell
    ./run dev start
    ```

    NOTE: you can run `./run help` to see help
