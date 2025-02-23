begin_func sqrt
param num
result = num
temp = 0
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

begin_func power
param base
param exp
t5 = exp == 0
ifz t5 goto L3
return 1
goto L4
L3:
L4:
result = 1
i = 0
L5:
t6 = i < exp
ifz t6 goto L6
t7 = result * base
result = t7
t8 = i + 1
i = t8
goto L5
L6:
return result
end_func

begin_func main
number = 16
param number
t9 = call sqrt, 1
root = t9
param root
param 2
t10 = call power, 2
powered = t10
end_func

