@N = global i32 5
@arr = global [5 x i32] zeroinitializer
declare void @print_int(i32)
declare void @print_float(float)
declare void @print_bool(i1)
declare void @print_char(i8)
define void @main() {
entry:
  %t0 = alloca i32
  store i32 0, i32* %t0
  br label %for.cond.0
for.cond.0:
  %t1 = load i32, i32* %t0
  %t2 = load i32, i32* @N
  %t3 = icmp slt i32 %t1, %t2
  br i1 %t3, label %for.body.1, label %for.end.3
for.body.1:
  %t4 = load i32, i32* %t0
  %t5 = getelementptr [5 x i32], [5 x i32]* @arr, i32 0, i32 %t4
  %t6 = load i32, i32* %t0
  %t7 = mul i32 %t6, 2
  store i32 %t7, i32* %t5
  br label %for.step.2
for.step.2:
  %t8 = load i32, i32* %t0
  %t9 = add i32 %t8, 1
  store i32 %t9, i32* %t0
  br label %for.cond.0
for.end.3:
  store i32 0, i32* %t0
  br label %for.cond.4
for.cond.4:
  %t10 = load i32, i32* %t0
  %t11 = load i32, i32* @N
  %t12 = icmp slt i32 %t10, %t11
  br i1 %t12, label %for.body.5, label %for.end.7
for.body.5:
  %t13 = load i32, i32* %t0
  %t14 = getelementptr [5 x i32], [5 x i32]* @arr, i32 0, i32 %t13
  %t15 = load i32, i32* %t14
  call void @print_int(i32 %t15)
  call void @print_char(i8 32)
  br label %for.step.6
for.step.6:
  %t16 = load i32, i32* %t0
  %t17 = add i32 %t16, 1
  store i32 %t17, i32* %t0
  br label %for.cond.4
for.end.7:
  ret void
}

