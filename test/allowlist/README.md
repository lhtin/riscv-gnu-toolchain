This folder contain all allowlist files for testsuite result,
it used for `riscv-gnu-toolchain/scripts/testsuite-filter`,
naming rule of allowlist file as below:

```
<toolname>/common.log
<toolname>/[<lib>.][rv(32|64|128).][<ext>.][<abi>.][<cmodel>.][<sim>.]log
```

- `toolname` can be `gcc`, `binutils` or `gdb`.

- `<toolname>/common.log`: Every target/library combination for the `<toolname>`
  will use this allowlist file.

- `<toolname>/[<lib>.][rv(32|64|128).][<ext>.][<abi>.][<cmodel>.][<sim>.]log`: `testsuite-filter`
  will according the target/library combination to match corresponding allowlist
  files.

- For example, rv32im,ilp32,medlow/newlib on spike simulater will match following 24 files, and ignored if
  file not exist:
  - common.log
  - one name
    - `<lib>`
      - newlib.log
    - `rv(32|64|128)`
      - rv32.log
    - `<ext>`
      - i.log
      - m.log
      - im.log
    - `<abi>`
      - ilp32.log
    - `<cmodel>`
      - medlow.log
    - `<sim>`
      - spike.log
  - tow name combo
    - newlib.rv32.log
    - etc.
  - three name combo
    - newlib.rv32.medlow.log
    - etc.
  - four name combo
    - newlib.rv32.ilp32.medlow.log
    - etc.
  - five name combo
    - newlib.rv32.im.ilp32.medlow.log
    - etc.
  - six name comb
    - newlib.rv32.im.ilp32.medlow.spike.log
