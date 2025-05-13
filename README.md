# PlayTingz Client

Client interface using MCP
 - Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
 - Install python 3.13
   ```bash
   uv python install 3.13
   ```
 - Install dependencies  
   
   ```bash
   uv python install 3.13
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
   
## Chat Interface

To run the chat interface, make sure to 
- install the [UnityMCPBridge](https://github.com/justinpbarnett/unity-mcp) (follow instructions)
- have unity running with the bridge active
- add location of the UnityMCPServer to the ``.env`` file. (Should be `"C:\\Users\\<USERNAME>\\AppData\\Local\\Programs\\UnityMCP\\UnityMcpServer\\src"`)
- add Anthropic API Key to ``.env`` file.

Then you should be able to run
``uv run src/client.py``