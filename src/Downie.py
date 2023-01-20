import os
import sys
import json
from src.utils.ipa_file import get_apps_from_csv
from src.utils.log import *
from src.History import History


class Downie:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, "r") as f:
            config = json.loads(f.read())

        self.em = config["email"]
        self.pw = config["password"]
        self.period = config["period"]
        self.log_dir = config["log_dir"]
        self.tmp_dir = config["tmp_dir"]
        self.download_dir = config["download_dir"]

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        self.log = os.path.join(self.log_dir, "download.log")
        self.history = History(os.path.join(
            self.log_dir, "download_history.csv"))

        # load time from last login
        last_login_path = os.path.join(self.log_dir, "last_login.txt")
        if os.path.exists(last_login_path):
            self.last_login = float(open(last_login_path, "r").read())
        else:
            self.last_login = 0

        self.ttl = []
        self.succ = []
        self.fail = []
        self.fatal = []
        self.wait = []

    def lazy_login(self, force=False):
        if not force and time.time() - self.last_login < self.period:
            return

        # echo_str = f"{time.strftime('%Y-%m-%d %H:%M:%S')} login"
        # os.system(f"echo {echo_str} >> {self.log}")

        # cmd = f"ipatool auth login -e {self.em} -p {self.pw} >> {self.log}"
        cmd = f"ipatool auth login -e {self.em} -p {self.pw}"
        os.system(cmd)

        self.last_login = time.time()
        # save to file
        with open(os.path.join(self.log_dir, "last_login.txt"), "w") as f:
            f.write(str(self.last_login))

    def download(self, bundleid: str, ipa_dir: str):
        log_file = os.path.join(self.tmp_dir, f"{bundleid}.log")
        # stderr & stdout to log file
        cmd = f"ipatool download --purchase -b {bundleid} -o {ipa_dir} > {log_file} 2>&1"
        os.system(cmd)

        log = open(log_file, "r").read()
        # success
        if "ERR" not in log:
            os.remove(log_file)
            return "True"

        # expired
        if "expired" in log:
            self.lazy_login(force=True)
            os.remove(log_file)
            return "False"

        if "failed to send request" in log:
            os.remove(log_file)
            return "False"

        if "failed to write file" in log:
            os.remove(log_file)
            return "False"

        # failed
        if "failed to find app" in log:
            os.remove(log_file)
            return "Fatal"

        if "paid apps" in log:
            os.remove(log_file)
            return "Fatal"

        if "license is required" in log:
            final_log = log_final(len(self.succ), len(
                self.fail), f"Download {bundleid}")
            print(final_log)
            with open(self.log, "a") as f:
                f.write(final_log + '\n')
            os.remove(log_file)
            os.system("say 'download dropped'")
            sys.exit(1)

        # print the tail of log
        print(f"Unsolved error, please check the log file {log_file}")
        print('\n'.join(log.splitlines()[-5:]))
        sys.exit(1)

    def download_batch(self, file_path: str):
        job_name = os.path.basename(file_path).split(".")[0]
        download_dir = os.path.join(self.download_dir, job_name)
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        self.ttl = get_apps_from_csv(file_path)
        self._download_batch(download_dir)

        os.system("say 'download finished'")

        final_log = log_final(len(self.succ), len(
            self.fail), f"Download {download_dir}")
        print(final_log)
        with open(self.log, "a") as f:
            f.write(final_log + '\n')

    def _download_batch(self, download_dir: str):
        self.succ, self.fatal, self.wait = self.history.resume_from_history(
            self.ttl)
        self.fail = []

        try:
            for i, bundleid in enumerate(self.wait):
                self.lazy_login()

                print(log_status(len(self.succ), len(
                    self.fail), i, len(self.wait), bundleid))

                success = self.download(bundleid, download_dir)
                self.history.record(bundleid, success)
                if success == "True":
                    self.succ.append(bundleid)
                elif success == "False":
                    self.fail.append(bundleid)
                elif success == "Fatal":
                    self.fail.append(bundleid)
                    self.fatal.append(bundleid)
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            sys.exit(1)

        if self.fail:
            # retry
            self._download_batch(download_dir)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 IPADownloadHelper.py bundleids.csv")
        sys.exit(1)

    helper = Downie()
    helper.download_batch(sys.argv[1])
