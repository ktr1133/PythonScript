#!/usr/bin/env python
# coding: utf-8

#正規表現
import re
#処理測定
from tqdm import tqdm
import pandas as pd
#自然言語処理
import MeCab
import mojimoji

def text_to_words(text, stop_word_pass='D:/jupyter notebook/LocalCouncilWebscraping/stopwords/Japanese_textdivide.txt'):
    # stopword listをつくる
    stopword_list = []
    with open(stop_word_pass, 'r', encoding="utf-8") as f:
        stopword_list = f.readlines()

    stopword_list = [x.strip() for x in stopword_list if x.strip()]
    #形態素解析を始める
    m = MeCab.Tagger('-d "C:/Program Files/MeCab/dic/ipadic"')
    m.parse('')
    #text = normalize_text(text)
    text = mojimoji.zen_to_han(text, kana=False)
    m_text = m.parse(text)
    basic_words = []
    #mecabの出力結果を単語ごとにリスト化
    m_text = m_text.split('\n')
    for row in m_text:
        #Tab区切りで形態素、その品詞等の内容と分かれているので単語部のみ取得
        word = row.split("\t")[0]
        #最終行はEOS
        if word == 'EOS':
            break
        else:
            pos = row.split('\t')[1]
            slice_ = pos.split(',')
            #品詞を取得する
            parts = slice_[0]
            if parts == '記号':
                continue

            #活用しない語についてはそのままの語を取得する
            elif slice_[0] =='名詞' and word not in stopword_list:
                basic_words.append(word)

    #basic_words = ' '.join(basic_words)

    return basic_words


