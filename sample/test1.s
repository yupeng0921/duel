_start:
	mov %pc, %r0
	add $_end, %r0
loop:
	str $0, %r0
	add $4, %r0
	cmp $8192, %r0
	jc $0x800c
	mov $1, %r0
	cmp $2, %r0
	jc $0x8020
_end:
