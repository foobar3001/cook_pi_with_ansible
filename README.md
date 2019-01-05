# Cook Pi with Ansible
Raspberry Piの初期設定をAnsibleで自動化します。
設定する内容は以下の通りです。
 - ユーザの追加
 - sshの設定
   - 公開鍵暗号方式によるログインのみに限定する
   - rootのログインを禁止する
 - 静的IPの設定

このツールはRaspberry Piに割り振られているIPアドレスに対して、静的IPアドレス、他必要な設定項目を設定ファイルに記述して、`ansible-playbook`を実行することでRaspberry Piの設定を行います。

このツールは設定ファイルから静的IPアドレスを読み込み、静的IPアドレスに対して、まずpingによる死活監視を行い、
静的IPアドレスから返答があれば、既にIPアドレスの設定がされているものと見なし、
静的IPアドレスに対してansibleによる設定を行います。

# 動作確認環境
 - Ansible 実行環境
     - VirtualBox 6.0 + CentOS 7
     - Ansible 2.7
     - Python 2.7


 - Raspberry Pi
   - Raspberry Pi 3 Model B
   - Raspberry Pi 2 Model B

# 事前準備
## Ansible実行側の準備
秘密鍵は`~/.ssh/id_rsa`、
公開鍵は`~/.ssh/id_rsa.pub`を利用します。
もしまだ鍵を生成していない場合には、以下のコマンドを実行することで鍵を生成します

```
$ ssh-keygen -t rsa -b 4096 -C "あなたのメールアドレス"
Enter file in which to save the key (/Users/you/.ssh/id_rsa): [Press enter] 何も入力せずEnter
Enter passphrase (empty for no passphrase): [Type a passphrase] パスフレーズを入力
Enter same passphrase again: [Type passphrase again]  パスフレーズを再入力
```

参照ページ
https://qiita.com/suthio/items/2760e4cff0e185fe2db9

## Raspberry Piの準備
Raspberry Piをsshでログインできる状態にして、
DHCP等でRaspberry Piに割り当てられたIPを予め調査してください。

参考ページ
https://qiita.com/nori-dev-akg/items/a8361e728a66a8c3bdba

# 利用方法
gitからcloneします。
```
git clone https://github.com/foobar3001/cook_pi_with_ansible.git cook_pi_with_ansible
```

`host_setting.yml`を編集し、
設定対象のRaspberry PiのIPアドレスと、
それに対応する設定を行います。以下は設定例です。
```
defaults:
   new_ansible_ssh_user: "foobar3000"
   host_var:
     router_ip: "192.168.0.1"
     dns_ip: "192.168.0.64"

hosts:
    "192.168.0.28":
        new_ip_cidr: "192.168.0.68/24"
        new_ansible_ssh_user: "foobar3000"
```
 項目 | 任意/必須 | 説明
---- | ---- | ----
router_ip | 必須 | ルータのIP
dns_ip | 必須 | DNSサーバのIP
new_ip_cidr | 必須 | 設定先の固定IP（CIDR形式で指定する)
new_ansible_ssh_user | 必須 | 設定後にsshログインに利用するユーザ

`vars/users.yml.sample`をコピーします。
```
$ cp vars/users.yml.sample vars/users.yml
```

`users.yml`にユーザ情報を設定します。以下は設定例です。
```
users:
  foobar3000:
    password: p@ssw0rd
    groups: sudo
    shell: /bin/bash
    ssh_enable: true

  admin:
    password: p@ssw0rd
    shell: /bin/bash
    ssh_enable: false
```
項目 | 任意/必須 | 説明
---- | ---- | ----
password | 必須 | パスワード
groups | 任意 | グループ ユーザ名のグループは自動で生成されるため、ここに記述する必要はない
shell | 必須 | シェル
ssh_enable | 必須 | sshによるログオンを可能にするかどうか　（~/.ssh/authorized_keysに公開鍵を追加するかどうか。）

`ansible-vault`で`users.yml`を暗号化します。
```
ansible-vault encrypt vars/users.yml
```

実行します。
```
$ ansible-playbook cookpi.yml -i hosts.py
```

実行すると、Raspberry Piの設定が行われ後、自動的にRaspberry Piの再起動が実行され、接続確認が行われます。

# 作成者
foobar3000

# 参照情報
[RaspberryPi Raspbian ヘッドレスインストール](https://qiita.com/nori-dev-akg/items/a8361e728a66a8c3bdba)<BR>
[Raspberry Pi3のLAN外からのSSH接続設定方法](https://qiita.com/3no3_tw/items/4b5975a9f3087edf4e20)<BR>
[お前らのSSH Keysの作り方は間違っている](https://qiita.com/suthio/items/2760e4cff0e185fe2db9)<BR>
[ansible で対象サーバを再起動する](http://d.hatena.ne.jp/incarose86/20150215/1424017177)<BR>
