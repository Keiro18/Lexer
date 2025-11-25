	.text
	.file	"knight.ll"
	.globl	index                           # -- Begin function index
	.p2align	4, 0x90
	.type	index,@function
index:                                  # @index
	.cfi_startproc
# %bb.0:                                # %entry
                                        # kill: def $esi killed $esi def $rsi
                                        # kill: def $edi killed $edi def $rdi
	movl	%edi, -4(%rsp)
	movl	%esi, -8(%rsp)
	movq	N@GOTPCREL(%rip), %rax
	imull	(%rax), %edi
	leal	(%rdi,%rsi), %eax
	retq
.Lfunc_end0:
	.size	index, .Lfunc_end0-index
	.cfi_endproc
                                        # -- End function
	.globl	print_board                     # -- Begin function print_board
	.p2align	4, 0x90
	.type	print_board,@function
print_board:                            # @print_board
	.cfi_startproc
# %bb.0:                                # %entry
	pushq	%rbx
	.cfi_def_cfa_offset 16
	subq	$16, %rsp
	.cfi_def_cfa_offset 32
	.cfi_offset %rbx, -16
	movq	%rdi, 8(%rsp)
	movl	$0, 4(%rsp)
	movq	N@GOTPCREL(%rip), %rbx
	jmp	.LBB1_1
	.p2align	4, 0x90
.LBB1_5:                                # %for.end.7
                                        #   in Loop: Header=BB1_1 Depth=1
	movl	$10, %edi
	callq	print_char@PLT
	incl	4(%rsp)
.LBB1_1:                                # %for.cond.0
                                        # =>This Loop Header: Depth=1
                                        #     Child Loop BB1_3 Depth 2
	movl	4(%rsp), %eax
	cmpl	(%rbx), %eax
	jge	.LBB1_6
# %bb.2:                                # %for.body.1
                                        #   in Loop: Header=BB1_1 Depth=1
	movl	$0, (%rsp)
	.p2align	4, 0x90
.LBB1_3:                                # %for.cond.4
                                        #   Parent Loop BB1_1 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movl	(%rsp), %eax
	cmpl	(%rbx), %eax
	jge	.LBB1_5
# %bb.4:                                # %for.body.5
                                        #   in Loop: Header=BB1_3 Depth=2
	movl	4(%rsp), %edi
	movl	(%rsp), %esi
	callq	index@PLT
	movq	8(%rsp), %rcx
	cltq
	movl	(%rcx,%rax,4), %edi
	callq	print_int@PLT
	movl	$32, %edi
	callq	print_char@PLT
	incl	(%rsp)
	jmp	.LBB1_3
.LBB1_6:                                # %for.end.3
	addq	$16, %rsp
	.cfi_def_cfa_offset 16
	popq	%rbx
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end1:
	.size	print_board, .Lfunc_end1-print_board
	.cfi_endproc
                                        # -- End function
	.globl	can_move                        # -- Begin function can_move
	.p2align	4, 0x90
	.type	can_move,@function
can_move:                               # @can_move
	.cfi_startproc
# %bb.0:                                # %entry
	subq	$24, %rsp
	.cfi_def_cfa_offset 32
	movl	%edi, 12(%rsp)
	movl	%esi, 8(%rsp)
	movq	%rdx, 16(%rsp)
	testl	%edi, %edi
	setns	%r8b
	movq	N@GOTPCREL(%rip), %rcx
	movl	(%rcx), %ecx
	cmpl	%ecx, %edi
	setl	%dl
	testl	%esi, %esi
	setns	%al
	andb	%dl, %al
	cmpl	%ecx, %esi
	setl	%cl
	andb	%al, %cl
	andb	%r8b, %cl
	movb	%cl, 7(%rsp)
	cmpb	$1, %cl
	jne	.LBB2_2
