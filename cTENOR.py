import argparse
import subprocess
import re, csv

def run_tools():
    # now developping!!!!!!!!!!!!!
    #deepTE = subprocess.run(['python3', 'DeepTE.py -d ./own_data/coelacanth -o ./own_data/coelacanth -i ./own_data/coelacanth/Lcha-families.fa -sp M -m_dir ./own_data/Ibetoge/download_M_model_dir/Metazoans_model/'], capture_output=True)
    return None

def labeling(itext):
    out = [['RMid', 'class', 'origin']]
    with open(itext) as f:
        flag = False
        for s_line in f:
            if not flag:
                if s_line[0] == '>':
                    id = re.findall('>(.+?)#', s_line)[0]
                    rm = re.findall('#(.+)__', s_line)[0]
                    print(">", id)

                    # RepeatModelerでUnknownの場合、DeepTEの結果を検索
                    if rm == 'Unknown':
                        dte = re.findall('__(.+?)\|', s_line)
                        dte = dte[0].split('_')

                        # DeepTEでもUnknownの場合、あるいは正確なドメインまでわからない場合はRFSBとTEclassの結果から導く
                        if dte[0] == 'unknown' or (len(dte) < 3 and not 'Helitron' in dte):
                            tec = re.findall('TEclass result: (.+)\|', s_line)[0]
                            flag = True

                        else: # DeepTEにアノテーションがついている場合
                            # データをRM形式に戻す
                            if 'Helitron' in dte:
                                odte = 'RC/Helitron'
                            elif 'SINE' in dte:
                                if len(dte) >= 4:
                                    odte = 'SINE/' + dte[3]
                                else:
                                    odte = 'SINE'
                            elif 'LINE' in dte:
                                if len(dte) >= 4:
                                    odte = 'LINE/' + dte[3]
                                else:
                                    odte = 'LINE'
                            else:
                                odte = dte[1] + '/' + dte[2]
                            out.append([id, odte, 'DeepTE'])
                            print('DeepTE: ', odte, '\n')
                        

                    else: # RepeatModelerでアノテーションがついている場合
                        out.append([id, rm, 'RepeatModeler'])
                        print('RepeatModeler: ', rm, '\n')

            else: # RFSBの読み込み
                flag = False
                rfsb = s_line.split(' ')[0].split(',')
                rfsb = [s.replace('DNATransposon', 'DNA').replace('Retrotransposon', 'Retro').replace('TIR', 'DNA').replace('Tc1-Mariner', 'TcMar') for s in rfsb]
                

                # Compare RFSB and TEclass
                if tec in rfsb:
                    if 'Helitron' in rfsb:
                        orfsb = 'RC/Helitron'
                    else:
                        if len(rfsb) >= 3:
                            orfsb = rfsb[1] + '/' + rfsb[0]
                        else:
                            orfsb = rfsb[-1]
                    out.append([id, orfsb, 'RFSB'])
                    print('RFSB and TEclass: ', orfsb,'\n')
                else:
                    out.append([id, 'Unknown', 'NA'])
                    print('unclear...ingnore the sequence', '\n')

    # 結果の出力
    with open('out_cTENOR.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(out)
    print(out)

    return None

if __name__ == '__main__':
    print("cTENOR version 0.1.0")

    parser = argparse.ArgumentParser()
    parser.add_argument("FASTA", help="library fasta file which is outputfile of RepeatModeler")
    parser.add_argument("-i", "--input", help="Result txt file of deepTE -> TEclass -> RFSB")
    args = parser.parse_args()

    if not args.input:
        run_tools()

    else:
        labeling(args.input)