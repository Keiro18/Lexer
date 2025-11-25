	.text
	.file	"mandel.ll"
	.section	.rodata.cst4,"aM",@progbits,4
	.p2align	2                               # -- Begin function in_mandelbrot
.LCPI0_0:
	.long	0x40800000                      # float 4
	.text
	.globl	in_mandelbrot
	.p2align	4, 0x90
	.type	in_mandelbrot,@function
in_mandelbrot:                          # @in_mandelbrot
	.cfi_startproc
# %bb.0:                                # %entry
	movss	%xmm0, -8(%rsp)
	movss	%xmm1, -12(%rsp)
	movl	%edi, -16(%rsp)
	movl	$0, -20(%rsp)
	movl	$0, -24(%rsp)
	movss	.LCPI0_0(%rip), %xmm0           # xmm0 = mem[0],zero,zero,zero
	.p2align	4, 0x90
.LBB0_1:                                # %while.cond.0
                                        # =>This Inner Loop Header: Depth=1
	cmpl	$0, -16(%rsp)
	jle	.LBB0_4
# %bb.2:                                # %while.body.1
                                        #   in Loop: Header=BB0_1 Depth=1
	movss	-20(%rsp), %xmm1                # xmm1 = mem[0],zero,zero,zero
	movaps	%xmm1, %xmm2
	mulss	%xmm1, %xmm2
	movss	-24(%rsp), %xmm3                # xmm3 = mem[0],zero,zero,zero
	addss	%xmm1, %xmm1
	mulss	%xmm3, %xmm1
	mulss	%xmm3, %xmm3
	subss	%xmm3, %xmm2
	addss	-8(%rsp), %xmm2
	movss	%xmm2, -4(%rsp)
	addss	-12(%rsp), %xmm1
	movss	%xmm1, -24(%rsp)
	movss	%xmm2, -20(%rsp)
	decl	-16(%rsp)
	mulss	%xmm2, %xmm2
	mulss	%xmm1, %xmm1
	addss	%xmm2, %xmm1
	ucomiss	%xmm0, %xmm1
	jbe	.LBB0_1
# %bb.3:                                # %if.then.3
	xorl	%eax, %eax
	retq
.LBB0_4:                                # %while.end.2
	movb	$1, %al
	retq
.Lfunc_end0:
	.size	in_mandelbrot, .Lfunc_end0-in_mandelbrot
	.cfi_endproc
                                        # -- End function
	.globl	mandel                          # -- Begin function mandel
	.p2align	4, 0x90
	.type	mandel,@function
mandel:                                 # @mandel
	.cfi_startproc
# %bb.0:                                # %entry
	pushq	%r15
	.cfi_def_cfa_offset 16
	pushq	%r14
	.cfi_def_cfa_offset 24
	pushq	%r12
	.cfi_def_cfa_offset 32
	pushq	%rbx
	.cfi_def_cfa_offset 40
	subq	$24, %rsp
	.cfi_def_cfa_offset 64
	.cfi_offset %rbx, -40
	.cfi_offset %r12, -32
	.cfi_offset %r14, -24
	.cfi_offset %r15, -16
	movq	xmax@GOTPCREL(%rip), %r12
	movss	(%r12), %xmm0                   # xmm0 = mem[0],zero,zero,zero
	movq	xmin@GOTPCREL(%rip), %r14
	subss	(%r14), %xmm0
	movq	width@GOTPCREL(%rip), %rax
	divss	(%rax), %xmm0
	movss	%xmm0, 20(%rsp)
	movq	ymax@GOTPCREL(%rip), %rax
	movq	ymin@GOTPCREL(%rip), %r15
	movss	(%rax), %xmm0                   # xmm0 = mem[0],zero,zero,zero
	movss	%xmm0, 12(%rsp)
	subss	(%r15), %xmm0
	movq	height@GOTPCREL(%rip), %rax
	divss	(%rax), %xmm0
	movss	%xmm0, 16(%rsp)
	movq	threshhold@GOTPCREL(%rip), %rbx
	jmp	.LBB1_1
	.p2align	4, 0x90
