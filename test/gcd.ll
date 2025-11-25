declare void @print_int(i32)
declare void @print_float(float)
declare void @print_bool(i1)
declare void @print_char(i8)
define i32 @gcd(i32 %m, i32 %n) {
entry:
  %t0 = alloca i32
  store i32 %m, i32* %t0
  %t1 = alloca i32
  store i32 %n, i32* %t1
  %t2 = load i32, i32* %t0
  %t3 = load i32, i32* %t1
  %t4 = srem i32 %t2, %t3
  %t5 = icmp eq i32 %t4, 0
  br i1 %t5, label %if.then.0, label %if.else.1
if.then.0:
  %t6 = load i32, i32* %t1
  ret i32 %t6
if.else.1:
  %t7 = load i32, i32* %t1
  %t8 = load i32, i32* %t0
  %t9 = load i32, i32* %t1
  %t10 = srem i32 %t8, %t9
  %t11 = call i32 @gcd(i32 %t7, i32 %t10)
  ret i32 %t11
}
define void @main() {
entry:
  %t0 = alloca i32
  %t1 = call i32 @gcd(i32 20, i32 8)
  store i32 %t1, i32* %t0
  %t2 = load i32, i32* %t0
  call void @print_int(i32 %t2)
  ret void
}

