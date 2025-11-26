	.text
	.file	"test_arith.ll"
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:                                # %entry
	pushq	%rax
	.cfi_def_cfa_offset 16
	movl	$3, %edi
	callq	print_int@PLT
	movl	$12, %edi
	callq	print_int@PLT
	movl	$7, %edi
	callq	print_int@PLT
	movl	$4, %edi
	callq	print_int@PLT
	popq	%rax
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc
                                        # -- End function
	.section	".note.GNU-stack","",@progbits