.LBB1_9:                                # %while.end.5
                                        #   in Loop: Header=BB1_1 Depth=1
	movl	$10, %edi
	callq	print_char@PLT
	movss	12(%rsp), %xmm0                 # xmm0 = mem[0],zero,zero,zero
	subss	16(%rsp), %xmm0
	movss	%xmm0, 12(%rsp)
.LBB1_1:                                # %while.cond.0
                                        # =>This Loop Header: Depth=1
                                        #     Child Loop BB1_3 Depth 2
	movss	12(%rsp), %xmm0                 # xmm0 = mem[0],zero,zero,zero
	ucomiss	(%r15), %xmm0
	jb	.LBB1_8
# %bb.2:                                # %while.body.1
                                        #   in Loop: Header=BB1_1 Depth=1
	movss	(%r14), %xmm0                   # xmm0 = mem[0],zero,zero,zero
	jmp	.LBB1_3
	.p2align	4, 0x90
.LBB1_6:                                # %if.else.7
                                        #   in Loop: Header=BB1_3 Depth=2
	movl	$46, %edi
.LBB1_7:                                # %if.end.8
                                        #   in Loop: Header=BB1_3 Depth=2
	callq	print_char@PLT
	movss	8(%rsp), %xmm0                  # xmm0 = mem[0],zero,zero,zero
	addss	20(%rsp), %xmm0
.LBB1_3:                                # %while.cond.3
                                        #   Parent Loop BB1_1 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movss	%xmm0, 8(%rsp)
	movss	(%r12), %xmm0                   # xmm0 = mem[0],zero,zero,zero
	ucomiss	8(%rsp), %xmm0
	jbe	.LBB1_9
# %bb.4:                                # %while.body.4
                                        #   in Loop: Header=BB1_3 Depth=2
	movss	8(%rsp), %xmm0                  # xmm0 = mem[0],zero,zero,zero
	movss	12(%rsp), %xmm1                 # xmm1 = mem[0],zero,zero,zero
	movl	(%rbx), %edi
	callq	in_mandelbrot@PLT
	testb	$1, %al
	je	.LBB1_6
# %bb.5:                                # %if.then.6
                                        #   in Loop: Header=BB1_3 Depth=2
	movl	$42, %edi
	jmp	.LBB1_7
.LBB1_8:                                # %while.end.2
	xorl	%eax, %eax
	addq	$24, %rsp
	.cfi_def_cfa_offset 40
	popq	%rbx
	.cfi_def_cfa_offset 32
	popq	%r12
	.cfi_def_cfa_offset 24
	popq	%r14
	.cfi_def_cfa_offset 16
	popq	%r15
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end1:
	.size	mandel, .Lfunc_end1-mandel
	.cfi_endproc
                                        # -- End function
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:                                # %entry
	pushq	%rax
	.cfi_def_cfa_offset 16
	callq	mandel@PLT
	popq	%rcx
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end2:
	.size	main, .Lfunc_end2-main
	.cfi_endproc
                                        # -- End function
	.type	xmin,@object                    # @xmin
	.data
	.globl	xmin
	.p2align	2
xmin:
	.long	0xc0000000                      # float -2
	.size	xmin, 4

	.type	xmax,@object                    # @xmax
	.globl	xmax
	.p2align	2
xmax:
	.long	0x3f800000                      # float 1
	.size	xmax, 4

	.type	ymin,@object                    # @ymin
	.globl	ymin
	.p2align	2
ymin:
	.long	0xbfc00000                      # float -1.5
	.size	ymin, 4

	.type	ymax,@object                    # @ymax
	.globl	ymax
	.p2align	2
ymax:
	.long	0x3fc00000                      # float 1.5
	.size	ymax, 4

	.type	width,@object                   # @width
	.globl	width
	.p2align	2
width:
	.long	0x42a00000                      # float 80
	.size	width, 4

	.type	height,@object                  # @height
	.globl	height
	.p2align	2
height:
	.long	0x42200000                      # float 40
	.size	height, 4

	.type	threshhold,@object              # @threshhold
	.globl	threshhold
	.p2align	2
threshhold:
	.long	1000                            # 0x3e8
	.size	threshhold, 4

	.section	".note.GNU-stack","",@progbits
