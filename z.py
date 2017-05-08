n = int(input())
a = list(input().split())
a = [int(x) for x in a]
maxx = max(a)
for d in range(n):
    for start in range(0,d):
        ind = start
        summ = 0
        while ind < n:
            summ += a[ind]
            maxx = max(maxx, summ)
            if summ < 0:
                summ = 0
            ind += d
print(maxx)