# %bb.1:                                # %if.then.0
	movl	12(%rsp), %edi
	movl	8(%rsp), %esi
	callq	index@PLT
	movq	16(%rsp), %rcx
	cltq
	cmpl	$0, (%rcx,%rax,4)
	sete	%al
	sete	6(%rsp)
	addq	$24, %rsp
	.cfi_def_cfa_offset 8
	retq
.LBB2_2:                                # %if.end.1
	.cfi_def_cfa_offset 32
	xorl	%eax, %eax
	addq	$24, %rsp
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end2:
	.size	can_move, .Lfunc_end2-can_move
	.cfi_endproc
                                        # -- End function
	.globl	walk                            # -- Begin function walk
	.p2align	4, 0x90
	.type	walk,@function
walk:                                   # @walk
	.cfi_startproc
# %bb.0:                                # %entry
	subq	$56, %rsp
	.cfi_def_cfa_offset 64
	movl	%edi, 36(%rsp)
	movl	%esi, 32(%rsp)
	movl	%edx, 28(%rsp)
	movq	%rcx, 16(%rsp)
	movq	%r8, 48(%rsp)
	movq	%r9, 40(%rsp)
	movq	N@GOTPCREL(%rip), %rax
	movl	(%rax), %eax
	imull	%eax, %eax
	cmpl	%eax, %edx
	jne	.LBB3_3
# %bb.1:                                # %if.then.0
	movq	16(%rsp), %rdi
	callq	print_board@PLT
.LBB3_2:                                # %if.then.8
	movb	$1, %al
	addq	$56, %rsp
	.cfi_def_cfa_offset 8
	retq
.LBB3_3:                                # %if.end.1
	.cfi_def_cfa_offset 64
	movl	$0, 12(%rsp)
	jmp	.LBB3_4
	.p2align	4, 0x90
.LBB3_8:                                # %if.end.7
                                        #   in Loop: Header=BB3_4 Depth=1
	incl	12(%rsp)
.LBB3_4:                                # %for.cond.2
                                        # =>This Inner Loop Header: Depth=1
	cmpl	$7, 12(%rsp)
	jg	.LBB3_9
# %bb.5:                                # %for.body.3
                                        #   in Loop: Header=BB3_4 Depth=1
	movl	36(%rsp), %edi
	movq	48(%rsp), %rax
	movslq	12(%rsp), %rcx
	addl	(%rax,%rcx,4), %edi
	movl	%edi, 8(%rsp)
	movl	32(%rsp), %esi
	movq	40(%rsp), %rax
	addl	(%rax,%rcx,4), %esi
	movl	%esi, 4(%rsp)
	movq	16(%rsp), %rdx
	callq	can_move@PLT
	testb	$1, %al
	je	.LBB3_8
# %bb.6:                                # %if.then.6
                                        #   in Loop: Header=BB3_4 Depth=1
	movl	8(%rsp), %edi
	movl	4(%rsp), %esi
	callq	index@PLT
	movq	16(%rsp), %rcx
	cltq
	movl	28(%rsp), %edx
	movl	%edx, (%rcx,%rax,4)
	movl	8(%rsp), %edi
	movl	4(%rsp), %esi
	movl	28(%rsp), %edx
	incl	%edx
	movq	16(%rsp), %rcx
	movq	48(%rsp), %r8
	movq	40(%rsp), %r9
	callq	walk@PLT
	testb	$1, %al
	jne	.LBB3_2
# %bb.7:                                # %if.end.9
                                        #   in Loop: Header=BB3_4 Depth=1
	movl	8(%rsp), %edi
	movl	4(%rsp), %esi
	callq	index@PLT
	movq	16(%rsp), %rcx
	cltq
	movl	$0, (%rcx,%rax,4)
	jmp	.LBB3_8
