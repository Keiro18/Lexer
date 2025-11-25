@xmin = global float -2.0
@xmax = global float 1.0
@ymin = global float -1.5
@ymax = global float 1.5
@width = global float 80.0
@height = global float 40.0
@threshhold = global i32 1000
declare void @print_int(i32)
declare void @print_float(float)
declare void @print_bool(i1)
declare void @print_char(i8)
define i1 @in_mandelbrot(float %x0, float %y0, i32 %n) {
entry:
  %t0 = alloca float
  store float %x0, float* %t0
  %t1 = alloca float
  store float %y0, float* %t1
  %t2 = alloca i32
  store i32 %n, i32* %t2
  %t3 = alloca float
  store float 0.0, float* %t3
  %t4 = alloca float
  store float 0.0, float* %t4
  %t5 = alloca float
  br label %while.cond.0
while.cond.0:
  %t6 = load i32, i32* %t2
  %t7 = icmp sgt i32 %t6, 0
  br i1 %t7, label %while.body.1, label %while.end.2
while.body.1:
  %t8 = load float, float* %t3
  %t9 = load float, float* %t3
  %t10 = fmul float %t8, %t9
  %t11 = load float, float* %t4
  %t12 = load float, float* %t4
  %t13 = fmul float %t11, %t12
  %t14 = fsub float %t10, %t13
  %t15 = load float, float* %t0
  %t16 = fadd float %t14, %t15
  store float %t16, float* %t5
  %t17 = load float, float* %t3
  %t18 = fmul float 2.0, %t17
  %t19 = load float, float* %t4
  %t20 = fmul float %t18, %t19
  %t21 = load float, float* %t1
  %t22 = fadd float %t20, %t21
  store float %t22, float* %t4
  %t23 = load float, float* %t5
  store float %t23, float* %t3
  %t24 = load i32, i32* %t2
  %t25 = sub i32 %t24, 1
  store i32 %t25, i32* %t2
  %t26 = load float, float* %t3
  %t27 = load float, float* %t3
  %t28 = fmul float %t26, %t27
  %t29 = load float, float* %t4
  %t30 = load float, float* %t4
  %t31 = fmul float %t29, %t30
  %t32 = fadd float %t28, %t31
  %t33 = fcmp ogt float %t32, 4.0
  br i1 %t33, label %if.then.3, label %if.end.4
while.end.2:
  ret i1 1
if.then.3:
  ret i1 0
if.end.4:
  br label %while.cond.0
}
define i32 @mandel() {
entry:
  %t0 = alloca float
  %t1 = load float, float* @xmax
  %t2 = load float, float* @xmin
  %t3 = fsub float %t1, %t2
  %t4 = load float, float* @width
  %t5 = fdiv float %t3, %t4
  store float %t5, float* %t0
  %t6 = alloca float
  %t7 = load float, float* @ymax
  %t8 = load float, float* @ymin
  %t9 = fsub float %t7, %t8
  %t10 = load float, float* @height
  %t11 = fdiv float %t9, %t10
  store float %t11, float* %t6
  %t12 = alloca float
  %t13 = load float, float* @ymax
  store float %t13, float* %t12
  %t14 = alloca float
  br label %while.cond.0
while.cond.0:
  %t15 = load float, float* %t12
  %t16 = load float, float* @ymin
  %t17 = fcmp oge float %t15, %t16
  br i1 %t17, label %while.body.1, label %while.end.2
while.body.1:
  %t18 = load float, float* @xmin
  store float %t18, float* %t14
  br label %while.cond.3
while.end.2:
  ret i32 0
while.cond.3:
  %t19 = load float, float* %t14
  %t20 = load float, float* @xmax
  %t21 = fcmp olt float %t19, %t20
  br i1 %t21, label %while.body.4, label %while.end.5
while.body.4:
  %t22 = load float, float* %t14
  %t23 = load float, float* %t12
  %t24 = load i32, i32* @threshhold
  %t25 = call i1 @in_mandelbrot(float %t22, float %t23, i32 %t24)
  br i1 %t25, label %if.then.6, label %if.else.7
while.end.5:
  call void @print_char(i8 10)
  %t29 = load float, float* %t12
  %t30 = load float, float* %t6
  %t31 = fsub float %t29, %t30
  store float %t31, float* %t12
  br label %while.cond.0
if.then.6:
  call void @print_char(i8 42)
  br label %if.end.8
if.else.7:
  call void @print_char(i8 46)
  br label %if.end.8
if.end.8:
  %t26 = load float, float* %t14
  %t27 = load float, float* %t0
  %t28 = fadd float %t26, %t27
  store float %t28, float* %t14
  br label %while.cond.3
}
define i32 @main() {
entry:
  %t0 = call i32 @mandel()
  ret i32 %t0
}

