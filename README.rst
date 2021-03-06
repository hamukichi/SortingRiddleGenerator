===================================================
SortingRiddleGenerator: ソートなぞなぞの出題
===================================================

概要
====

英語や日本語などの単語を構成する文字を昇順に整列したものを与え，もとの単語を復元させる言葉遊びを，ソートなぞなぞと呼びます．
この Python 製 CUI ツールは，ソートなぞなぞを自動で出題し，答え合わせも行うものです．

機能
====

* ソートなぞなぞを自動的に出題する
* 答え合わせ，別解の提示，成績の集計も行う
* プリセット機能により，使用する単語リストを容易に切り替えられる
* マージなぞなぞにも対応

導入
====

あらかじめ，Python 3.x を導入してください．作者は Windows 10 上の Python 3.7.0 で動作確認をしました．
当リポジトリ内のファイル，ディレクトリを適当な場所に配置してください．
コンソールで ``python sortridgen.py --help`` を実行し，
コマンドライン引数の入力方法の説明が表示されれば，導入はできています．

基本的な使い方
==============

``python sortridgen.py contest`` を実行すると，基本的な英単語を用いたソートなぞなぞの出題が始まります．
なお，後述のように，プリセット機能を用いて，出題範囲の単語を，難しめの英単語や，日本語の単語に設定できます．
単語を構成する文字を昇順に整列したものが表示されるので，もとの単語を入力してください．
正答が入力されると，存在するならば別解が表示されるとともに，次の問題に進みます．

解答の代わりに，次のコマンドを入力することもできます．

* ``HINT [文字数]``: 答えの単語の先頭から順に，指定された数の文字をヒントとして出力します．
  文字数は正の整数です．その後，再度解答かコマンドの入力を求められます．
* ``GIVEUP``: この問題を諦めて，次の問題に進みます．その際に，想定された正答が表示されます．
* ``EXIT``: 出題を終了します．成績の集計が表示され，プログラムが終了します．

コマンド ``EXIT`` が入力されない限り，エンドレスで出題が続きます．

進んだ使い方
=============

以下のように，``--option`` の形をしたオプションを指定してプログラムを実行することにより，
出題範囲や問題数といった設定を変えることができます．
特に記述のない限り，これらのオプションは併用可能です．

出題する問題数を指定する
------------------------

``python sortridgen.py contest --num [問題数]`` を実行すると，指定した問題数だけ，連続して出題します．
なお，問題数が 0 以下の整数の場合，上記と同様にエンドレスでの出題が続きます．

辞書プリセットを切り替える
--------------------------

当プログラムが使用する単語リストとその組み合わせは，次の二種類のファイルで規定されます．

* ソートなぞなぞ用辞書：``dictionaries/`` 以下に格納される CSV ファイルです．
  元の単語を示す ``orig_word`` 列と，それを整列したものを示す ``sorted_word`` 列からなります．
* 辞書プリセット：``presets/`` 以下に格納される JSON ファイルです．次を規定します．

  * 主辞書：出題と別解の探索に使われるソートなぞなぞ用辞書です．
    JSON ファイルの ``maindicts`` にパスを列挙して指定します．
  * 副辞書：別解の探索のみに使われるソートなぞなぞ用辞書です．
    JSON ファイルの ``subdicts`` にパスを列挙して指定します．
  * 出題する単語の長さの上限と下限：JSON ファイルの
    ``maxwordlen`` と ``minwordlen`` でそれぞれ指定します．

``python sortridgen.py contest --preset [プリセット名]`` を実行すると，
指定した名前の辞書プリセットを用いて，出題が始まります．
プリセット名は，辞書プリセットのファイル名 ``*.json`` です．
使用できるプリセットの例は後述の通りです．

たとえば，``python sortridgen.py contest --preset ejdic-hand-medium.json`` を実行すると，
やや難しめの英単語を出題範囲とすることができます．

マージなぞなぞ
--------------

複数の単語を連結後に整列し，そこから元の単語たちを復元する言葉遊びをマージなぞなぞと呼びます．
``python sortridgen.py contest --merge [単語数]`` と入力すると，
ソートなぞなぞの代わりにマージなぞなぞで遊べます．
使えるコマンドはソートなぞなぞと同様です．
答えは，単語を「，」「、」「,」のいずれかで区切って入力してください．例えば， 二単語であれば ``word1,word2`` の形式です．

使用できるソートなぞなぞ用辞書と辞書プリセットの例
========================================================

当プログラムで使用できるソートなぞなぞ用辞書と辞書プリセットの例は以下の通りです．

同梱しているもの
------------------------

配布物の中には，以下の辞書プリセットと，それが要求するソートなぞなぞ用辞書が含まれます．

ejdic-hand 系プリセット
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

