# PlayTingz Client

Client interface using MCP
 - Install Python 3.x
 - Create Python venv
 - Setup Flask
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
    or
    ```bash
    python -m venv .venv
    source .venv/Scripts/activate
    ```
 - Setup Flask
 - use pip to freeze dependencies
    This script gets dependencies installed and stores them in requirements text file
    ```bash
    (.venv) chukwuyenum@Yenums-MBP playtingz-client % pip freeze > requirements.txt
    ```
    This script gets list of dependencies from requirements text file and installs them into flask app
    ```bash
    (.venv) chukwuyenum@Yenums-MBP playtingz-client % pip install -r requirements.txt
    ```
 - build docker image using Dockerfile

    ```bash
    (.venv) chukwuyenum@Yenums-MBP playtingz-client % docker build -t playtingz-client:1.0 .
    (.venv) chukwuyenum@Yenums-MBP playtingz-client % docker run -d -p 80:5000 --name api playtingz-client:1.0
    (.venv) chukwuyenum@Yenums-MBP playtingz-client % docker ps
    (.venv) chukwuyenum@Yenums-MBP playtingz-client % docker rm -f api
    ```
 - write Docker compose file
 - build docker with docker-compose

    ```bash
    (.venv) chukwuyenum@Yenums-MBP playtingz-client % docker-compose build
    (.venv) chukwuyenum@Yenums-MBP playtingz-client % docker-compose up -d
    (.venv) chukwuyenum@Yenums-MBP playtingz-client % docker-compose down
    ```
 - Set up kubernetes (optional)

    ```bash
    (.venv) chukwuyenum@Yenums-MBP kubernetes % kubectl apply -f deployment.yml
    (.venv) chukwuyenum@Yenums-MBP kubernetes % kubectl get po, svc
    (.venv) chukwuyenum@Yenums-MBP kubernetes % kubectl delete -f
    ```
 - Set up helms (optional)

    ```bash
    (.venv) chukwuyenum@Yenums-MBP playtingz-client % helm create playtingz-client-api
    Creating playtingz-client-api
    (.venv) chukwuyenum@Yenums-MBP playtingz-client % cd playtingz-client-api
    (.venv) chukwuyenum@Yenums-MBP playtingz-client-api % helm install playtingz-client-api .
    (.venv) chukwuyenum@Yenums-MBP playtingz-client-api % helm uninstall playtingz-client-api
    ```

 - Fixing SQLAlchemy issue (optional)
    ```bash
    pip3 install Flask-SQLAlchemy --upgrade
    pip3 install SQLAlchemy --upgrade
    ```