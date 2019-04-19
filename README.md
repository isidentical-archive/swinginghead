# Swinging Head Language (SHL)
SHL is a !(easy-to-write, easy-to-understand) language that is backed by LLVM.
## Binding
```py
from swinginghead.compiler import Binder

binder = Binder(<code>)
binder.<func_name> => your function

binder = Binder.from_file('examples/demo.shl')
assert binder.head(3.0, 4.0) == 5.0
```

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
## Control Flow Graphs
### Comparison
```
| expr ">" <comp prefix><comp type><comperator> "<" expr | 

,1 >f ordered gt< ,2
```
### If / Then
```
comp "=>" {
    exprs*
}

|,1 >f ordered gt< ,2| => {
    ./ (`float`->2.0)
}
```
### If / Then / Else
```
comp "=>" {
    exprs*
}
"!=>" {
    exprs*
}

|,1 >f ordered gt< ,2| => {
    ./ (`float`->2.0)
}
!=> {
    ./ (`float`->5.0)
}
```
# Functions
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