def divide_Qtex(self):
    """ﾃｷｽﾄを渡すと、質問の項目単位で全文を分割してﾘｽﾄで返す関数（項目単位の文末で区切り文字を挿入）"""
    se_terms = ['入ります', '終わります', '終わらせていただきます', 'してまいります', '入りたい']
    se_noun = ['質問']
    settou = ['それでは', 'さて', 'まず', 'そこで', 'しかしながら']
    q_start = ['そこで', 'このうち', 'これ', 'このこと', 'そのうち', 'このため', 'ただ、']
    q_noun = ['質問', '考え', '提案', '見解', '所見', '答弁']
    interrogative_word = ['どの', 'どれだけ', 'どういった', 'いかが', 'どのように', 'でしょうか。',
                          'どのような', 'どのくらい']
    q_verb = ['伺', 'でしょうか。', 'お聞かせください', '求めます。', '尋', '求め、', 'します。',
              'いるのか。', 'ですか。', 'いただきたい', '移ります。', '移らせていただきます。',
              'させていただきます。']
    order_terms = ['最初に', 'まず、', '初めに、', 'はじめに、', '次に', '続いて、', '続きまして、', '次いで',
                   '最後に', 'あわせて', '次の', '続き、',
                   '一つ目', '二つ目', '三つ目', '四つ目', '五つ目', '六つ目', '七つ目', '八つ目', '九つ目',
                   '一点目', '二点目', '三点目', '四点目', '五点目', '六点目', '七点目', '八点目', '九点目',
                   '一点', '二点', '三点', '四点', '五点', '六点', '七点', '八点', '九点',
                   '１点', '２点', '３点', '４点', '５点', '６点', '７点', '８点', '９点',
                   '１つ目', '２つ目', '３つ目', '４つ目', '５つ目', '６つ目', '７つ目', '８つ目', '９つ目',
                   '１点目', '２点目', '３点目', '４点目', '５点目', '６点目', '７点目', '８点目', '９点目',
                   '10点目', '11点目', '12点目', '13点目', '14点目', '15点目', '16点目', '17点目', '18点目',
                   '19点目'
                   '一、', '二、', '三、', '四、', '五、', '六、', '七、', '八、', '九、', '十、',
                   '(一)', '(二)', '(三)', '(四)', '(五)', '(六)', '(七)', '(八)', '(九)', '(十)',
                   '(1)', '(2)', '(3)', '(4)', '(5)', '(6)', '(7)', '(8)', '(9)', '(10)',
                   'ア、', 'イ、', 'ウ、', 'エ、', 'オ、', 'カ、', 'キ、', 'ク、', 'ケ、', 'コ、',
                   'サ、', 'シ、', 'ス、', 'セ、', 'ソ、',
                   '第一', '第二', '第三', '第四', '第五', '第六', '第七', '第八', '第九'
                   '第１', '第２', '第３', '第４', '第５', '第６', '第７', '第８', '第９', '第10'
                   '一項', '二項', '三項', '四項', '五項', '六項', '七項', '八項', '九項',
                   '１番目', '２番目', '３番目', '４番目', '５番目', '６番目', '７番目', '８番目', '９番目',
                   '10番目', '11番目', '12番目', '13番目', '14番目', '15番目',
                   '1、', '2、', '3、', '4、', '5、', '6、', '7、', '8、', '9、', '10、', '11、', '12、',
                   '13、', '14、', '15、',
                   '１、', '２、', '３、', '４、', '５、', '６、', '７、', '８、', '９、', '１０、']
    selected_adverb = ['について', 'としての']

    order_terms_0 = {1: '最初に', 2: 'まず、', 3: '初めに、', 4: 'はじめに、', 5: '次に', 6: '続いて、',
                     7: '続きまして、', 8: '次いで', 9: '続き、', 10: '次の', 11: 'あわせて', 12: '最後に'}
    order_terms_1 = {1: '一つ目', 2: '二つ目', 3: '三つ目', 4: '四つ目', 5: '五つ目', 6: '六つ目',
                     7: '七つ目', 8: '八つ目', 9: '九つ目'}
    order_terms_2 = {1: '一点', 2: '二点', 3: '三点', 4: '四点', 5: '五点', 6: '六点', 7: '七点', 8: '八点',
                     9: '九点', 10: '十点', 11: '十一点', 12: '十二点', 13: '十三点', 14: '十四点',
                     15: '十五点', 16: '十六点', 17: '十七点', 18: '十八点', 19: '十九点'}
    order_terms_3 = {1: '１点', 2: '２点', 3: '３点', 4: '４点', 5: '５点', 6: '６点', 7: '７点', 8: '８点',
                     9: '９点', 10: '10点', 11: '11点', 12: '12点', 13: '13点', 14: '14点', 15: '15点',
                     16: '16点', 17: '17点', 18: '18点', 19: '19点'}
    order_terms_4 = {1: '１つ目', 2: '２つ目', 3: '３つ目', 4: '４つ目', 5: '５つ目', 6: '６つ目', 7: '７つ目',
                     8: '８つ目', 9: '９つ目'}
    order_terms_5 = {1: '一、', 2: '二、', 3: '三、', 4: '四、', 5: '五、', 6: '六、', 7: '七、', 8: '八、',
                     9: '九、', 10: '十、'}
    order_terms_6 = {1: '(一)', 2: '(二)', 3: '(三)', 4: '(四)', 5: '(五)', 6: '(六)', 7: '(七)',
                     8: '(八)', 9: '(九)', 10: '(十)'}
    order_terms_7 = {1: '(1)', 2: '(2)', 3: '(3)', 4: '(4)', 5: '(5)', 6: '(6)', 7: '(7)', 8: '(8)',
                     9: '(9)', 10: '(10)'}
    order_terms_8 = {1: 'ア、', 2: 'イ、', 3: 'ウ、', 4: 'エ、', 5: 'オ、', 6: 'カ、', 7: 'キ、', 8: 'ク、',
                     9: 'ケ、', 10: 'コ、', 11: 'サ、', 12: 'シ、', 13: 'ス、', 14: 'セ、', 15: 'ソ、'}
    order_terms_9 = {1: '第一', 2: '第二', 3: '第三', 4: '第四', 5: '第五', 6: '第六', 7: '第七', 8: '第八',
                     9: '第九'}
    order_terms_10 = {1: '第１', 2: '第２', 3: '第３', 4: '第４', 5: '第５', 6: '第６', 7: '第７', 8: '第８',
                      9: '第９', 10: '第10', 11: '第11', 12: '第12', 13: '第13', 14: '第14', 15: '第15'}
    order_terms_11 = {1: '一項', 2: '二項', 3: '三項', 4: '四項', 5: '五項', 6: '六項', 7: '七項', 8: '八項',
                      9: '九項'}
    order_terms_12 = {1: '１番目', 2: '２番目', 3: '３番目', 4: '４番目', 5: '５番目', 6: '６番目', 7: '７番目',
                      8: '８番目', 9: '９番目', 10: '10番目', 11: '11番目', 12: '12番目', 13: '13番目',
                      14: '14番目', 15: '15番目'}
    order_terms_13 = {1: '1、', 2: '2、', 3: '3、', 4: '4、', 5: '5、', 6: '6、', 7: '7、', 8: '8、',
                      9: '9、', 10: '10、', 11: '11、', 12: '12、', 13: '13、', 14: '14、', 15: '15、'}
    order_terms_14 = {1: '１、', 2: '２、', 3: '３、', 4: '４、', 5: '５、', 6: '６、', 7: '７、', 8: '８、',
                      9: '９、', 10: '１０、'}

    verification = []
    hanbetsu = pd.DataFrame(index=[], columns=['Order', 'Sentence', 'newline_cate'])
    divisions = re.split('(?<=。)(?=.)', self)

    df_order = pd.DataFrame(index=[], columns=['o0', 'o1', 'o2', 'o3', 'o4', 'o5', 'o6', 'o7', 'o8',
                                               'o9', 'o10', 'o11', 'o12', 'o13', 'o14'])
    for i in range(len(divisions)):
        list0 = []
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        list5 = []
        list6 = []
        list7 = []
        list8 = []
        list9 = []
        list10 = []
        list11 = []
        list12 = []
        list13 = []
        list14 = []

        o0 = 0
        o0_1 = 0
        o0_2 = 0
        for a1, a2 in order_terms_0.items():
            if a2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o0_1 += 1
                        o0 = a1
                        temp0 = a2
                for c in q_verb:
                    if c in divisions[i]:
                        o0_2 += 1
                        o0 = a1
                        temp0 = a2

        if o0_1 > 0 or o0_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list0 = [o0, temp0, i]

        o1 = 0
        o1_1 = 0
        o1_2 = 0
        for b1, b2 in order_terms_1.items():
            if b2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o1_1 += 1
                        o1 = b1
                        temp1 = b2
                for c in q_verb:
                    if c in divisions[i]:
                        o1_2 += 1
                        o1 = b1
                        temp1 = b2

        if o1_1 > 0 or o1_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list1 = [o1, temp1, i]

        o2 = 0
        o2_1 = 0
        o2_2 = 0
        for c1, c2 in order_terms_2.items():
            if c2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o2_1 += 1
                        o2 = c1
                        temp2 = c2
                for c in q_verb:
                    if c in divisions[i]:
                        o2_2 += 1
                        o2 = c1
                        temp2 = c2

        if o2_1 > 0 or o2_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list2 = [o2, temp2, i]

        o3 = 0
        o3_1 = 0
        o3_2 = 0
        for d1, d2 in order_terms_3.items():
            if d2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o3_1 += 1
                        o3 = d1
                        temp3 = d2
                for c in q_verb:
                    if c in divisions[i]:
                        o3_2 += 1
                        o3 = d1
                        temp3 = d2

        if o3_1 > 0 or o3_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list3 = [o3, temp3, i]

        o4 = 0
        o4_1 = 0
        o4_2 = 0
        for e1, e2 in order_terms_4.items():
            if e2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o4_1 += 1
                        o4 = e1
                        temp4 = e2
                for c in q_verb:
                    if c in divisions[i]:
                        o4_2 += 1
                        o4 = e1
                        temp4 = e2

        if o4_1 > 0 or o4_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list4 = [o4, temp4, i]

        o5 = 0
        o5_1 = 0
        o5_2 = 0
        for f1, f2 in order_terms_5.items():
            if f2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o5_1 += 1
                        o5 = f1
                        temp5 = f2
                for c in q_verb:
                    if c in divisions[i]:
                        o5_2 += 1
                        o5 = f1
                        temp5 = f2

        if o5_1 > 0 or o5_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list5 = [o5, temp5, i]

        o6 = 0
        o6_1 = 0
        o6_2 = 0
        for g1, g2 in order_terms_6.items():
            if g2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o6_1 += 1
                        o6 = g1
                        temp6 = g2
                for c in q_verb:
                    if c in divisions[i]:
                        o6_2 += 1
                        o6 = g1
                        temp6 = g2

        if o6_1 > 0 or o6_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list6 = [o6, temp6, i]

        o7 = 0
        o7_1 = 0
        o7_2 = 0
        for h1, h2 in order_terms_7.items():
            if h2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o7_1 += 1
                        o7 = h1
                        temp7 = h2
                for c in q_verb:
                    if c in divisions[i]:
                        o7_2 += 1
                        o7 = h1
                        temp7 = h2

        if o7_1 > 0 or o7_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list7 = [o7, temp7, i]

        o8 = 0
        o8_1 = 0
        o8_2 = 0
        for ii1, ii2 in order_terms_8.items():
            if ii2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o8_1 += 1
                        o8 = ii1
                        temp8 = ii2
                for c in q_verb:
                    if c in divisions[i]:
                        o8_2 += 1
                        o8 = ii1
                        temp8 = ii2

        if o8_1 > 0 or o8_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list8 = [o8, temp8, i]

        o9 = 0
        o9_1 = 0
        o9_2 = 0
        for j1, j2 in order_terms_9.items():
            if j2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o9_1 += 1
                        o9 = j1
                        temp9 = j2
                for c in q_verb:
                    if c in divisions[i]:
                        o9_2 += 1
                        o9 = j1
                        temp9 = j2

        if o9_1 > 0 or o9_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list9 = [o9, temp9, i]

        o10 = 0
        o10_1 = 0
        o10_2 = 0
        for k1, k2 in order_terms_10.items():
            if k2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o10_1 += 1
                        o10 = k1
                        temp10 = k2
                for c in q_verb:
                    if c in divisions[i]:
                        o10_2 += 1
                        o10 = k1
                        temp10 = k2

        if o10_1 > 0 or o10_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list10 = [o10, temp10, i]

        o11 = 0
        o11_1 = 0
        o11_2 = 0
        for l1, l2 in order_terms_11.items():
            if l2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o11_1 += 1
                        o11 = l1
                        temp11 = l2
                for c in q_verb:
                    if c in divisions[i]:
                        o11_2 += 1
                        o11 = l1
                        temp11 = l2

        if o11_1 > 0 or o11_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list11 = [o11, temp11, i]

        o12 = 0
        o12_1 = 0
        o12_2 = 0
        for m1, m2 in order_terms_12.items():
            if m2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o12_1 += 1
                        o12 = m1
                        temp12 = m2
                for c in q_verb:
                    if c in divisions[i]:
                        o12_2 += 1
                        o12 = m1
                        temp12 = m2

        if o12_1 > 0 or o12_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list12 = [o12, temp12, i]

        o13 = 0
        o13_1 = 0
        o13_2 = 0
        for n1, n2 in order_terms_13.items():
            if n2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o13_1 += 1
                        o13 = n1
                        temp13 = n2
                for c in q_verb:
                    if c in divisions[i]:
                        o13_2 += 1
                        o13 = n1
                        temp13 = n2

        if o13_1 > 0 or o13_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list13 = [o13, temp13, i]

        o14 = 0
        o14_1 = 0
        o14_2 = 0
        for p1, p2 in order_terms_14.items():
            if p2 in divisions[i][:20]:
                for b in selected_adverb:
                    if b in divisions[i]:
                        o14_1 += 1
                        o14 = p1
                        temp14 = p2
                for c in q_verb:
                    if c in divisions[i]:
                        o14_2 += 1
                        o14 = p1
                        temp14 = p2

        if o14_1 > 0 or o14_2 > 0:
            v_check = 1
            for f in q_start:
                if f in divisions[i][:20]:
                    v_check += 1
            if v_check == 1:
                list14 = [o14, temp14, i]

        record = pd.Series([list0, list1, list2, list3, list4, list5, list6, list7, list8, list9,
                            list10, list11, list12, list13, list14], index=df_order.columns)
        df_order = df_order.append(record, ignore_index=True)

    list_columns = list(df_order.columns)

    df_compare = pd.DataFrame(index=[], columns=['order', 'order_term', 'div_num'])
    for ele in list_columns:
        exec_command0 ="df_compare_"+ele+" = pd.DataFrame(index=[], columns=['order', 'order_term', 'div_num'])"
        exec(exec_command0)
        for i in range(len(df_order)):
            if len(df_order[ele][i]) == 3:
                order = df_order[ele][i][0]
                order_term = df_order[ele][i][1]
                div_num = df_order[ele][i][2]
                record = pd.Series([order, order_term, div_num], index=df_compare.columns)
                exec_command1 = 'df_compare_'+ele+'='+'df_compare_'+ele+'.append(record, ignore_index=True)'
                exec(exec_command1)

    #場合分け用
    df_class = pd.DataFrame(index=[], columns=['order_cate', 'cla', 'orders', 'max_order'])
    for ele in list_columns:
        command_str = ""
        command_str += "if len(df_compare_"+ele+") <= 1:"+"\n"
        command_str += "    classification = 'no_cla'"+"\n"
        command_str += "    order_cate = ele"+"\n"
        command_str += "    orders = len(df_compare_"+ele+")"+"\n"
        command_str += "    max_order = 'invalid'"+"\n"
        command_str += "    record =  pd.Series([order_cate, classification, orders, max_order], index=df_class.columns)"+"\n"
        command_str += "    df_class = df_class.append(record, ignore_index=True)"+"\n"
        command_str += "else:"+"\n"
        command_str += "    if ele == 'o0':"+"\n"
        command_str += "        classification = 'mix'"+"\n"
        command_str += "        order_cate = ele"+"\n"
        command_str += "        orders = len(df_compare_"+ele+")"+"\n"
        command_str += "        max_order = 'invalid'"+"\n"
        command_str += "        record =  pd.Series([order_cate, classification, orders, max_order], index=df_class.columns)"+"\n"
        command_str += "        df_class = df_class.append(record, ignore_index=True)"+"\n"
        command_str += "    else:"+"\n"
        command_str += "        if list(df_compare_"+ele+".duplicated('order')).count(True) > 1:"+"\n"
        command_str += "            classification = 'repeat'"+"\n"
        command_str += "            order_cate = ele"+"\n"
        command_str += "            orders = len(df_compare_"+ele+")"+"\n"
        command_str += "            max_order = max(df_compare_"+ele+"['order'])"+"\n"
        command_str += "            record =  pd.Series([order_cate, classification, orders, max_order], index=df_class.columns)"+"\n"
        command_str += "            df_class = df_class.append(record, ignore_index=True)"+"\n"
        command_str += "        elif list(df_compare_"+ele+".duplicated('order')).count(True) <= 1:"+"\n"
        command_str += "            order_step = 0"+"\n"
        command_str += "            for i in range(len(df_compare_"+ele+")-1):"+"\n"
        command_str += "                if df_compare_"+ele+"['order'][i+1] - df_compare_"+ele+"['order'][i] == 1:"+"\n"
        command_str += "                    order_step += 1"+"\n"
        command_str += "            if (order_step>1) and (len(df_compare_"+ele+")>2):"+"\n"
        command_str += "                classification = 'consecutive'"+"\n"
        command_str += "                order_cate = ele"+"\n"
        command_str += "                orders = len(df_compare_"+ele+")"+"\n"
        command_str += "                max_order = max(df_compare_"+ele+"['order'])"+"\n"
        command_str += "                record =  pd.Series([order_cate, classification, orders, max_order], index=df_class.columns)"+"\n"
        command_str += "                df_class = df_class.append(record, ignore_index=True)"+"\n"
        command_str += "            else:"+"\n"
        command_str += "                classification = 'discontinuity'"+"\n"
        command_str += "                order_cate = ele"+"\n"
        command_str += "                orders = len(df_compare_"+ele+")"+"\n"
        command_str += "                max_order = max(df_compare_"+ele+"['order'])"+"\n"
        command_str += "                record =  pd.Series([order_cate, classification, orders, max_order], index=df_class.columns)"+"\n"
        command_str += "                df_class = df_class.append(record, ignore_index=True)"+"\n"
        exec(command_str)

    mix = 0
    repeat = 0
    consecutive = 0
    for i in list(df_class.query('cla != "no_cla"').index):
        if 'mix' == df_class['cla'][i]:
            mix += 1
        elif 'repeat' == df_class['cla'][i]:
            repeat += 1
        elif 'consecutive' == df_class['cla'][i]:
            consecutive += 1

    #入れ子構造ありの場合
    temp = []
    if (repeat >= 1) and ((mix == 1) or (consecutive >= 1)):
        temp.append(1)
        comparelist = []
        for ele1 in list_columns:
            command_str = 'df_compare_'+ele1+"_2 = pd.DataFrame(index=[], columns=['order', 'order_term', 'div_num'])"+'\n'
            command_str += "list_rec = list(set(df_compare_"+ele1+"['order']))"+'\n'
            command_str += 'for ele2 in list_rec:'+'\n'
            command_str += '    min_div_num = min(df_compare_'+ele1+'.query("order == @ele2")["div_num"])'+'\n'
            command_str += '    id_mindiv = df_compare_'+ele1+".query('order == @ele2 and div_num == @min_div_num').index"+"\n"
            command_str += "    df_compare_"+ele1+"_2 = df_compare_"+ele1+"_2.append(df_compare_"+ele1+".iloc[id_mindiv], ignore_index=True)"+"\n"
            command_str += "comparelist.append(df_compare_"+ele1+"_2)"
            exec(command_str)

        df_step = pd.DataFrame(index=[], columns=['order_step', 'step', 'order_term'])
        steplist = []
        for ele in list_columns:
            if ele == 'o0':
                command_str = ""
                command_str += "df_step_"+ele+" = pd.DataFrame(index=[], columns=['order_step', 'step', 'order_term'])"+"\n"
                command_str += 'for i in range(len(df_compare_'+ele+')-1):'+ '\n'
                command_str += '    order_step = df_compare_'+ele+"['order'][i+1] - df_compare_"+ele+"['order'][i]"+"\n"
                command_str += "    step = df_compare_"+ele+"['div_num'][i+1] - df_compare_"+ele+"['div_num'][i]"+"\n"
                command_str += "    order_term = [df_compare_"+ele+"['order_term'][i], df_compare_"+ele+"['order_term'][i]]"+"\n"
                command_str += '    record = pd.Series([order_step, step, order_term], index=df_step.columns)'+"\n"
                command_str += "    df_step_"+ele+ " = df_step_"+ele+".append(record, ignore_index=True)"+"\n"
                command_str += "steplist.append(df_step_"+ele+")"
                exec(command_str)
            else:
                command_str = ""
                command_str += "df_step_"+ele+" = pd.DataFrame(index=[], columns=['order_step', 'step', 'order_term'])"+"\n"
                command_str += 'for i in range(len(df_compare_'+ele+'_2)-1):'+ '\n'
                command_str += '    order_step = df_compare_'+ele+"_2['order'][i+1] - df_compare_"+ele+"_2['order'][i]"+"\n"
                command_str += "    step = df_compare_"+ele+"_2['div_num'][i+1] - df_compare_"+ele+"_2['div_num'][i]"+"\n"
                command_str += "    order_term = [df_compare_"+ele+"_2['order_term'][i], df_compare_"+ele+"_2['order_term'][i]]"+"\n"
                command_str += '    record = pd.Series([order_step, step, order_term], index=df_step.columns)'+"\n"
                command_str += "    df_step_"+ele+ " = df_step_"+ele+".append(record, ignore_index=True)"+"\n"
                command_str += "steplist.append(df_step_"+ele+")"
                exec(command_str)

        df_select = pd.DataFrame(index=[], columns=['order_cate', 'order_step_judge', 'step_min', 'cla'])
        for i in range(len(steplist)):
            if i == 0:
                if len(steplist[i]) > 0:
                    order_cate = 'o'+str(i)
                    order_step_judge ='T'
                    step_min = min(steplist[i]['step'])
                    cla = df_class['cla'][i]
                    record = pd.Series([order_cate, order_step_judge, step_min, cla], index=df_select.columns)
                    df_select = df_select.append(record, ignore_index=True)
                else:
                    order_cate = 'o'+str(i)
                    order_step_judge ='F'
                    step_min = 0
                    cla = df_class['cla'][i]
                    record = pd.Series([order_cate, order_step_judge, step_min, cla], index=df_select.columns)
                    df_select = df_select.append(record, ignore_index=True)
            else:
                if df_class['cla'][i] == 'consecutive':
                    order_cate = 'o'+str(i)
                    order_step_judge ='T'
                    step_min = min(steplist[i]['step'])
                    cla = df_class['cla'][i]
                    record = pd.Series([order_cate, order_step_judge, step_min, cla], index=df_select.columns)
                    df_select = df_select.append(record, ignore_index=True)
                else:
                    order_cate = 'o'+str(i)
                    order_step_judge ='F'
                    step_min = 0
                    cla = df_class['cla'][i]
                    record = pd.Series([order_cate, order_step_judge, step_min, cla], index=df_select.columns)
                    df_select = df_select.append(record, ignore_index=True)

        for i in range(len(df_select)):
            if df_select['order_cate'][i] == 'o0':
                if df_select['step_min'][i] == max(df_select['step_min']):
                    max_order = 0
            else:
                if df_select['cla'][i] == 'consecutive':
                    if df_select['step_min'][i] == max(df_select['step_min']):
                        max_order = i

        if max_order == 0:
            re_division = []
            for i in range(len(divisions)):
                num = 0
                for j in df_compare_o0['div_num']:
                    if j == i:
                        num = j
                if num > 0:
                    re_division.append('\n'+divisions[num])
                else:
                    re_division.append(divisions[i])

        else:
            re_division = []
            df_compare_uni = pd.DataFrame(index=[], columns=['order', 'order_term', 'div_num'])
            command_str = ""
            command_str += "df_compare_uni = df_compare_uni.append(df_compare_o0, ignore_index=True)"+"\n"
            command_str += "df_compare_uni = df_compare_uni.append(df_compare_o"+str(max_order)+"_2, ignore_index=True)"+"\n"
            exec(command_str)

            df_compare_uni = df_compare_uni.sort_values('div_num').reset_index(drop=True)
            for i in range(len(divisions)):
                num = 0
                for j in df_compare_uni['div_num']:
                    if j == i:
                        num = j
                if num > 0:
                    re_division.append('\n'+divisions[num])
                else:
                    re_division.append(divisions[i])

        re_uni = ''.join(re_division)
        re2_division = re_uni.split('\n')

        rere_division = []
        for ele in re2_division:
            if ele != "":
                rere_division.append(ele)

    #入れ子構造なし、かつ(複合)連番ありの場合
    elif ((repeat == 0) and (consecutive >= 1)) or ((repeat == 0) and (mix == 1)):
        temp.append(2)
        for ele1 in list_columns:
            command_str = ''
            command_str += 'df_compare_'+ele1+"_2 = pd.DataFrame(index=[], columns=['order', 'order_term', 'div_num'])"+'\n'
            command_str += "list_rec = list(set(df_compare_"+ele1+"['order']))"+'\n'
            command_str += 'for ele2 in list_rec:'+'\n'
            command_str += '    min_div_num = min(df_compare_'+ele1+'.query("order == @ele2")["div_num"])'+'\n'
            command_str += '    id_mindiv = df_compare_'+ele1+".query('order == @ele2 and div_num == @min_div_num').index"+"\n"
            command_str += "    df_compare_"+ele1+"_2 = df_compare_"+ele1+"_2.append(df_compare_"+ele1+".iloc[id_mindiv], ignore_index=True)"
            exec(command_str)

        df_order_uni = pd.DataFrame(index=[], columns=['order', 'order_term', 'div_num', 'order_cate'])
        sequential_order = 1
        for i in range(len(df_order)):
            check = 0
            for ele in list(df_order.columns):
                if len(df_order[ele][i]) == 3:
                    if ele == 'o0':
                        pass
                    else:
                        if sequential_order == df_order[ele][i][0]:
                            order = df_order[ele][i][0]
                            order_term = df_order[ele][i][1]
                            div_num = df_order[ele][i][2]
                            order_cate = ele
                            record = pd.Series([order, order_term, div_num, order_cate], index=df_order_uni.columns)
                            df_order_uni = df_order_uni.append(record, ignore_index=True)
                            sequential_order += 1
                            check += 1

            if (check == 0) and (len(df_order['o0'][i]) == 3):
                order = df_order['o0'][i][0]
                order_term = df_order['o0'][i][1]
                div_num = df_order['o0'][i][2]
                order_cate = 'o0'
                record = pd.Series([order, order_term, div_num, order_cate], index=df_order_uni.columns)
                df_order_uni = df_order_uni.append(record, ignore_index=True)
                sequential_order += 1

        df_step = pd.DataFrame(index=[], columns=['order_step', 'step', 'order_term'])
        steplist = []
        for ele in list_columns:
            if ele == 'o0':
                command_str = ""
                command_str += "df_step_"+ele+" = pd.DataFrame(index=[], columns=['order_step', 'step', 'order_term'])"+"\n"
                command_str += 'for i in range(len(df_compare_'+ele+')-1):'+ '\n'
                command_str += '    order_step = df_compare_'+ele+"['order'][i+1] - df_compare_"+ele+"['order'][i]"+"\n"
                command_str += "    step = df_compare_"+ele+"['div_num'][i+1] - df_compare_"+ele+"['div_num'][i]"+"\n"
                command_str += "    order_term = [df_compare_"+ele+"['order_term'][i], df_compare_"+ele+"['order_term'][i+1]]"+"\n"
                command_str += '    record = pd.Series([order_step, step, order_term], index=df_step.columns)'+"\n"
                command_str += "    df_step_"+ele+ " = df_step_"+ele+".append(record, ignore_index=True)"+"\n"
                command_str += "steplist.append(df_step_"+ele+")"
                exec(command_str)
            else:
                command_str = ""
                command_str += "df_step_"+ele+" = pd.DataFrame(index=[], columns=['order_step', 'step', 'order_term'])"+"\n"
                command_str += 'for i in range(len(df_compare_'+ele+'_2)-1):'+ '\n'
                command_str += '    order_step = df_compare_'+ele+"_2['order'][i+1] - df_compare_"+ele+"_2['order'][i]"+"\n"
                command_str += "    step = df_compare_"+ele+"_2['div_num'][i+1] - df_compare_"+ele+"_2['div_num'][i]"+"\n"
                command_str += "    order_term = [df_compare_"+ele+"_2['order_term'][i], df_compare_"+ele+"_2['order_term'][i+1]]"+"\n"
                command_str += '    record = pd.Series([order_step, step, order_term], index=df_step.columns)'+"\n"
                command_str += "    df_step_"+ele+ " = df_step_"+ele+".append(record, ignore_index=True)"+"\n"
                command_str += "steplist.append(df_step_"+ele+")"
                exec(command_str)

        df_select = pd.DataFrame(index=[], columns=['order_cate', 'order_step_judge', 'step_min', 'cla'])
        for i in range(len(steplist)):
            if i == 0:
                if len(steplist[i]) > 0:
                    order_cate = 'o'+str(i)
                    order_step_judge ='T'
                    step_min = min(steplist[i]['step'])
                    cla = df_class['cla'][i]
                    record = pd.Series([order_cate, order_step_judge, step_min, cla], index=df_select.columns)
                    df_select = df_select.append(record, ignore_index=True)
                else:
                    order_cate = 'o'+str(i)
                    order_step_judge ='F'
                    step_min = 0
                    cla = df_class['cla'][i]
                    record = pd.Series([order_cate, order_step_judge, step_min, cla], index=df_select.columns)
                    df_select = df_select.append(record, ignore_index=True)
            else:
                if df_class['cla'][i] == 'consecutive':
                    order_cate = 'o'+str(i)
                    order_step_judge ='T'
                    step_min = min(steplist[i]['step'])
                    cla = df_class['cla'][i]
                    record = pd.Series([order_cate, order_step_judge, step_min, cla], index=df_select.columns)
                    df_select = df_select.append(record, ignore_index=True)
                else:
                    order_cate = 'o'+str(i)
                    order_step_judge ='F'
                    step_min = 0
                    cla = df_class['cla'][i]
                    record = pd.Series([order_cate, order_step_judge, step_min, cla], index=df_select.columns)
                    df_select = df_select.append(record, ignore_index=True)

        if max(df_select['step_min']) == 0:
            max_order = 0
        else:
            for i in range(len(df_select)):
                if df_select['step_min'][i] == max(df_select['step_min']):
                    if df_select['step_min'][i] > 0:
                        max_order = i
                    else:
                        max_order = 0

        if max_order == 0:
            re_division = []
            for i in range(len(divisions)):
                num = 0
                for j in df_compare_o0['div_num']:
                    if j == i:
                        num = j
                if num > 0:
                    re_division.append('\n'+divisions[num])
                else:
                    re_division.append(divisions[i])

        else:
            for ele1 in list_columns:
                command_str = ''
                command_str += 'df_compare_'+ele1+"_2 = pd.DataFrame(index=[], columns=['order', 'order_term', 'div_num'])"+'\n'
                command_str += "list_rec = list(set(df_compare_"+ele1+"['order']))"+'\n'
                command_str += 'for ele2 in list_rec:'+'\n'
                command_str += '    min_div_num = min(df_compare_'+ele1+'.query("order == @ele2")["div_num"])'+'\n'
                command_str += '    id_mindiv = df_compare_'+ele1+".query('order == @ele2 and div_num == @min_div_num').index"+"\n"
                command_str += "    df_compare_"+ele1+"_2 = df_compare_"+ele1+"_2.append(df_compare_"+ele1+".iloc[id_mindiv], ignore_index=True)"+"\n"
                exec(command_str)

            re_division = []
            df_compare_uni = pd.DataFrame(index=[], columns=['order', 'order_term', 'div_num'])
            command_str = ""
            command_str += "df_compare_uni = df_compare_uni.append(df_compare_o0, ignore_index=True)"+"\n"
            command_str += "df_compare_uni = df_compare_uni.append(df_compare_o"+str(max_order)+"_2, ignore_index=True)"+"\n"
            exec(command_str)
            df_compare_uni = df_compare_uni.sort_values('div_num').reset_index(drop=True)
            for i in range(len(divisions)):
                num = 0
                for j in df_compare_uni['div_num']:
                    if j == i:
                        num = j
                if num > 0:
                    re_division.append('\n'+divisions[num])
                else:
                    re_division.append(divisions[i])

        re_uni = ''.join(re_division)
        re2_division = re_uni.split('\n')

        rere_division = []
        for ele in re2_division:
            if ele != "":
                rere_division.append(ele)

    #order_termsなしの場合
    else:
        temp.append(3)
        re_division = []
        for i in range(len(divisions)):
            if divisions[i] != '':
                #pa0
                num0 = 0
                for se_t in se_terms:
                    if se_t in divisions[i]:
                        for se_n in se_noun:
                            if se_n in divisions[i]:
                                num0 += 1
                                verification.append([i, 'pa0', se_t, se_n, divisions[i]])
                                break
                if num0 > 0:
                    record = pd.Series([i, divisions[i], 'p'], index=hanbetsu.columns)
                    hanbetsu = hanbetsu.append(record, ignore_index=True)
                else:
                    pass

                #pa1
                num1 = 0
                for a in q_noun:
                    if a in divisions[i]:
                        for b in q_verb:
                            if b in divisions[i] and 'します' not in divisions[i]:
                                    num1 += 1
                                    verification.append([i, 'pa1', a, b, divisions[i]])
                                    break
                if num1 > 0:
                    record = pd.Series([i, divisions[i], 'p'], index=hanbetsu.columns)
                    hanbetsu = hanbetsu.append(record, ignore_index=True)
                else:
                    pass

                #pa2
                num2 = 0
                num3 = 0
                for c in interrogative_word:
                    if c in divisions[i] and 'などの' not in divisions[i]:
                        for b in q_verb:
                            if b in divisions[i]:
                                    num2 += 1
                                    verification.append([i, 'pa2', c, b, divisions[i]])
                                    break
                        #pa3
                        for d in selected_adverb:
                            if d in divisions[i] and 'の' not in divisions[i]:
                                    num3 += 1
                                    verification.append([i, 'pa3', c, d, divisions[i]])
                                    break
                if num2 > 0:
                    record = pd.Series([i, divisions[i], 'p'], index=hanbetsu.columns)
                    hanbetsu = hanbetsu.append(record, ignore_index=True)
                elif num3 > 0:
                    record = pd.Series([i, divisions[i], 'p'], index=hanbetsu.columns)
                    hanbetsu = hanbetsu.append(record, ignore_index=True)
                else:
                    pass

                #pa4
                num4 = 0
                for d in selected_adverb:
                    if d in divisions[i] and '次' not in divisions[i]:
                        if d in divisions[i] and '最後' not in divisions[i]:
                            for b in q_verb:
                                if b in divisions[i] and 'します' not in divisions[i]:
                                        num4 += 1
                                        verification.append([i, 'pa4', d, b, divisions[i]])
                                        break
                if num4 > 0:
                    record = pd.Series([i, divisions[i], 'p'], index=hanbetsu.columns)
                    hanbetsu = hanbetsu.append(record, ignore_index=True)
                else:
                    pass

                #v1
                v1 = 0
                v2 = 0
                for e in order_terms:
                    if e in divisions[i]:
                        for d in selected_adverb:
                            if d in divisions[i]:
                                v1 += 1
                                verification.append([i, 'v1', e, d, divisions[i]])
                                break
                        #v2
                        for b in q_verb:
                            if b in divisions[i]:
                                v2 += 1
                                verification.append([i, 'v2', e, b, divisions[i]])
                                break
                if v1 > 0:
                    record = pd.Series([i, divisions[i], 'v'], index=hanbetsu.columns)
                    hanbetsu = hanbetsu.append(record, ignore_index=True)
                elif v2 > 0:
                    record = pd.Series([i, divisions[i], 'v'], index=hanbetsu.columns)
                    hanbetsu = hanbetsu.append(record, ignore_index=True)
                else:
                    pass

                if v1 > 0 or v2 > 0:
                    v_check = 1
                    for f in q_start:
                        if f in divisions[i]:
                            v_check += 1
                    if v_check == 1:
                        re_division.append('\n' + divisions[i])
                    else:
                        re_division.append(divisions[i])
                else:
                    if len(divisions[i]) > 30:
                        if i != 0:
                            if i != 1:
                                if i != 2:
                                    if i != 3:
                                        if (num0 > 1 and '\n' not in re_division[-1]) and\
                                        (num1 > 1 and '\n' not in re_division[-1]) and\
                                        (num2 > 1 and '\n' not in re_division[-1]) and\
                                        (num3 > 1 and '\n' not in re_division[-1]) and\
                                        (num4 > 1 and '\n' not in re_division[-1]):
                                            num_q = 1
                                            for qs in q_start:
                                                if qs in divisions[i+1]:
                                                    num_q += 1
                                            if num_q == 1:
                                                re_division.append(divisions[i] + '\n')
                                        else:
                                            if num0 > 1:
                                                re_division.append(divisions[i] + '\n')
                                            else:
                                                re_division.append(divisions[i])
                                    else:
                                        if num0 > 1:
                                            re_division.append(divisions[i] + '\n')
                                        else:
                                            re_division.append(divisions[i])
                                else:
                                    if num0 > 1:
                                        re_division.append(divisions[i] + '\n')
                                    else:
                                        re_division.append(divisions[i])
                            else:
                                if num0 > 1:
                                    re_division.append(divisions[i] + '\n')
                                else:
                                    re_division.append(divisions[i])
                        else:
                            if num0 > 1:
                                re_division.append(divisions[i] + '\n')
                            else:
                                re_division.append(divisions[i])
                    else:
                        if num0 > 1:
                            re_division.append(divisions[i] + '\n')
                        else:
                            re_division.append(divisions[i])

        re_uni = ''.join(re_division)
        re2_division = re_uni.split('\n')

        rere_division = []
        for ele in re2_division:
            if ele != "":
                rere_division.append(ele)

    re3_temp = {}
    df_rate = pd.DataFrame(index=[], columns=['div_num', 'div_length', 'judge', 'hitrate_next', 'hitrate_prev'])
    for i in range(len(rere_division)):
        if rere_division[i] != '':
            if len(rere_division[i]) > 50:
                re3_temp[i] = 0
                record = pd.Series([i, len(rere_division[i]), re3_temp[i], 0, 0], index=df_rate.columns)
                df_rate = df_rate.append(record, ignore_index=True)
            else:
                if i == 0:
                    words_self = text_to_words(rere_division[i])
                    words_nex = text_to_words(rere_division[i+1])

                    hit_n =0
                    for ele1 in words_self:
                        for ele2 in words_nex:
                            if ele2 == ele1:
                                hit_n += 1
                    try:
                        hitrate_n = hit_n/(len(words_self)*len(words_nex))
                    except ZeroDivisionError:
                        hitrate_n = 0

                    if hitrate_n > 0:
                        re3_temp[i] = 1
                    else:
                        re3_temp[i] = 0

                    record = pd.Series([i, len(rere_division[i]), re3_temp[i], hitrate_n, 0], index=df_rate.columns)
                    df_rate = df_rate.append(record, ignore_index=True)

                elif i == len(rere_division)-1:
                    words_self = text_to_words(rere_division[i])
                    words_prev = text_to_words(rere_division[i-1])

                    hit_p =0
                    for ele1 in words_self:
                        for ele2 in words_prev:
                            if ele2 == ele1:
                                hit_p += 1
                    try:
                        hitrate_p = hit_p/(len(words_self)*len(words_prev))
                    except ZeroDivisionError:
                        hitrate_p = 0

                    if hitrate_p > 0:
                        re3_temp[i] = -1
                    else:
                        re3_temp[i] = 0

                    record = pd.Series([i, len(rere_division[i]), re3_temp[i], 0, hitrate_p], index=df_rate.columns)
                    df_rate = df_rate.append(record, ignore_index=True)

                else:
                    words_self = text_to_words(rere_division[i])
                    words_prev = text_to_words(rere_division[i-1])
                    words_nex = text_to_words(rere_division[i+1])

                    hit_p =0
                    for ele1 in words_self:
                        for ele2 in words_prev:
                            if ele2 == ele1:
                                hit_p += 1
                    try:
                        hitrate_p = hit_p/(len(words_self)*len(words_prev))
                    except ZeroDivisionError:
                        hitrate_p = 0

                    hit_n =0
                    for ele1 in words_self:
                        for ele2 in words_nex:
                            if ele2 == ele1:
                                hit_n += 1
                    try:
                        hitrate_n = hit_n/(len(words_self)*len(words_nex))
                    except ZeroDivisionError:
                        hitrate_n = 0

                    if (hitrate_p > hitrate_n) and (hitrate_p > 0):
                        re3_temp[i] = -1
                    elif (hitrate_p < hitrate_n) and (hitrate_n > 0):
                        re3_temp[i] = 1
                    else:
                        re3_temp[i] = 0

                    record = pd.Series([i, len(rere_division[i]), re3_temp[i], hitrate_n, hitrate_p], index=df_rate.columns)
                    df_rate = df_rate.append(record, ignore_index=True)

    re3_division_temp = ''
    num_rere = 0
    for i in range(len(rere_division)):
        if i == 0:
            if re3_temp[i] == 1:
                re3_division_temp += rere_division[i]+rere_division[i+1]
                num_rere += 1
            else:
                re3_division_temp += rere_division[i]

        elif i == len(rere_division)-1:
            if num_rere == 0:
                if re3_temp[i] == -1:
                    re3_division_temp += rere_division[i]
                else:
                    re3_division_temp += '\n'+rere_division[i]
            else:
                num_rere -= 1
                pass
        else:
            if num_rere == 0:
                if re3_temp[i] == -1:
                    re3_division_temp += rere_division[i]
                elif re3_temp[i] == 1:
                    re3_division_temp += '\n'+rere_division[i]+rere_division[i+1]
                    num_rere += 1
                else:
                    re3_division_temp += '\n'+rere_division[i]
            else:
                num_rere -= 1
                pass

    re3_division = re3_division_temp.split('\n')

    return re3_division


