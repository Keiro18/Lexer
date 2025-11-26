declare void @print_int(i32)
declare void @print_float(float)
declare void @print_bool(i1)
declare void @print_char(i8)
define i32 @sum(i32 %a, i32 %b) {
entry:
  %t0 = alloca i32
  store i32 %a, i32* %t0
  %t1 = alloca i32
  store i32 %b, i32* %t1
  %t2 = load i32, i32* %t0
  %t3 = load i32, i32* %t1
  %t4 = add i32 %t2, %t3
  ret i32 %t4
}
define void @main() {
entry:
  %t0 = call i32 @sum(i32 3, i32 4)
  call void @print_int(i32 %t0)
  ret void
}

