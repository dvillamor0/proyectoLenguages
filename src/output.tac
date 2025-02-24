begin_func main
num = 16.0
result = num
temp = 0.0
L1:
t1 = temp != result
ifz t1 goto L2
temp = result
t2 = num / result
t3 = t2 + result
t4 = t3 / 2
result = t4
goto L1
L2:
return result
end_func