def divide_Atex(self):
    """ﾃｷｽﾄを渡すと、回答の項目単位で全文を分割してﾘｽﾄで返す関数。（項目単位の文頭で区切り文字を挿入）"""
    a_verb = ['いたします', 'でございます', 'しています', 'です', 'であります', 'おります', 'でありますが、' , 'ございました。',
              'します。']
    a_verb2 = ['まいります', 'まいりたい', 'おります。', 'でございます。', '思います。']
    order_terms = ['最初に', 'まず、', '初めに', '次に', '続いて、', '続きまして、', '次いで', '最後に', 'あわせて、', '次は、',
                   '一つ目', '二つ目','三つ目','四つ目','五つ目', '六つ目', '七つ目', '八つ目', '九つ目',
                   '一点目','二点目', '三点目', '四点目','五点目', '六点目', '七点目', '八点目', '九点目', '十点目',
                   '一点', '二点', '三点', '四点','五点', '六点','七点', '八点', '九点', '十点',
                   '１点', '２点', '３点', '４点','５点', '６点', '７点', '８点', '９点', '１０点',
                   '１つ目', '２つ目', '３つ目', '４つ目','５つ目', '６つ目', '７つ目', '８つ目', '９つ目',
                   '１点目', '２点目', '３点目', '４点目','５点目', '６点目', '７点目', '８点目', '９点目', '１０点目',
                   '10点目', '11点目', '12点目', '13点目', '14点目', '15点目', '16点目', '17点目', '18点目', '19点目'
                   '一、', '二、', '三、', '四、', '五、','六、', '七、', '八、', '九、', '十、',
                   '(一)', '(二)', '(三)', '(四)', '(五)', '(六)','(七)', '(八)', '(九)', '(十)',
                   '１つ', '２つ', '３つ', '４つ', '５つ', '６つ', '７つ', '８つ', '９つ']
    selected_adverb = ['について', 'なんですが', 'につきましては']
    demonstrative = ['そこで', 'このうち', 'これ', 'このこと', 'そのうち', 'このため', 'ただ、', 'この', 'その']

    verification = []
    hanbetsu = pd.DataFrame(index=[], columns=['Order', 'Sentence', 'newline_cate'])

    divisions = re.split('(?<=。)', self)#「。」で区切り、単文に分割

    #内容別に文章を分割するパート
    re_division = []
    for i in range(len(divisions)):
        if divisions[i] != '':
            #v1
            v1 = 1
            v2 = 1
            temp_v1 = 0
            temp_v2 = 0
            for a in order_terms:
                if a in divisions[i][:20]:
                    for b in a_verb:
                        if b in divisions[i]:
                            for c in demonstrative:
                                if c in divisions[i][:10]:
                                    temp_v1 +=1
                            if temp_v1 == 0:
                                v1 += 1
                                verification.append([i, 'v1', a, b, divisions[i]])
                                break
                    #v2
                    for c in selected_adverb:
                        if c in divisions[i]:
                            for d in demonstrative:
                                if d in divisions[i][:10]:
                                    temp_v2 +=1
                            if temp_v2 == 0:
                                v2 += 1
                                verification.append([i, 'v2', a, c, divisions[i]])
                                break
            if v1 > 1:
                record = pd.Series([i, divisions[i], 'v'], index=hanbetsu.columns)
                hanbetsu = hanbetsu.append(record, ignore_index=True)
            elif v2 > 1:
                record = pd.Series([i, divisions[i], 'v'], index=hanbetsu.columns)
                hanbetsu = hanbetsu.append(record, ignore_index=True)
            else:
                pass

            v3 = 1
            temp_v3 = 0
            for a in selected_adverb:
                if a in divisions[i]:
                    for b in a_verb:
                        if b in divisions[i]:
                            for c in demonstrative:
                                if c in divisions[i][:10]:
                                    temp_v3 += 1
                            if temp_v3 == 0:
                                v3 += 1
                                verification.append([i, 'v3', a, b, divisions[i]])
                                break
            if v3 > 1:
                record = pd.Series([i, divisions[i], 'v'], index=hanbetsu.columns)
                hanbetsu = hanbetsu.append(record, ignore_index=True)
            else:
                pass

            v4 = 1
            temp_v4_1 = 0
            temp_v4 = 0
            for a in selected_adverb:
                if a in divisions[i]:
                    for b in a_verb2:
                        if b in divisions[i-1]:
                            temp_v4_1 += 1
                    if temp_v4_1 == 0:
                        for c in demonstrative:
                            if c in divisions[i][:10]:
                                temp_v4 += 1
                        if temp_v4 == 0:
                            v4 += 1
                            verification.append([i, 'v4', a, b, divisions[i]])
                            break
            if v4 > 1:
                record = pd.Series([i, divisions[i], 'v'], index=hanbetsu.columns)
                hanbetsu = hanbetsu.append(record, ignore_index=True)
            else:
                pass

            if v1 > 1 or v2 > 1 or v3 > 1 or v4 > 1:
                re_division.append('\n' + divisions[i])
            else:
                re_division.append(divisions[i])

    re_uni = ''.join(re_division)
    rere_division = re_uni.split('\n')

    re3_division = []
    num = 0
    for i in range(len(rere_division)):
        if rere_division[i] != '':
            if num == 0:
                num = 0
                if len(rere_division[i]) < 50:
                    order = 0
                    for a in order_terms:
                        if a in rere_division[i][:20]:
                            order += 1
                    if order > 0:
                        if len(rere_division) > i+1:
                            re3_division.append(rere_division[i]+rere_division[i+1])
                            num += 1
                        else:
                            re3_division.append(rere_division[i])
                            num += 1
                    else:
                        re3_division.append(rere_division[i])
                else:
                    re3_division.append(rere_division[i])
            else:
                num = 0
                pass

    df_words = pd.DataFrame(index=[], columns=['words', 'hitrate_pre', 'hitrate_nex'])
    if len(re3_division) > 2:
        for i in range(len(re3_division)):
            if i == 0:
                words_self = text_to_words(re3_division[i])
                words_nex = text_to_words(re3_division[i+1])

                hit_n =0
                for ele1 in words_self:
                    for ele2 in words_nex:
                        if ele2 == ele1:
                            hit_n += 1
                try:
                    hitrate_n = hit_n/(len(words_self)*len(words_nex))
                except ZeroDivisionError:
                    hitrate_n = 0
                record = pd.Series([words_self, '', hitrate_n], index=df_words.columns)
                df_words = df_words.append(record, ignore_index=True)

            elif i == len(re3_division)-1:
                words_self = text_to_words(re3_division[i])
                words_prev = text_to_words(re3_division[i-1])

                hit_p =0
                for ele1 in words_self:
                    for ele2 in words_prev:
                        if ele2 == ele1:
                            hit_p += 1
                try:
                    hitrate_p = hit_p/(len(words_self)*len(words_prev))
                except ZeroDivisionError:
                    hitrate_p = 0
                record = pd.Series([words_self, hitrate_p, ''], index=df_words.columns)
                df_words = df_words.append(record, ignore_index=True)

            else:
                words_self = text_to_words(re3_division[i])
                words_prev = text_to_words(re3_division[i-1])
                words_nex = text_to_words(re3_division[i+1])

                hit_p =0
                for ele1 in words_self:
                    for ele2 in words_prev:
                        if ele2 == ele1:
                            hit_p += 1
                try:
                    hitrate_p = hit_p/(len(words_self)*len(words_prev))
                except ZeroDivisionError:
                    hitrate_p = 0

                hit_n =0
                for ele1 in words_self:
                    for ele2 in words_nex:
                        if ele2 == ele1:
                            hit_n += 1
                try:
                    hitrate_n = hit_n/(len(words_self)*len(words_nex))
                except ZeroDivisionError:
                    hitrate_n = 0

                record = pd.Series([words_self, hitrate_p, hitrate_n], index=df_words.columns)
                df_words = df_words.append(record, ignore_index=True)
    else:
        for i in range(len(re3_division)):
            words_self = text_to_words(re3_division[i])
            record = pd.Series([words_self, 0, 0], index=df_words.columns)
            df_words = df_words.append(record, ignore_index=True)

    re4_temp = {}
    num_order = 0
    for i in range(len(re3_division)):
        num = 0
        for a in order_terms:
            if a in re3_division[i][:20]:
                num += 1
        if num == 0:
            re4_temp[i] = 'no_order'
        else:
            re4_temp[i] = 'order'
            num_order += 1

    if num_order/len(re3_division) > 0.3:
        re4_division = []
        num = 0
        for i in range(len(re3_division)):
            if num == 0:
                if i == len(re3_division)-1:
                    re4_division.append(re3_division[i])

                else:
                    j = 1
                    temp_text = []
                    if i+j < len(re3_division):
                        while (i+j < len(re3_division)) and\
                        (re4_temp[i+j] != 'order') and\
                        (df_words['hitrate_nex'][i+j-1] > 0.002):
                            temp_text.append(re3_division[i+j])
                            num += 1
                            j += 1

                        else:
                            if temp_text != []:
                                temp_text.insert(0, re3_division[i])
                                text = ''.join(temp_text)
                                re4_division.append(text)
                            else:
                                re4_division.append(re3_division[i])
                    else:
                        pass
            else:
                num -= 1
                pass
    else:
        re4_division = re3_division


    return re4_division
