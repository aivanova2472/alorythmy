
N=int(input('cдача: '))
M1,S1= map(int, input('1.количество монет, номинал ').split())
M2,S2= map(int, input('2.количество монет, номинал ').split())
M3,S3= map(int, input('3.количество монет, номинал ').split())
M4,S4= map(int, input('4.количество монет, номинал ').split())

res=[[S1,M1],[S2,M2],[S3,M3],[S4,M4]]
res.sort(reverse=True)

ans=[]
if M1*S1+M2*S2+M3*S3+M4*S4<N:
    print('недостаточно монет')
else:
    for i in range(len(res)):
        while(N-res[i][0]>=0) and (res[i][1]!=0):
            N -= res[i][0]
            ans.append(res[i][0])
            res[i][1] -= 1
    print('комбинация монет:', *ans)


