def multiplication(s):
    const = 0.1
    mass=[ord(i) for i in s]
    hash=[]
    for i in range(len(mass)):
        hash.append(int(len(mass) * ((mass[i] * const) % 1)))
    return sum(hash)


k=input('Введите ключ ')
print(multiplication(k))
