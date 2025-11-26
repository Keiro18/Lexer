@N = global i32 100
@isprime = global [100 x i1] zeroinitializer
declare void @print_int(i32)
declare void @print_float(float)
declare void @print_bool(i1)
declare void @print_char(i8)
define void @main() {
entry:
  %t0 = alloca i32
  %t1 = alloca i32
  store i32 0, i32* %t0
  br label %for.cond.0
for.cond.0:
  %t2 = load i32, i32* %t0
  %t3 = load i32, i32* @N
  %t4 = icmp slt i32 %t2, %t3
  br i1 %t4, label %for.body.1, label %for.end.3
for.body.1:
  %t5 = load i32, i32* %t0
  %t6 = getelementptr [100 x i1], [100 x i1]* @isprime, i32 0, i32 %t5
  store i1 1, i1* %t6
  br label %for.step.2
for.step.2:
  %t7 = load i32, i32* %t0
  %t8 = add i32 %t7, 1
  store i32 %t8, i32* %t0
  br label %for.cond.0
for.end.3:
  %t9 = getelementptr [100 x i1], [100 x i1]* @isprime, i32 0, i32 0
  store i1 0, i1* %t9
  %t10 = getelementptr [100 x i1], [100 x i1]* @isprime, i32 0, i32 1
  store i1 0, i1* %t10
  store i32 2, i32* %t0
  br label %while.cond.4
while.cond.4:
  %t11 = load i32, i32* %t0
  %t12 = load i32, i32* %t0
  %t13 = mul i32 %t11, %t12
  %t14 = load i32, i32* @N
  %t15 = icmp slt i32 %t13, %t14
  br i1 %t15, label %while.body.5, label %while.end.6
while.body.5:
  %t16 = load i32, i32* %t0
  %t17 = getelementptr [100 x i1], [100 x i1]* @isprime, i32 0, i32 %t16
  %t18 = load i1, i1* %t17
  br i1 %t18, label %if.then.7, label %if.end.8
while.end.6:
  call void @print_char(i8 80)
  call void @print_char(i8 114)
  call void @print_char(i8 105)
  call void @print_char(i8 109)
  call void @print_char(i8 111)
  call void @print_char(i8 115)
  call void @print_char(i8 32)
  call void @print_char(i8 109)
  call void @print_char(i8 101)
  call void @print_char(i8 110)
  call void @print_char(i8 111)
  call void @print_char(i8 114)
  call void @print_char(i8 101)
  call void @print_char(i8 115)
  call void @print_char(i8 32)
  call void @print_char(i8 113)
  call void @print_char(i8 117)
  call void @print_char(i8 101)
  call void @print_char(i8 32)
  call void @print_char(i8 49)
  call void @print_char(i8 48)
  call void @print_char(i8 48)
  call void @print_char(i8 58)
  store i32 2, i32* %t0
  br label %for.cond.12
if.then.7:
  %t19 = load i32, i32* %t0
  %t20 = load i32, i32* %t0
  %t21 = mul i32 %t19, %t20
  store i32 %t21, i32* %t1
  br label %while.cond.9
if.end.8:
  %t30 = load i32, i32* %t0
  %t31 = add i32 %t30, 1
  store i32 %t31, i32* %t0
  br label %while.cond.4
while.cond.9:
  %t22 = load i32, i32* %t1
  %t23 = load i32, i32* @N
  %t24 = icmp slt i32 %t22, %t23
  br i1 %t24, label %while.body.10, label %while.end.11
while.body.10:
  %t25 = load i32, i32* %t1
  %t26 = getelementptr [100 x i1], [100 x i1]* @isprime, i32 0, i32 %t25
  store i1 0, i1* %t26
  %t27 = load i32, i32* %t1
  %t28 = load i32, i32* %t0
  %t29 = add i32 %t27, %t28
  store i32 %t29, i32* %t1
  br label %while.cond.9
while.end.11:
  br label %if.end.8
for.cond.12:
  %t32 = load i32, i32* %t0
  %t33 = load i32, i32* @N
  %t34 = icmp slt i32 %t32, %t33
  br i1 %t34, label %for.body.13, label %for.end.15
for.body.13:
  %t35 = load i32, i32* %t0
  %t36 = getelementptr [100 x i1], [100 x i1]* @isprime, i32 0, i32 %t35
  %t37 = load i1, i1* %t36
  br i1 %t37, label %if.then.16, label %if.end.17
for.step.14:
  %t39 = load i32, i32* %t0
  %t40 = add i32 %t39, 1
  store i32 %t40, i32* %t0
  br label %for.cond.12
for.end.15:
  ret void
if.then.16:
  %t38 = load i32, i32* %t0
  call void @print_int(i32 %t38)
  call void @print_char(i8 32)
  call void @print_char(i8 124)
  call void @print_char(i8 32)
  br label %if.end.17
if.end.17:
  br label %for.step.14
}