パブリックドメインの英和辞典 `ejdic-hand <https://kujirahand.com/web-tools/EJDictFreeDL.php>`_ から，
英小文字のみからなる英単語とそれを整列したものを抜き出して作ったソートなぞなぞ用辞書です．
このソートなぞなぞ用辞書は ``dictionaries/english/`` 内にあり，単語の利用頻度の高いものから，
``ejdic-hand_level2.csv`` （650 語）， ``ejdic-hand_level1.csv`` （1434 語），
``ejdic-hand_level0.csv``  （32944 語）となっています．
これらのソートなぞなぞ用辞書を用いたプリセットは以下の通りです．

* ``ejdic-hand-easy.json``: ``ejdic-hand-level2`` を主辞書に，残りの二つを副辞書に用います．
  既定のプリセット ``default.json`` と，同一の辞書たちを用います．
* ``ejdic-hand-medium.json``: ``ejdic-hand-level1`` を主辞書に，残りの二つを副辞書に用います．
* ``ejdic-hand-hard.json``: ``ejdic-hand-level0`` を主辞書に，残りの二つを副辞書に用います．

NAIST Japanese Dictionary 系プリセット
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

日本語辞書 `NAIST Japanese Dictionary <https://ja.osdn.net/projects/naist-jdic/>`_ から，
読みが仮名のみからなる日本語の普通名詞とそれを整列したものを抜き出して作ったソートなぞなぞ用辞書です．
このソートなぞなぞ用辞書は ``dictionaries/japanese/naist-jdic-common-nouns.csv``
として同梱されています（のべ約 8 万語）．
これを用いたプリセットとして，``naist-jdic.json`` を同梱しています．

なお，和語や外来語といった種別によらず，単語はすべてカタカナで表記されていることに注意してください．

自作する
---------------------

上記のファイルに倣って，ソートなぞなぞ用辞書（CSV ファイル）と辞書プリセット（JSON ファイル）を自作することもできます．
詳細な説明は現在作成中です．

sort_nazonazo 用辞書との相互変換
---------------------------------

`sort_nazonazo <https://github.com/1119-2916/sort_nazonazo>`_ で用いられる DIC 形式の辞書と，
ソートなぞなぞ用辞書（CSV 形式）を相互変換することができます．
詳細な説明は ``python sortridgen.py convert -h`` （CSV 形式へ変換）および
``python sortridgen.py invconv -h`` （DIC 形式へ変換）を確認してください．

なお，配布物の ``foreign-format-dictionaries`` ディレクトリには，この方法で作成した
DIC 形式の辞書が格納されています．

ライセンスおよび著作権情報
================================

当プログラムには 3 条項 BSD ライセンスを適用します．詳細については LICENSE ファイルを参照してください．

また，当プログラムに同梱した，外部のライブラリ，データ等のライセンスおよび著作権情報は次の通りです．

NAIST Japanese Dictionary
-------------------------

同梱している ``naist-jdic-common-nouns.csv`` および
``naist-jdic-common-nouns.dic`` は， `NAIST Japanese Dictionary <https://ja.osdn.net/projects/naist-jdic/>`_ の
``mecab-naist-jdic`` より抽出したものです．NAIST Japanese Dictionary は以下の通り，3 条項 BSD ライセンスで提供されています::

    Copyright (c) 2009, Nara Institute of Science and Technology, Japan.

    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

    Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
    Neither the name of the Nara Institute of Science and Technology
    (NAIST) nor the names of its contributors may be used to endorse or
    promote products derived from this software without specific prior
    written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
    CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
    PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
    LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


更新履歴
===============

* Version 0.3.0 (2019-08-12)

  * マージなぞなぞに対応．
  * ソートなぞなぞ辞書と `sort_nazonazo <https://github.com/1119-2916/sort_nazonazo>`_ の辞書（DIC 形式）との相互変換機能を追加．

* Version 0.2.0 (2019-08-04)

  * NAIST Japanese Dictionary 由来の日本語ソートなぞなぞ辞書および辞書プリセットを追加．
  * 外部の辞書データをソートなぞなぞ辞書に変換する機能を追加．現状では NAIST Japanese Dictionary のみに対応．
  * ライセンスを 3 条項 BSD ライセンスに変更．

* Version 0.1.0 (2019-08-03)

  * 全面的リファクタリング．
  * 出す問題数を指定する機能を追加．
  * ロギング機能を追加．
  * コマンドライン引数を修正．
  * 辞書プリセットにて，使用する単語の文字数の上限，下限を設定可能に変更．
  * ソートなぞなぞ用辞書および辞書プリセットを指定する際に，拡張子の省略を認めないように変更．
  * 同梱の辞書プリセット名を変更．
  * その他，雑多な修正．

* Version 0.0.1 (2019-07-29): 初版．

関連するプロジェクト
=================================

sort_nazonazo
-------------

ソートなぞなぞおよびマージなぞなぞを考案した `Ti11192916 <https://github.com/1119-2916>`_ さんは，
`sort_nazonazo <https://github.com/1119-2916/sort_nazonazo>`_ を作成されました．これは，
ソートなぞなぞの出題，答え合わせを Discord 上で行える Bot です．
SortingRiddleGenerator は，ここから着想を得て，
手元の端末でもソートなぞなぞの練習ができるように作成したものです．
