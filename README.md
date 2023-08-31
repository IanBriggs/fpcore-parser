# FPCore Parser
An attempt at an FPCore 2.0 compliant parser in python.

Relevant information can be found at
[FPBench's website](https://fpbench.org/spec/fpcore-2.0.html)

## Requirements
__[SLY](https://sly.readthedocs.io/en/latest/)__, a lexer and parser generator.


## Modifications from stated grammar or given regex
* `(# <expr>)` added as syntactic sugar for `(! precision integer <expr>)`
* strings regex extended to include all whitespace characters
* added Greek Unicode letters (α-ωΑ-Ω) to symbols and strings
* added Unicode × to strings
* `<data>` can be `<operation> | <let> | <binding>`
* `<data>` can also be `( if <expr> <expr> <expr> )`
* changed `( <operation> <expr>+ )` to  `( <operation> <expr>* )`
* `<property>` can be `operation <data>`
* Created the new lex token `ADDED_OPERATION` that gets populated with named FPCores
* Also added parse rule to use these as normal operators


## Things present in existing FPCores that are not supported

### [FPBench](https://github.com/FPBench/FPBench)
* Using reserved names as variables
  - `benchmarks/fptaylor-real2float.fpcore`

### [Herbie](https://github.com/herbie-fp/herbie)
* Using parenthesis for let bindings
  - `bench/mathematics/latlong.fpcore`
  - `bench/libraries/jmatjs.fpcore`
  - `bench/libraries/octave/CollocWt.fpcore`
  - `bench/libraries/octave/randgamma.fpcore`
  - `bench/numerics/rosa.fpcore`
  - `bench/numerics/martel.fpcore`
  - `bench/numerics/every-cs.fpcore`
  - `bench/demo.fpcore`
  - `bench/hamming/quadratic.fpcore`
  - `bench/physics/tea-flows.fpcore`
  - `bench/physics/tea-whistle.fpcore`

#### etc
* ascii font used in header comments is "Graceful" from
[patorjk.com](https://patorjk.com/software/taag/#p=display&f=Graceful&t=Type%20Something%20)