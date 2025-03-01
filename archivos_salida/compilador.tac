begin_func main
t1 = 5
nums = new_array t1
t2 = 0
t3 = 10
nums[t2] = t3
t4 = 1
t5 = 20
nums[t4] = t5
t6 = 2
t7 = 30
nums[t6] = t7
t8 = 3
t9 = 40
nums[t8] = t9
t10 = 4
t11 = 50
nums[t10] = t11
t12 = 3
t13 = new_array 3
t14 = 10.5
t13[0] = t14
t15 = 20.75
t13[1] = t15
t16 = 30.99
t13[2] = t16
prices = new_array t12
prices = t13
t17 = 0
t18 = nums[t17]
t19 = 4
t20 = nums[t19]
t21 = t18 + t20
total = t21
t22 = 0
i = t22
L1:
t23 = 5
t24 = i < t23
ifz t24 goto L2
t25 = nums[i]
t26 = 2
t27 = t25 * t26
nums[i] = t27
t28 = 1
t29 = i + t28
i = t29
goto L1
L2:
t30 = 0
return t30
end_func

