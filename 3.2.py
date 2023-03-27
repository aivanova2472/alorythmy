exh=[(180, 10),(100, 9),(80, 2),(40, 3),(65, 7),(170, 7)]
exh.sort()
exh.reverse()
print("экспонаты:",exh,"первое число-цена, второе-вес")
n=len(exh)
m=3
k=10
stolen=[]
stolen_print=[]
summ=0
while m>0:
    stole=False
    i=0
    k=10
    while True:
        if len(exh)==0:
            stole=True
            break
        if i<len(exh) and k-exh[i][1]>=0: #если можно украсть самое ценное, то берем
            k-=exh[i][1]
            summ+=exh[i][0]
            stolen_print.append(exh[i])
            stolen.append(exh[i])
            exh.remove(exh[i])
        elif i<len(exh)-1: #если самое ценное не помещается, то идем дальше
            i+=1
        else: #уже ничего не помещается, идем на следующий заход
            print(f"{4-m} заход: украдено -",stolen_print)
            stolen_print=[]
            m-=1
            break
    if stole:
        break
print("сумма украденного:",summ)
print("всего украдено:",len(stolen))
print("не удалось украсть:", exh)
