import subprocess

def addslash(i: str):
    if i[-1] != '/':
        i = i + '/'
    return i

if __name__ == '__main__':
    print("cTENOR configure")
    print("Yuki Kimura 2022-2025, MIT licence")

    print('Enter FULL PATH of DeepTE directory:')
    path_deepTE = subprocess.run(['which', 'DeepTE.py'], stdout=subprocess.PIPE, text=True)
    if not path_deepTE.stdout:
        d_deepTE = ''
    else:
        d_deepTE = path_deepTE.stdout

    deepTE = str(input(d_deepTE) or d_deepTE)
    if deepTE == '':
        print('error')

    print('Enter FULL PATH of RFSB directory:')
    path_RFSB = subprocess.run(['which', 'transposon_classifier_RFSB'], stdout=subprocess.PIPE, text=True)
    if path_RFSB.stdout == '':
        d_RFSB = None
    else:
        d_RFSB = path_RFSB.stdout
    RFSB = input(d_RFSB + "Is this path OK?: [Enter] or [PATH]")
    
    if not RFSB:
        if d_RFSB:
            RFSB = d_RFSB
        else:
            print("ERROR")


    with open('cTENOR_configure', 'w') as f:
        print(deepTE, RFSB)
        f.write(addslash(deepTE) + '\n')
        f.write(addslash(RFSB))

    print('Settings Done!')
