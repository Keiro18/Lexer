declare void @print_int(i32)
declare void @print_float(float)
declare void @print_bool(i1)
declare void @print_char(i8)
define void @main() {
entry:
  %t0 = add i32 1, 2
  call void @print_int(i32 %t0)
  %t1 = mul i32 3, 4
  call void @print_int(i32 %t1)
  %t2 = sub i32 10, 3
  call void @print_int(i32 %t2)
  %t3 = sdiv i32 20, 5
  call void @print_int(i32 %t3)
  ret void
}

