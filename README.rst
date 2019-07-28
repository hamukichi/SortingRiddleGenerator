===============
SortRiddleMaker
===============

概要
====

ソートなぞなぞを出題する Python 製のツールです．

使い方
======

Python 3.x を導入し，コンソールで `sortridgen.py` を実行してください．
既定では，基本的な英単語を用いたソートなぞなぞが出題されます．
詳細は，`sortridgen.py --help` を参照してください．
（ドキュメントは現在作成中です．）

同梱の辞書について
================

ファイル `dictionaries/english/ejdict_level*_words.csv` は，
パブリックドメインの英和辞書 ejdic-hand https://kujirahand.com/web-tools/EJDictFreeDL.php から
英単語とそれを整列したものを抽出したものです．
既定では特に利用頻度の高い語を集めた `ejdict_level2_words.csv` が出題に使用されますが，
利用頻度の下がる `ejdict_level1_words.csv` や `ejdict_level0_words.csv` を使用するようにも設定できます．
例： `python3 sortridgen.py --maindic ejdict_level0_words.csv`