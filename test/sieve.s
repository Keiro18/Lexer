	.text
	.file	"sieve.ll"
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
	movl	$0, (%rsp)
	movq	N@GOTPCREL(%rip), %rbx
	movq	isprime@GOTPCREL(%rip), %r14
	.p2align	4, 0x90
.LBB0_1:                                # %for.cond.0
                                        # =>This Inner Loop Header: Depth=1
	movl	(%rsp), %eax
	cmpl	(%rbx), %eax
	jge	.LBB0_3
# %bb.2:                                # %for.body.1
                                        #   in Loop: Header=BB0_1 Depth=1
	movslq	(%rsp), %rax
	movb	$1, (%r14,%rax)
	incl	%eax
	movl	%eax, (%rsp)
	jmp	.LBB0_1
.LBB0_3:                                # %for.end.3
	movw	$0, (%r14)
	movl	$2, (%rsp)
	jmp	.LBB0_4
	.p2align	4, 0x90
.LBB0_14:                               # %if.end.8
                                        #   in Loop: Header=BB0_4 Depth=1
	incl	(%rsp)
.LBB0_4:                                # %while.cond.4
                                        # =>This Loop Header: Depth=1
                                        #     Child Loop BB0_7 Depth 2
	movl	(%rsp), %eax
	imull	%eax, %eax
	cmpl	(%rbx), %eax
	jge	.LBB0_9
# %bb.5:                                # %while.body.5
                                        #   in Loop: Header=BB0_4 Depth=1
	movslq	(%rsp), %rax
	cmpb	$0, (%r14,%rax)
	je	.LBB0_14
# %bb.6:                                # %if.then.7
                                        #   in Loop: Header=BB0_4 Depth=1
	movl	(%rsp), %eax
	imull	%eax, %eax
	movl	%eax, 4(%rsp)
	.p2align	4, 0x90
.LBB0_7:                                # %while.cond.9
                                        #   Parent Loop BB0_4 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movl	4(%rsp), %eax
	cmpl	(%rbx), %eax
	jge	.LBB0_14
# %bb.8:                                # %while.body.10
                                        #   in Loop: Header=BB0_7 Depth=2
	movslq	4(%rsp), %rax
	movb	$0, (%r14,%rax)
	movl	(%rsp), %ecx
	addl	%eax, %ecx
	movl	%ecx, 4(%rsp)
	jmp	.LBB0_7
.LBB0_9:                                # %while.end.6
	movl	$80, %edi
	callq	print_char@PLT
	movl	$114, %edi
	callq	print_char@PLT
	movl	$105, %edi
	callq	print_char@PLT
	movl	$109, %edi
	callq	print_char@PLT
	movl	$111, %edi
	callq	print_char@PLT
	movl	$115, %edi
	callq	print_char@PLT
	movl	$32, %edi
	callq	print_char@PLT
	movl	$109, %edi
	callq	print_char@PLT
	movl	$101, %edi
	callq	print_char@PLT
	movl	$110, %edi
	callq	print_char@PLT
	movl	$111, %edi
	callq	print_char@PLT
	movl	$114, %edi
	callq	print_char@PLT
	movl	$101, %edi
	callq	print_char@PLT
	movl	$115, %edi
	callq	print_char@PLT
	movl	$32, %edi
	callq	print_char@PLT
	movl	$113, %edi
	callq	print_char@PLT
	movl	$117, %edi
	callq	print_char@PLT
	movl	$101, %edi
	callq	print_char@PLT
	movl	$32, %edi
	callq	print_char@PLT
	movl	$49, %edi
	callq	print_char@PLT
	movl	$48, %edi
	callq	print_char@PLT
	movl	$48, %edi
	callq	print_char@PLT
	movl	$58, %edi
	callq	print_char@PLT
	movl	$2, (%rsp)
	jmp	.LBB0_10
	.p2align	4, 0x90
.LBB0_13:                               # %if.end.17
                                        #   in Loop: Header=BB0_10 Depth=1
	incl	(%rsp)
.LBB0_10:                               # %for.cond.12
                                        # =>This Inner Loop Header: Depth=1
	movl	(%rsp), %eax
	cmpl	(%rbx), %eax
	jge	.LBB0_15
# %bb.11:                               # %for.body.13
                                        #   in Loop: Header=BB0_10 Depth=1
	movslq	(%rsp), %rax
	cmpb	$0, (%r14,%rax)
	je	.LBB0_13
# %bb.12:                               # %if.then.16
                                        #   in Loop: Header=BB0_10 Depth=1
	movl	(%rsp), %edi
	callq	print_int@PLT
	movl	$32, %edi
	callq	print_char@PLT
	movl	$124, %edi
	callq	print_char@PLT
	movl	$32, %edi
	callq	print_char@PLT
	jmp	.LBB0_13
.LBB0_15:                               # %for.end.15
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
	.long	100                             # 0x64
	.size	N, 4

	.type	isprime,@object                 # @isprime
	.bss
	.globl	isprime
	.p2align	4
isprime:
	.zero	100
	.size	isprime, 100

	.section	".note.GNU-stack","",@progbits
