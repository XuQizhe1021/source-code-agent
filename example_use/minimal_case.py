import os
import time
import requests


def main() -> None:
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000/api").rstrip("/")
    seed = str(int(time.time()))
    username = f"example_user_{seed}"
    password = "ExamplePass123!"

    session = requests.Session()

    register_payload = {
        "username": username,
        "password": password,
        "name": "Example User",
        "email": f"{username}@example.com",
        "role": "admin"
    }
    register_resp = session.post(f"{base_url}/auth/register", json=register_payload, timeout=30)
    print("REGISTER:", register_resp.status_code)
    if register_resp.status_code != 200:
        print(register_resp.text[:400])
        return

    login_payload = {
        "username": username,
        "password": password,
        "remember": False
    }
    login_resp = session.post(f"{base_url}/auth/login", json=login_payload, timeout=30)
    print("LOGIN:", login_resp.status_code)
    if login_resp.status_code != 200:
        print(login_resp.text[:400])
        return

    token = login_resp.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    providers_resp = session.get(f"{base_url}/models/providers", timeout=30)
    print("PROVIDERS:", providers_resp.status_code)
    if providers_resp.status_code == 200:
        providers = providers_resp.json()["data"]
        print("PROVIDERS_COUNT:", len(providers))
        print("PROVIDERS_SAMPLE:", [p["value"] for p in providers[:5]])

    graph_payload = {
        "name": f"示例图谱_{seed}",
        "description": "example_use 最小案例创建",
        "config": {"from": "example_use"}
    }
    graph_resp = session.post(f"{base_url}/graphs/", headers=headers, json=graph_payload, timeout=30)
    print("CREATE_GRAPH:", graph_resp.status_code)
    if graph_resp.status_code == 200:
        graph_id = graph_resp.json()["data"]["id"]
        print("GRAPH_ID:", graph_id)
        upload_resp = session.post(
            f"{base_url}/graphs/{graph_id}/files/upload",
            headers=headers,
            files=[("files", ("example.txt", b"hello graph from example_use", "text/plain"))],
            timeout=60
        )
        print("UPLOAD_FILE_TO_MINIO:", upload_resp.status_code)
        if upload_resp.status_code != 200:
            print(upload_resp.text[:400])

        neo4j_test_resp = session.post(f"{base_url}/graphs/{graph_id}/neo4j-test", headers=headers, timeout=30)
        print("NEO4J_TEST:", neo4j_test_resp.status_code)
        if neo4j_test_resp.status_code == 200:
            body = neo4j_test_resp.json()
            print("NEO4J_TEST_STATUS:", body.get("data", {}).get("status"))
        else:
            print(neo4j_test_resp.text[:400])
    else:
        print(graph_resp.text[:400])


if __name__ == "__main__":
    main()
