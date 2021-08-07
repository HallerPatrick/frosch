# Themes

If you get tired of seeing your `frosch` output always in the same color theme or it does not fit well with
your theming of your terminal, you can switch it with a different color palette or even create your own ones.

Following themes can be used directly:

| Themes   |          |          |               |             |      |
|----------|----------|----------|---------------|-------------|------|
| abap     | bw       | igor     | native        | rrt         | trac |
| algol    | colorful | inkpot   | paraiso_dark  | sas         | vim  |
| algol_nu | default  | lovelace | paraiso_light | solarized   | vs   |
| arduino  | emacs    | manni    | pastie        | stata_dark  | xcode |
| autumn   | friendly | monokai  | perldoc       | stata_light |      |
| borland  | fruity   | murphy   | rainbow_dash  | tango       |      |


## Usage

```python
from frosch import hook

hook(theme="vim")
```

## Custom Themes

Custom themes can be created throught the `frosch.style` API:

```python

from frosch import hook
from frosch.style import Style
from frosch.style.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic

class CustomStyle(Style):
    default_style = ""
    styles = {
        Comment:                'italic #888',
        Keyword:                'bold #005',
        Name:                   '#f00',
        Name.Function:          '#0f0',
        Name.Class:             'bold #0f0',
        String:                 'bg:#eee #111'
    }

hook(theme=CustomStyle)

```

In the future the theme can be read from a global config so it does not always has to be written/set in your python projects.
