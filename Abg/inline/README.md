
# Installation

```shell
pip3 install Abg
```

# Documentation

## Inline Keyboard

```python
from Abg.inline import InlineKeyboard
```

##### Parameters:

- row_width (integer, default 3)

### Inline Keyboard add buttons

#### Code

```python
from Abg.inline import InlineKeyboard, InlineButton


keyboard = InlineKeyboard(row_width=3)
keyboard.add(
    InlineButton('1', 'inline_keyboard:1'),
    InlineButton('2', 'inline_keyboard:2'),
    InlineButton('3', 'inline_keyboard:3'),
    InlineButton('4', 'inline_keyboard:4'),
    InlineButton('5', 'inline_keyboard:5'),
    InlineButton('6', 'inline_keyboard:6'),
    InlineButton('7', 'inline_keyboard:7')
)
```

#### Result

<p><img src="https://raw.githubusercontent.com/Abishnoi69/Abg/master/doce/images/add_inline_button.png" alt="add_inline_button"></p>

### Inline Keyboard row buttons

#### Code

```python
from Abg.inline import InlineKeyboard, InlineButton


keyboard = InlineKeyboard()
keyboard.row(InlineButton('1', 'inline_keyboard:1'))
keyboard.row(
    InlineButton('2', 'inline_keyboard:2'),
    InlineButton('3', 'inline_keyboard:3')
)
keyboard.row(InlineButton('4', 'inline_keyboard:4'))
keyboard.row(
    InlineButton('5', 'inline_keyboard:5'),
    InlineButton('6', 'inline_keyboard:6')
)
```

#### Result

<p><img src="https://raw.githubusercontent.com/Abishnoi69/Abg/master/doce/images/row_inline_button.png" alt="row_inline_button"></p>

### Pagination inline keyboard

```python
from Abg.inline import InlineKeyboard
```

#### Parameters:

- count_pages (integer)
- current_page (integer)
- callback_pattern (string) - use of the `{number}` pattern is <ins>required</ins>

#### Pagination 3 pages

#### Code

```python
from Abg.inline import InlineKeyboard

keyboard = InlineKeyboard()
keyboard.paginate(3, 3, 'pagination_keyboard:{number}')
```

#### Result

<p><img src="https://raw.githubusercontent.com/Abishnoi69/Abg/master/doce/images/pagination_keyboard_3.png" alt="pagination_keyboard_3"></p>

#### Pagination 5 pages

#### Code

```python
from Abg.inline import InlineKeyboard

keyboard = InlineKeyboard()
keyboard.paginate(5, 3, 'pagination_keyboard:{number}')
```

#### Result

<p><img src="https://raw.githubusercontent.com/Abishnoi69/Abg/master/doce/images/pagination_keyboard_5.png" alt="pagination_keyboard_5"></p>

#### Pagination 9 pages

#### Code

```python
from Abg.inline import InlineKeyboard

keyboard = InlineKeyboard()
keyboard.paginate(9, 5, 'pagination_keyboard:{number}')
```

#### Result

<p><img src="https://raw.githubusercontent.com/Abishnoi69/Abg/master/doce/images/pagination_keyboard_9.png" alt="pagination_keyboard_9"></p>

#### Pagination 100 pages

#### Code

```python
from Abg.inline import InlineKeyboard

keyboard = InlineKeyboard()
keyboard.paginate(100, 100, 'pagination_keyboard:{number}')
```

#### Result

<p><img src="https://raw.githubusercontent.com/Abishnoi69/Abg/master/doce/images/pagination_keyboard_100.png" alt="pagination_keyboard_100"></p>

#### Pagination 150 pages and buttons

#### Code

```python
from Abg.inline import InlineKeyboard, InlineButton

keyboard = InlineKeyboard()
keyboard.paginate(150, 123, 'pagination_keyboard:{number}')
keyboard.row(
    InlineButton('Back', 'pagination_keyboard:back'),
    InlineButton('Close', 'pagination_keyboard:close')
)
```

#### Result

<p><img src="https://raw.githubusercontent.com/Abishnoi69/Abg/master/doce/images/pagination_keyboard_150.png" alt="pagination_keyboard_150"></p>

### Languages inline keyboard

```python
from Abg.inline import InlineKeyboard
```

#### Parameters:

- callback_pattern (string) - use of the `{locale}` pattern is <ins>required</ins>
- locales (string | list) - list of language codes
  - be_BY - Belarusian
  - de_DE - German
  - zh_CN - Chinese
  - en_US - English
  - fr_FR - French
  - id_ID - Indonesian
  - it_IT - Italian
  - ko_KR - Korean
  - tr_TR - Turkish
  - ru_RU - Russian
  - es_ES - Spanish
  - uk_UA - Ukrainian
  - uz_UZ - Uzbek
- row_width (integer, default 2)


#### Code

```python
from Abg.inline import InlineKeyboard


keyboard = InlineKeyboard(row_width=3)
keyboard.languages(
    'languages:{locale}', ['en_US', 'ru_RU', 'id_ID'], 2
)
```

#### Result

<p><img src="https://raw.githubusercontent.com/Abishnoi69/Abg/master/doce/images/languages_keyboard.png" alt="languages_keyboard"></p>

## Reply Keyboard

```python
from Abg.inline import ReplyKeyboard
```

#### Parameters:

- resize_keyboard (bool, optional)
- one_time_keyboard (bool, optional)
- selective (bool, optional)
- row_width (integer, default 3)

### Reply keybord add buttons

#### Code

```python
from Abg.inline import ReplyKeyboard, ReplyButton


keyboard = ReplyKeyboard(row_width=3)
keyboard.add(
    ReplyButton('Reply button 1'),
    ReplyButton('Reply button 2'),
    ReplyButton('Reply button 3'),
    ReplyButton('Reply button 4'),
    ReplyButton('Reply button 5')
)
```

#### Result

<p><img src="https://raw.githubusercontent.com/Abishnoi69/Abg/master/doce/images/add_reply_button.png" alt="add_reply_button"></p>

### Reply Keyboard row buttons

#### Code

```python
from Abg.inline import ReplyKeyboard, ReplyButton


keyboard = ReplyKeyboard()
keyboard.row(ReplyButton('Reply button 1'))
keyboard.row(
    ReplyButton('Reply button 2'),
    ReplyButton('Reply button 3')
)
keyboard.row(ReplyButton('Reply button 4'))
keyboard.row(ReplyButton('Reply button 5'))
```

#### Result

<p><img src="https://raw.githubusercontent.com/Abishnoi69/Abg/master/doce/images/row_reply_button.png" alt="row_reply_button"></p>


### Thanks pykeyboard 
