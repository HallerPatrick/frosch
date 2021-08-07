# Getting Started

`frosch` can be used by installing it with `pip`:

```shell
pip install frosch
```

## Usage

``` python
from frosch import hook

hook()

x = 3 + "String" # This is not working!
```

If you dont feel like calling the hook manually, you can just import `frosch.activate` and 
the hook is already executed!

```python
import frosch.activate

x = 3 + "String" # This is not working!
```