.LBB3_9:                                # %for.end.5
	xorl	%eax, %eax
	addq	$56, %rsp
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end3:
	.size	walk, .Lfunc_end3-walk
	.cfi_endproc
                                        # -- End function
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:                                # %entry
	subq	$168, %rsp
	.cfi_def_cfa_offset 176
	movabsq	$4294967298, %rax               # imm = 0x100000002
	movq	%rax, 36(%rsp)
	movabsq	$-4294967297, %rcx              # imm = 0xFFFFFFFEFFFFFFFF
	movq	%rcx, 44(%rsp)
	movq	$-2, 52(%rsp)
	movabsq	$8589934593, %rdx               # imm = 0x200000001
	movq	%rdx, 60(%rsp)
	movq	%rdx, 4(%rsp)
	movq	%rax, 12(%rsp)
	movq	%rcx, 20(%rsp)
	movq	$-2, 28(%rsp)
	xorl	%edi, %edi
	xorl	%esi, %esi
	callq	index@PLT
	cltq
	movl	$1, 68(%rsp,%rax,4)
	leaq	68(%rsp), %rcx
	leaq	36(%rsp), %r8
	leaq	4(%rsp), %r9
	xorl	%edi, %edi
	xorl	%esi, %esi
	movl	$2, %edx
	callq	walk@PLT
	testb	$1, %al
	je	.LBB4_2
# %bb.1:                                # %if.then.0
	movl	$83, %edi
	callq	print_char@PLT
	movl	$111, %edi
	callq	print_char@PLT
	movl	$108, %edi
	callq	print_char@PLT
	movl	$117, %edi
	callq	print_char@PLT
	movl	$99, %edi
	callq	print_char@PLT
	movl	$105, %edi
	callq	print_char@PLT
	movl	$111, %edi
	callq	print_char@PLT
	movl	$110, %edi
	callq	print_char@PLT
	movl	$32, %edi
	callq	print_char@PLT
	movl	$101, %edi
	callq	print_char@PLT
	movl	$110, %edi
	callq	print_char@PLT
	movl	$99, %edi
	callq	print_char@PLT
	movl	$111, %edi
	callq	print_char@PLT
	movl	$110, %edi
	callq	print_char@PLT
	movl	$116, %edi
	callq	print_char@PLT
	movl	$114, %edi
	callq	print_char@PLT
	movl	$97, %edi
	callq	print_char@PLT
	movl	$100, %edi
	callq	print_char@PLT
	movl	$97, %edi
	callq	print_char@PLT
	movl	$33, %edi
	jmp	.LBB4_3
.LBB4_2:                                # %if.else.1
	movl	$78, %edi
	callq	print_char@PLT
	movl	$111, %edi
	callq	print_char@PLT
	movl	$32, %edi
	callq	print_char@PLT
	movl	$101, %edi
	callq	print_char@PLT
	movl	$120, %edi
	callq	print_char@PLT
	movl	$105, %edi
	callq	print_char@PLT
	movl	$115, %edi
	callq	print_char@PLT
	movl	$116, %edi
	callq	print_char@PLT
	movl	$101, %edi
	callq	print_char@PLT
	movl	$32, %edi
	callq	print_char@PLT
	movl	$115, %edi
	callq	print_char@PLT
	movl	$111, %edi
	callq	print_char@PLT
	movl	$108, %edi
	callq	print_char@PLT
	movl	$117, %edi
	callq	print_char@PLT
	movl	$99, %edi
	callq	print_char@PLT
	movl	$105, %edi
	callq	print_char@PLT
	movl	$111, %edi
	callq	print_char@PLT
	movl	$110, %edi
.LBB4_3:                                # %if.end.2
	callq	print_char@PLT
	movl	$10, %edi
	callq	print_char@PLT
	xorl	%eax, %eax
	addq	$168, %rsp
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end4:
	.size	main, .Lfunc_end4-main
	.cfi_endproc
                                        # -- End function
	.type	N,@object                       # @N
	.data
	.globl	N
	.p2align	2
N:
	.long	5                               # 0x5
	.size	N, 4

	.section	".note.GNU-stack","",@progbits
