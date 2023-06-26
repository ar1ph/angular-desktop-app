import sys, json
data = sys.argv[1]
data = json.loads(data)
print(data)
def Combination(dir: str, model: str, strategy: str):
    return f"""Multiline response test:
                    {dir}
                    {model}
                    {strategy}"""
sys.stdout.flush()