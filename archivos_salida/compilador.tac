begin_func main
t1 = 10
x = t1
t2 = 3.14
y = t2
t3 = 5
z = t3
t4 = 5
t5 = x + t4
sum = t5
t6 = 1.5
t7 = y - t6
diff = t7
t8 = 2
t9 = x * t8
product = t9
t10 = 2.0
t11 = y / t10
quotient = t11
t12 = 5
t13 = x + t12
t14 = 2
t15 = t13 * t14
t16 = 1
t17 = 1
t18 = t16 + t17
t19 = t15 / t18
complex_expr = t19
t20 = 5
t21 = new_array 5
t22 = 1
t21[0] = t22
t23 = 2
t21[1] = t23
t24 = 3
t21[2] = t24
t25 = 4
t21[3] = t25
t26 = 5
t21[4] = t26
intArray = new_array t20
intArray = t21
t27 = 3
t28 = new_array 3
t29 = 1.1
t28[0] = t29
t30 = 2.2
t28[1] = t30
t31 = 3.3
t28[2] = t31
floatArray = new_array t27
floatArray = t28
t32 = 4
t33 = new_array 4
t34 = 10
t33[0] = t34
t35 = 20
t33[1] = t35
t36 = 30
t33[2] = t36
t37 = 40
t33[3] = t37
natArray = new_array t32
natArray = t33
t38 = 0
t39 = intArray[t38]
firstElement = t39
t40 = 1
t41 = 5.5
floatArray[t40] = t41
t42 = 2
t43 = 0
t44 = natArray[t43]
t45 = 1
t46 = natArray[t45]
t47 = t44 + t46
natArray[t42] = t47
t48 = 5
t49 = x > t48
ifz t49 goto L1
t50 = 42
inside_if = t50
t51 = x + inside_if
x = t51
goto L2
L1:
L2:
t52 = 0
counter = t52
L3:
t53 = 10
t54 = counter < t53
ifz t54 goto L4
t55 = 1
t56 = counter + t55
counter = t56
t57 = 5
t58 = counter == t57
ifz t58 goto L5
t59 = x + counter
x = t59
goto L6
L5:
L6:
goto L3
L4:
t60 = x <= y
ifz t60 goto L7
t61 = 2
t62 = x * t61
x = t62
goto L8
L7:
L8:
t63 = x != y
ifz t63 goto L9
t64 = 1.0
t65 = y + t64
y = t65
goto L10
L9:
L10:
t66 = 20
t67 = x == t66
ifz t67 goto L11
t68 = 30
x = t68
goto L12
L11:
L12:
t69 = x >= y
ifz t69 goto L13
t70 = 1
t71 = x - t70
x = t71
goto L14
L13:
L14:
t72 = 5
param t72
t73 = call factorial, 1
fact_result = t73
t74 = 5
param t74
t75 = call sumArray, 1
array_sum = t75
return array_sum
end_func

begin_func factorial
param n
t76 = 1
t77 = n <= t76
ifz t77 goto L15
t78 = 1
return t78
goto L16
L15:
L16:
t79 = 1
t80 = n - t79
param t80
t81 = call factorial, 1
t82 = n * t81
return t82
end_func

begin_func calculate
param a
param b
param c
t83 = a + b
temp = t83
t84 = temp * c
temp = t84
t85 = 2.0
t86 = temp / t85
return t86
end_func

begin_func sumArray
param size
t87 = 0
sum = t87
t88 = 0
i = t88
L17:
t89 = i < size
ifz t89 goto L18
t90 = intArray[i]
t91 = sum + t90
sum = t91
t92 = 1
t93 = i + t92
i = t93
goto L17
L18:
return sum
end_func

begin_func createAndFillArray
param size
param value
newArray = new_array size
t94 = 0
i = t94
L19:
t95 = i < size
ifz t95 goto L20
t96 = value * i
newArray[i] = t96
t97 = 1
t98 = i + t97
i = t98
goto L19
L20:
t99 = 1
t100 = size - t99
t101 = newArray[t100]
return t101
end_func

