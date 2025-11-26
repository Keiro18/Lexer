	.text
	.file	"test_array.ll"
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:                                # %entry
	pushq	%r14
	.cfi_def_cfa_offset 16
	pushq	%rbx
	.cfi_def_cfa_offset 24
	pushq	%rax
	.cfi_def_cfa_offset 32
	.cfi_offset %rbx, -24
	.cfi_offset %r14, -16
	movl	$0, 4(%rsp)
	movq	N@GOTPCREL(%rip), %rbx
	movq	arr@GOTPCREL(%rip), %r14
	.p2align	4, 0x90
.LBB0_1:                                # %for.cond.0
                                        # =>This Inner Loop Header: Depth=1
	movl	4(%rsp), %eax
	cmpl	(%rbx), %eax
	jge	.LBB0_3
# %bb.2:                                # %for.body.1
                                        #   in Loop: Header=BB0_1 Depth=1
	movslq	4(%rsp), %rax
	leal	(%rax,%rax), %ecx
	movl	%ecx, (%r14,%rax,4)
	incl	4(%rsp)
	jmp	.LBB0_1
.LBB0_3:                                # %for.end.3
	movl	$0, 4(%rsp)
	.p2align	4, 0x90
.LBB0_4:                                # %for.cond.4
                                        # =>This Inner Loop Header: Depth=1
	movl	4(%rsp), %eax
	cmpl	(%rbx), %eax
	jge	.LBB0_6
# %bb.5:                                # %for.body.5
                                        #   in Loop: Header=BB0_4 Depth=1
	movslq	4(%rsp), %rax
	movl	(%r14,%rax,4), %edi
	callq	print_int@PLT
	movl	$32, %edi
	callq	print_char@PLT
	incl	4(%rsp)
	jmp	.LBB0_4
.LBB0_6:                                # %for.end.7
	addq	$8, %rsp
	.cfi_def_cfa_offset 24
	popq	%rbx
	.cfi_def_cfa_offset 16
	popq	%r14
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc
                                        # -- End function
	.type	N,@object                       # @N
	.data
	.globl	N
	.p2align	2
N:
	.long	5                               # 0x5
	.size	N, 4

	.type	arr,@object                     # @arr
	.bss
	.globl	arr
	.p2align	4
arr:
	.zero	20
	.size	arr, 20

	.section	".note.GNU-stack","",@progbits
