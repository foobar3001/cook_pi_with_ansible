#!/usr/bin/python
# vim: fileencoding=utf-8

# host_settingを読み込みinventoryを生成する
# host_settingからはdefaultsをまず読み込み
# そのあとホスト毎の設定を読み込む
# host_settingのnew_ipに対してpingを送信し、
# 応答があった場合:
#   すでに設定済みとみなして、
#   new_ipを接続先のホスト
#   new_ansible_ssh_userを接続先のユーザ
#   公開鍵認証が設定されている
#   としてパラメータを返却する
# 応答がない場合:
#   まだ設定されていないものとみなして、
#   キー値に設定されたipを接続先のホスト
#   piを接続先のユーザ
#   raspberryを接続先のパスワード
#   としてパラメータを返却する
import subprocess
import json
import yaml
import re


# コマンドを利用したpingの実行
# 参照元ページ
# https://www.hadacchi.com/wp_blog/2220.html
def ping_test(hosts):
    loss_pat = '0 received'
    for host in hosts:
        ping = subprocess.Popen(
            ["ping", "-c", "1", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, error = ping.communicate()
        for line in out.splitlines():
            if line.find(loss_pat) > -1:  # パケット未到着ログの抽出
                return False
        return True


# 辞書のディープコピー
def deepupdate(dict_base, other):
    for k, v in other.items():
        if isinstance(v, dict) and k in dict_base:
            deepupdate(dict_base[k], v)
    else:
        dict_base[k] = v


if __name__ == '__main__':

    # ファイル読み込み
    host_setting_root = {}
    with open("./host_setting.yml") as f:
        host_setting_root = yaml.load(f)

    defaults = host_setting_root.get("defaults", {})
    hosts = host_setting_root["hosts"]

    # 出力用パラメータ
    output_hosts = []
    output_host_vars = {}

    # ホスト毎に設定
    for host, setting in hosts.items():
        # デフォルト値と各ホスト値をマージ
        host_setting = defaults.copy()
        deepupdate(host_setting, setting)

        # CIDR表記のIPをIP部分とサブネット部分に分離する
        new_ip_cidr = host_setting["new_ip_cidr"]
        new_ip = re.match('(.*)/(.*)', new_ip_cidr).group(1)

        # 設定先のIPがアクセス可能であれば設定先のIPを接続先ホストとする
        if ping_test([new_ip]):
            output_hosts.append(new_ip)
            host_var = host_setting["host_var"]
            host_var["new_ip"] = new_ip
            host_var["new_ip_cidr"] = new_ip_cidr
            host_var["ansible_ssh_user"] = host_setting["new_ansible_ssh_user"]
            output_host_vars[new_ip] = host_var
        else:
            output_hosts.append(host)
            host_var = host_setting["host_var"]
            host_var["new_ip"] = new_ip
            host_var["new_ip_cidr"] = new_ip_cidr
            host_var["ansible_ssh_user"] = "pi"
            host_var["ansible_ssh_pass"] = "raspberry"
            output_host_vars[host] = host_var

    # 出力
    output = {
        "_meta": {
            "hostvars": output_host_vars
        },
        "all": {
            "children": [
                "pis"
            ]
        },
        "pis": {
            "hosts": output_hosts,
            "children": []
        },
    }

    print(json.dumps(output))
