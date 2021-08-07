# Exception Printing

You can also easily print your catched exceptions to stdout

```python

from frosch import print_exception

try:
  x = [0, 1]
  x[3]
except IndexError as error:
  print_exception(error)

```

