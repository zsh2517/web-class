import sys
if len(sys.argv) <= 1:
    print("")
    exit(0)
s = str(sys.argv[1])
print(s.replace("你","我").replace("吗","").replace("？","！"))