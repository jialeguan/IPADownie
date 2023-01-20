import os
import time
import pandas as pd


class History:
    def __init__(self, path: str, header=None):
        self.path = path
        if header is None:
            header = ['time', 'bundleid', 'success']
        if not os.path.exists(self.path):
            os.system(f"echo '{','.join(header)}' >> {self.path}")

    def get_bundleid_list(self):
        df = pd.read_csv(self.path)
        # success as str
        df["success"] = df["success"].astype(str)
        succ = df[df['success'] == "True"]["bundleid"].tolist()
        fail = df[df['success'] == "False"]["bundleid"].tolist()
        fatal = df[df['success'] == "Fatal"]["bundleid"].tolist()
        return succ, fail, fatal

    def resume_from_history(self, ttl: list):
        # True or Fatal
        ttl = set(ttl)
        succ, fail, fatal = self.get_bundleid_list()

        succ = set(succ) & ttl
        fatal += [x for x in fail if fail.count(x) >= 2]
        fatal = set(fatal) & ttl - succ
        wait = ttl - succ - fatal
        return list(succ), list(fatal), list(wait)

    def record(self, bundleid: str, success: str):
        record_str = f"{time.strftime('%Y-%m-%d %H:%M:%S')},{bundleid},{success}"
        os.system(f"echo {record_str} >> {self.path}")


if __name__ == "__main__":
    history = History("./log/download_history.csv")

