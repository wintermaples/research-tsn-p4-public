# priority指定ができるiperf

以下からpriority指定ができるiperfをダウンロードする。
https://github.com/olerem/iperf/tree/so_priority

ダウンロードしたら展開し、以下のコマンドを実行することでインストールされる。
```
autoreconf -vfi
make clean; ./configure; make; make install
```

autoreconfは```automake libtool```ライブラリが必要。
