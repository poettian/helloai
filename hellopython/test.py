a:list = [1, 2, 3, 4]

b = [x*2 if x % 2 == 0 else x for x in a]
print(b)