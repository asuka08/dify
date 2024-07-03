import requests
import typer
from typing_extensions import Annotated
from rich import print
from pathlib import Path
import urllib.parse
import yaml

app = typer.Typer()
tool_app = typer.Typer()
app.add_typer(tool_app, name="tool", help="工具")
app_app = typer.Typer()
app.add_typer(app_app, name="app", help="应用")

from_base = "http://42.193.112.247:82"
from_email = "gaoxin@synergence.cn"

to_base = "https://workflow.syngents.cn"
to_email = "syner@synergence.cn"

from_login = requests.post(f"{from_base}/console/api/login", json={
    "email": from_email,
    "password": "Aa123456",
    "remember_me": True
})
from_token = from_login.json().get("data")
from_auth_header = {"Authorization": f"Bearer {from_token}"}

to_login = requests.post(f"{to_base}/console/api/login", json={
    "email": to_email,
    "password": "Aa123456",
    "remember_me": True
})
to_token = to_login.json().get("data")
to_auth_header = {"Authorization": f"Bearer {to_token}"}


@tool_app.command("1", help="迁移工具")
def import_tool(
        tool_name: Annotated[str, typer.Argument(help="工具名称")]
):
    from_tool_data = requests.get(
        f"{from_base}/console/api/workspaces/current/tool-provider/api/get?provider={urllib.parse.quote(tool_name)}",
        headers=from_auth_header).json()

    from_tool_data.pop("tools")
    from_tool_data["provider"] = tool_name
    to_tool_exist = not requests.get(
        f"{to_base}/console/api/workspaces/current/tool-provider/api/get?provider={urllib.parse.quote(tool_name)}",
        headers=to_auth_header).json().get("status") == 400
    if (to_tool_exist):
        from_tool_data["original_provider"] = tool_name
        result = requests.post(
            f"{to_base}/console/api/workspaces/current/tool-provider/api/update", json=from_tool_data,
            headers=to_auth_header)
        print(result.json())
    else:
        result = requests.post(
            f"{to_base}/console/api/workspaces/current/tool-provider/api/add", json=from_tool_data,
            headers=to_auth_header)
        print(result.json())


# python dify_tools.py app 1 f22246d6-3c1b-47dd-a56a-b5ba05ab1c05 6f2f13c5-06e1-4f99-b0dc-738b1fb7d35a
@app_app.command("1", help="迁移应用")
def import_app(
        app_id: Annotated[str, typer.Argument(help="应用id")],
        to_app_id: Annotated[str, typer.Argument(help="导入应用id")] = None
):
    from_app_data = requests.get(
        f"{from_base}/console/api/apps/{app_id}",
        headers=from_auth_header).json()

    if from_app_data["mode"] not in ["workflow", "advanced-chat"]:
        result = requests.post(
            f"{to_base}/console/api/apps/{to_app_id}/model-config", json=from_app_data["model_config"],
            headers=to_auth_header).json()
        print(result)
    else:
        draft = requests.get(f"{from_base}/console/api/apps/{app_id}/workflows/draft", headers=from_auth_header).json()
        to_draft = requests.get(f"{to_base}/console/api/apps/{to_app_id}/workflows/draft",
                                headers=to_auth_header).json()
        result = requests.post(
            f"{to_base}/console/api/apps/{to_app_id}/workflows/draft", json={
                "graph": draft["graph"],
                "features": draft["features"],
                "hash": to_draft["hash"]
            },
            headers=to_auth_header).json()
        print(result)
        result = requests.post(
            f"{to_base}/console/api/apps/{to_app_id}/workflows/publish",
            headers=to_auth_header).json()
        print(result)


@app_app.command("2", help="导入新app")
def import_new_app(
        app_id: Annotated[str, typer.Argument(help="应用id")]
):
    from_app = requests.get(f"{from_base}/console/api/apps/{app_id}/export", headers=from_auth_header).json()["data"]

    # 读取 YAML 文件
    config = yaml.safe_load(from_app)
    # 打印读取到的内容
    to_tool_providers = requests.get(f"{to_base}/console/api/workspaces/current/tool-providers",
                                     headers=to_auth_header).json()
    tool_dict = dict((f"{provider['type']}_{provider['name']}", provider["id"]) for provider in to_tool_providers)
    if config["app"]["mode"] in ["workflow", "advanced-chat"]:
        for node in config["workflow"]["graph"]["nodes"]:
            if node["data"]["type"] == "tool":
                if node["data"]["provider_type"] in ["api", "workflow"]:
                    node["data"]["provider_id"] = tool_dict[
                        f'{node["data"]["provider_type"]}_{node["data"]["provider_name"]}']

    config = yaml.dump(config)

    result = requests.post(
        f"{to_base}/console/api/apps/import",
        headers=to_auth_header, json={"data": config}).json()
    print(result)


if __name__ == '__main__':
    app()
