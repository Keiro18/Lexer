declare void @print_int(i32)
declare void @print_float(float)
declare void @print_bool(i1)
declare void @print_char(i8)
define void @main() {
entry:
  %t0 = alloca i32
  store i32 5, i32* %t0
  %t1 = load i32, i32* %t0
  %t2 = icmp sgt i32 %t1, 3
  br i1 %t2, label %if.then.0, label %if.else.1
if.then.0:
  call void @print_int(i32 1)
  br label %if.end.2
if.else.1:
  call void @print_int(i32 0)
  br label %if.end.2
if.end.2:
  ret void
}

