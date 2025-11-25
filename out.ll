@g_int = global i32 7
@g_char = global i8 65
declare void @print_int(i32)
declare void @print_float(float)
declare void @print_bool(i1)
declare void @print_char(i8)
define i32 @main() {
entry:
  call void @print_char(i8 72)
  call void @print_char(i8 111)
  call void @print_char(i8 108)
  call void @print_char(i8 97)
  call void @print_char(i8 32)
  call void @print_char(i8 109)
  call void @print_char(i8 117)
  call void @print_char(i8 110)
  call void @print_char(i8 100)
  call void @print_char(i8 111)
  call void @print_char(i8 10)
  %t1 = load i32, i32* @g_int
  call void @print_int(i32 %t1)
  call void @print_char(i8 10)
  %t2 = load i8, i8* @g_char
  call void @print_char(i8 %t2)
  call void @print_char(i8 10)
  ret i32 0
}

