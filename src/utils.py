import os
import pandas as pd


def get_apps_from_ipa_dir(ipa_dir: str) -> dict:
    if not os.path.exists(ipa_dir):
        print(f"[!] {ipa_dir} not exists")
        return {}

    return {file.split("_")[0]: os.path.join(ipa_dir, file) for file in os.listdir(ipa_dir) if file.endswith(".ipa")}


def get_apps_from_app_dir(ipa_dir: str) -> dict:
    if not os.path.exists(ipa_dir):
        print(f"[!] {ipa_dir} not exists")
        return {}

    res = {}
    for directory in os.listdir(ipa_dir):
        path = os.path.join(ipa_dir, directory)
        if not os.path.isdir(path):
            continue
        if directory.startswith("."):
            continue
        app_name = directory
        res[app_name] = path

    return res


def get_apps_from_csv(csv_path: str) -> list:
    if not os.path.exists(csv_path):
        print(f"[!] {csv_path} not exists")
        return []

    df = pd.read_csv(csv_path)
    if "bundleid" not in df.columns:
        print("No bundleid column in the csv file")
        return []

    return df["bundleid"].tolist()
