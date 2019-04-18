# Swinging Head Language (SHL)
SHL is a !(easy-to-write, easy-to-understand) language that is backed by LLVM.
## Types
```
`type(<meta>)?`
`int<32>`
`float`
`array<`int<32>`, 4>`
``` 
## Literals
```
(<type>-><literal>)
(`int<32>`->15)
(`int<64>`->323443)
(`float`->3.35)
(`void`->0)
(`array<`int<32>`, 4>`->@32~44~55~66@)
```
## Pointers
```
<-<value>
<-(`float`->3.35)
```
## Functions
### Func Type
```
swing <return> $<arg1>€....€<argn>$
swing `float` $`float`€`float`$
```
### Body
```
<name> {
    <expr>*
}
add {
    ,1 f+ (`float`->3.35)
    res eqs ,1 f+ ,2
    ./ ,res
}
```
### Local Names
```
,<name>
,1 (first argument)
,n (nth argument)
,xyz (xyz declared upper)
```
### Operations
```
<literal or name> <op prefix> <op> <literal or name>
,1 f+ (`float`->3.35)
```
### Equations
```
<name> eqs <something>
res eqs ,1 f+ ,2
```
### Returning
```
./ <return value>
./ ,res
```
