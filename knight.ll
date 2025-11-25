@N = global i32 5
declare void @print_int(i32)
declare void @print_float(float)
declare void @print_bool(i1)
declare void @print_char(i8)
define i32 @index(i32 %r, i32 %c) {
entry:
  %t0 = alloca i32
  store i32 %r, i32* %t0
  %t1 = alloca i32
  store i32 %c, i32* %t1
  %t2 = load i32, i32* %t0
  %t3 = load i32, i32* @N
  %t4 = mul i32 %t2, %t3
  %t5 = load i32, i32* %t1
  %t6 = add i32 %t4, %t5
  ret i32 %t6
}
define void @print_board(i32* %board) {
entry:
  %t0 = alloca i32*
  store i32* %board, i32** %t0
  %t1 = alloca i32
  %t2 = alloca i32
  store i32 0, i32* %t1
  br label %for.cond.0
for.cond.0:
  %t3 = load i32, i32* %t1
  %t4 = load i32, i32* @N
  %t5 = icmp slt i32 %t3, %t4
  br i1 %t5, label %for.body.1, label %for.end.3
for.body.1:
  store i32 0, i32* %t2
  br label %for.cond.4
for.step.2:
  %t17 = load i32, i32* %t1
  %t18 = add i32 %t17, 1
  store i32 %t18, i32* %t1
  br label %for.cond.0
for.end.3:
  ret void
for.cond.4:
  %t6 = load i32, i32* %t2
  %t7 = load i32, i32* @N
  %t8 = icmp slt i32 %t6, %t7
  br i1 %t8, label %for.body.5, label %for.end.7
for.body.5:
  %t9 = load i32, i32* %t1
  %t10 = load i32, i32* %t2
  %t11 = call i32 @index(i32 %t9, i32 %t10)
  %t12 = load i32*, i32** %t0
  %t13 = getelementptr i32, i32* %t12, i32 %t11
  %t14 = load i32, i32* %t13
  call void @print_int(i32 %t14)
  call void @print_char(i8 32)
  br label %for.step.6
for.step.6:
  %t15 = load i32, i32* %t2
  %t16 = add i32 %t15, 1
  store i32 %t16, i32* %t2
  br label %for.cond.4
for.end.7:
  call void @print_char(i8 10)
  br label %for.step.2
}
define i1 @can_move(i32 %r, i32 %c, i32* %board) {
entry:
  %t0 = alloca i32
  store i32 %r, i32* %t0
  %t1 = alloca i32
  store i32 %c, i32* %t1
  %t2 = alloca i32*
  store i32* %board, i32** %t2
  %t3 = alloca i1
  %t4 = alloca i1
  %t5 = load i32, i32* %t0
  %t6 = icmp sge i32 %t5, 0
  %t7 = load i32, i32* %t0
  %t8 = load i32, i32* @N
  %t9 = icmp slt i32 %t7, %t8
  %t10 = and i1 %t6, %t9
  %t11 = load i32, i32* %t1
  %t12 = icmp sge i32 %t11, 0
  %t13 = and i1 %t10, %t12
  %t14 = load i32, i32* %t1
  %t15 = load i32, i32* @N
  %t16 = icmp slt i32 %t14, %t15
  %t17 = and i1 %t13, %t16
  store i1 %t17, i1* %t3
  %t18 = load i1, i1* %t3
  br i1 %t18, label %if.then.0, label %if.end.1
if.then.0:
  %t19 = load i32, i32* %t0
  %t20 = load i32, i32* %t1
  %t21 = call i32 @index(i32 %t19, i32 %t20)
  %t22 = load i32*, i32** %t2
  %t23 = getelementptr i32, i32* %t22, i32 %t21
  %t24 = load i32, i32* %t23
  %t25 = icmp eq i32 %t24, 0
  store i1 %t25, i1* %t4
  %t26 = load i1, i1* %t4
  ret i1 %t26
if.end.1:
  ret i1 0
}
define i1 @walk(i32 %r, i32 %c, i32 %m, i32* %board, i32* %xmoves, i32* %ymoves) {
entry:
  %t0 = alloca i32
  store i32 %r, i32* %t0
  %t1 = alloca i32
  store i32 %c, i32* %t1
  %t2 = alloca i32
  store i32 %m, i32* %t2
  %t3 = alloca i32*
  store i32* %board, i32** %t3
  %t4 = alloca i32*
  store i32* %xmoves, i32** %t4
  %t5 = alloca i32*
  store i32* %ymoves, i32** %t5
  %t6 = alloca i32
  %t7 = alloca i32
  %t8 = alloca i32
  %t9 = load i32, i32* %t2
  %t10 = load i32, i32* @N
  %t11 = load i32, i32* @N
  %t12 = mul i32 %t10, %t11
  %t13 = icmp eq i32 %t9, %t12
  br i1 %t13, label %if.then.0, label %if.end.1
if.then.0:
  %t14 = load i32*, i32** %t3
  call void @print_board(i32* %t14)
  ret i1 1
if.end.1:
  store i32 0, i32* %t6
  br label %for.cond.2
for.cond.2:
  %t15 = load i32, i32* %t6
  %t16 = icmp slt i32 %t15, 8
  br i1 %t16, label %for.body.3, label %for.end.5
for.body.3:
  %t17 = load i32, i32* %t0
  %t18 = load i32, i32* %t6
  %t19 = load i32*, i32** %t4
  %t20 = getelementptr i32, i32* %t19, i32 %t18
  %t21 = load i32, i32* %t20
  %t22 = add i32 %t17, %t21
  store i32 %t22, i32* %t7
  %t23 = load i32, i32* %t1
  %t24 = load i32, i32* %t6
  %t25 = load i32*, i32** %t5
  %t26 = getelementptr i32, i32* %t25, i32 %t24
  %t27 = load i32, i32* %t26
  %t28 = add i32 %t23, %t27
  store i32 %t28, i32* %t8
  %t29 = load i32, i32* %t7
  %t30 = load i32, i32* %t8
  %t31 = load i32*, i32** %t3
  %t32 = call i1 @can_move(i32 %t29, i32 %t30, i32* %t31)
  br i1 %t32, label %if.then.6, label %if.end.7
for.step.4:
  %t52 = load i32, i32* %t6
  %t53 = add i32 %t52, 1
  store i32 %t53, i32* %t6
  br label %for.cond.2
for.end.5:
  ret i1 0
if.then.6:
  %t33 = load i32, i32* %t7
  %t34 = load i32, i32* %t8
  %t35 = call i32 @index(i32 %t33, i32 %t34)
  %t36 = load i32*, i32** %t3
  %t37 = getelementptr i32, i32* %t36, i32 %t35
  %t38 = load i32, i32* %t2
  store i32 %t38, i32* %t37
  %t39 = load i32, i32* %t7
  %t40 = load i32, i32* %t8
  %t41 = load i32, i32* %t2
  %t42 = add i32 %t41, 1
  %t43 = load i32*, i32** %t3
  %t44 = load i32*, i32** %t4
  %t45 = load i32*, i32** %t5
  %t46 = call i1 @walk(i32 %t39, i32 %t40, i32 %t42, i32* %t43, i32* %t44, i32* %t45)
  br i1 %t46, label %if.then.8, label %if.end.9
if.end.7:
  br label %for.step.4
if.then.8:
  ret i1 1
if.end.9:
  %t47 = load i32, i32* %t7
  %t48 = load i32, i32* %t8
  %t49 = call i32 @index(i32 %t47, i32 %t48)
  %t50 = load i32*, i32** %t3
  %t51 = getelementptr i32, i32* %t50, i32 %t49
  store i32 0, i32* %t51
  br label %if.end.7
}
define i32 @main() {
entry:
  %t0 = alloca [25 x i32]
  %t1 = alloca [8 x i32]
  %t2 = getelementptr [8 x i32], [8 x i32]* %t1, i32 0, i32 0
  store i32 2, i32* %t2
  %t3 = getelementptr [8 x i32], [8 x i32]* %t1, i32 0, i32 1
  store i32 1, i32* %t3
  %t4 = getelementptr [8 x i32], [8 x i32]* %t1, i32 0, i32 2
  %t5 = sub i32 0, 1
  store i32 %t5, i32* %t4
  %t6 = getelementptr [8 x i32], [8 x i32]* %t1, i32 0, i32 3
  %t7 = sub i32 0, 2
  store i32 %t7, i32* %t6
  %t8 = getelementptr [8 x i32], [8 x i32]* %t1, i32 0, i32 4
  %t9 = sub i32 0, 2
  store i32 %t9, i32* %t8
  %t10 = getelementptr [8 x i32], [8 x i32]* %t1, i32 0, i32 5
  %t11 = sub i32 0, 1
  store i32 %t11, i32* %t10
  %t12 = getelementptr [8 x i32], [8 x i32]* %t1, i32 0, i32 6
  store i32 1, i32* %t12
  %t13 = getelementptr [8 x i32], [8 x i32]* %t1, i32 0, i32 7
  store i32 2, i32* %t13
  %t14 = alloca [8 x i32]
  %t15 = getelementptr [8 x i32], [8 x i32]* %t14, i32 0, i32 0
  store i32 1, i32* %t15
  %t16 = getelementptr [8 x i32], [8 x i32]* %t14, i32 0, i32 1
  store i32 2, i32* %t16
  %t17 = getelementptr [8 x i32], [8 x i32]* %t14, i32 0, i32 2
  store i32 2, i32* %t17
  %t18 = getelementptr [8 x i32], [8 x i32]* %t14, i32 0, i32 3
  store i32 1, i32* %t18
  %t19 = getelementptr [8 x i32], [8 x i32]* %t14, i32 0, i32 4
  %t20 = sub i32 0, 1
  store i32 %t20, i32* %t19
  %t21 = getelementptr [8 x i32], [8 x i32]* %t14, i32 0, i32 5
  %t22 = sub i32 0, 2
  store i32 %t22, i32* %t21
  %t23 = getelementptr [8 x i32], [8 x i32]* %t14, i32 0, i32 6
  %t24 = sub i32 0, 2
  store i32 %t24, i32* %t23
  %t25 = getelementptr [8 x i32], [8 x i32]* %t14, i32 0, i32 7
  %t26 = sub i32 0, 1
  store i32 %t26, i32* %t25
  %t27 = call i32 @index(i32 0, i32 0)
  %t28 = getelementptr [25 x i32], [25 x i32]* %t0, i32 0, i32 %t27
  store i32 1, i32* %t28
  %t29 = getelementptr [25 x i32], [25 x i32]* %t0, i32 0, i32 0
  %t30 = getelementptr [8 x i32], [8 x i32]* %t1, i32 0, i32 0
  %t31 = getelementptr [8 x i32], [8 x i32]* %t14, i32 0, i32 0
  %t32 = call i1 @walk(i32 0, i32 0, i32 2, i32* %t29, i32* %t30, i32* %t31)
  br i1 %t32, label %if.then.0, label %if.else.1
if.then.0:
  call void @print_char(i8 83)
  call void @print_char(i8 111)
  call void @print_char(i8 108)
  call void @print_char(i8 117)
  call void @print_char(i8 99)
  call void @print_char(i8 105)
  call void @print_char(i8 111)
  call void @print_char(i8 110)
  call void @print_char(i8 32)
  call void @print_char(i8 101)
  call void @print_char(i8 110)
  call void @print_char(i8 99)
  call void @print_char(i8 111)
  call void @print_char(i8 110)
  call void @print_char(i8 116)
  call void @print_char(i8 114)
  call void @print_char(i8 97)
  call void @print_char(i8 100)
  call void @print_char(i8 97)
  call void @print_char(i8 33)
  call void @print_char(i8 10)
  br label %if.end.2
if.else.1:
  call void @print_char(i8 78)
  call void @print_char(i8 111)
  call void @print_char(i8 32)
  call void @print_char(i8 101)
  call void @print_char(i8 120)
  call void @print_char(i8 105)
  call void @print_char(i8 115)
  call void @print_char(i8 116)
  call void @print_char(i8 101)
  call void @print_char(i8 32)
  call void @print_char(i8 115)
  call void @print_char(i8 111)
  call void @print_char(i8 108)
  call void @print_char(i8 117)
  call void @print_char(i8 99)
  call void @print_char(i8 105)
  call void @print_char(i8 111)
  call void @print_char(i8 110)
  call void @print_char(i8 10)
  br label %if.end.2
if.end.2:
  ret i32 0
}

