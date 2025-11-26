@N = global i32 10
@f = global [10 x i32] zeroinitializer
declare void @print_int(i32)
declare void @print_float(float)
declare void @print_bool(i1)
declare void @print_char(i8)
define void @main() {
entry:
  %t0 = alloca i32
  %t1 = getelementptr [10 x i32], [10 x i32]* @f, i32 0, i32 0
  store i32 0, i32* %t1
  %t2 = getelementptr [10 x i32], [10 x i32]* @f, i32 0, i32 1
  store i32 1, i32* %t2
  store i32 2, i32* %t0
  br label %for.cond.0
for.cond.0:
  %t3 = load i32, i32* %t0
  %t4 = load i32, i32* @N
  %t5 = icmp slt i32 %t3, %t4
  br i1 %t5, label %for.body.1, label %for.end.3
for.body.1:
  %t6 = load i32, i32* %t0
  %t7 = getelementptr [10 x i32], [10 x i32]* @f, i32 0, i32 %t6
  %t8 = load i32, i32* %t0
  %t9 = sub i32 %t8, 1
  %t10 = getelementptr [10 x i32], [10 x i32]* @f, i32 0, i32 %t9
  %t11 = load i32, i32* %t10
  %t12 = load i32, i32* %t0
  %t13 = sub i32 %t12, 2
  %t14 = getelementptr [10 x i32], [10 x i32]* @f, i32 0, i32 %t13
  %t15 = load i32, i32* %t14
  %t16 = add i32 %t11, %t15
  store i32 %t16, i32* %t7
  br label %for.step.2
for.step.2:
  %t17 = load i32, i32* %t0
  %t18 = add i32 %t17, 1
  store i32 %t18, i32* %t0
  br label %for.cond.0
for.end.3:
  store i32 0, i32* %t0
  br label %for.cond.4
for.cond.4:
  %t19 = load i32, i32* %t0
  %t20 = load i32, i32* @N
  %t21 = icmp slt i32 %t19, %t20
  br i1 %t21, label %for.body.5, label %for.end.7
for.body.5:
  %t22 = load i32, i32* %t0
  %t23 = getelementptr [10 x i32], [10 x i32]* @f, i32 0, i32 %t22
  %t24 = load i32, i32* %t23
  call void @print_int(i32 %t24)
  call void @print_char(i8 32)
  br label %for.step.6
for.step.6:
  %t25 = load i32, i32* %t0
  %t26 = add i32 %t25, 1
  store i32 %t26, i32* %t0
  br label %for.cond.4
for.end.7:
  ret void
}

