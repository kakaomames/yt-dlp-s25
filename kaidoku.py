# radar.py
def get_shindo(char):
    # コードの差分で震度を判定
    code = ord(char)
    if code <= 100: return 0
    return code - 100

with open('delta.txt', 'r') as f:
    data = f.read().strip()

# 震度1以上の地点をリストアップ
alerts = [(i, get_shindo(c)) for i, c in enumerate(data) if get_shindo(c) > 0]

if not alerts:
    print("日本全国、震度1以上なし。平和そのものだ！")
else:
    for loc, shindo in alerts:
        print(f"地点ID: {loc} で震度 {shindo} を観測中！")
