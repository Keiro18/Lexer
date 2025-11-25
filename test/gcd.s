	.text
	.file	"gcd.ll"
	.globl	gcd                             # -- Begin function gcd
	.p2align	4, 0x90
	.type	gcd,@function
gcd:                                    # @gcd
	.cfi_startproc
# %bb.0:                                # %entry
	pushq	%rax
	.cfi_def_cfa_offset 16
	movl	%edi, %eax
	movl	%edi, 4(%rsp)
	movl	%esi, (%rsp)
	cltd
	idivl	%esi
	testl	%edx, %edx
	je	.LBB0_1
# %bb.2:                                # %if.else.1
	movl	(%rsp), %edi
	movl	4(%rsp), %eax
	cltd
	idivl	%edi
	movl	%edx, %esi
	callq	gcd@PLT
	popq	%rcx
	.cfi_def_cfa_offset 8
	retq
.LBB0_1:                                # %if.then.0
	.cfi_def_cfa_offset 16
	movl	(%rsp), %eax
	popq	%rcx
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end0:
	.size	gcd, .Lfunc_end0-gcd
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
	movl	$20, %edi
	movl	$8, %esi
	callq	gcd@PLT
	movl	%eax, 4(%rsp)
	movl	%eax, %edi
	callq	print_int@PLT
	popq	%rax
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end1:
	.size	main, .Lfunc_end1-main
	.cfi_endproc
                                        # -- End function
	.section	".note.GNU-stack","",@progbits
