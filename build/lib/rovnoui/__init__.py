from os import system
from platform import system as oprsys
from rich.console import Console
from typing import overload
import ctypes


ROVNOUI_VERSION = '0.4.3'


class Widget():
    """Base class for any widget."""
    
    def __init__(self) -> None:
        pass
    
    @overload
    def print(self):
        """Print the widget."""
        ...


class _CursorInfo(ctypes.Structure):
    _fields_ = [
        ("size", ctypes.c_int),
        ("visible", ctypes.c_byte)
    ]


class Screen():
    """The screen class. Contains methods to manage your screen, clear it, print stuff, etc"""

    def __init__(self, layout: list[Widget] | None = None, widget_separator: str = '\n') -> None:
        self._updates: int = 0
        self.console = Console()
        self.layout = layout
        self.widget_separator = widget_separator
        self.ci = _CursorInfo()
        self.ci_handle = ctypes.windll.kernel32.GetStdHandle(-11)

    def clear(self) -> None:
        """Fully clear the screen, like the cls command on Windows."""
        system('cls') if oprsys() == 'Windows' else system('clear')
        self._updates += 1
    
    def partial_clear(self, lines: int | str = 99) -> None:
        """Clear only part of the screen."""
        print(f'\033[{lines}A\033[2K', end='')
        self._updates += 1

    def hide_cursor(self) -> None:
        """Hide the terminal cursor."""
        ctypes.windll.kernel32.GetConsoleCursorInfo(self.ci_handle, ctypes.byref(self.ci))
        self.ci.visible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(self.ci_handle, ctypes.byref(self.ci))

    def show_cursor(self) -> None:
        """Show the terminal cursor."""
        ctypes.windll.kernel32.GetConsoleCursorInfo(self.ci_handle, ctypes.byref(self.ci))
        self.ci.visible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(self.ci_handle, ctypes.byref(self.ci))

    def print(self, text) -> None:
        """Print any Rich renderable to the terminal."""
        self.console.print(text, highlight=False)
    
    def print_layout(self) -> None:
        """Print the screen layout."""
        for widget in self.layout:
            widget.print()
            print(self.widget_separator, end='')


class Header(Widget):
    """A simple header widget - text on color background."""

    def __init__(self, text: str, style: str = 'bold white on blue') -> None:
        self._console = Console()
        self.text = text
        self.style = style
    
    def print(self) -> None:
        self._console.print(f' {self.text} ', style=self.style, highlight=False)


class ScrollingTextBox(Widget):
    """A text box of fixed height that scrolls when there are too much lines."""

    def __init__(self, limit: int = 10, header = Header | None) -> None:
        self._line_buffer: list[str] = ['' for i in range(limit)]
        self.limit: int = limit
        self._console = Console()

    def print(self, text) -> None:
        if len(self._line_buffer) >= self.limit:
            self._line_buffer.pop(0)
        self._line_buffer.append(text)
        for line in self._line_buffer:
            self._console.print(line, highlight=False)


class DataFrame(Widget):
    """A frame that shows some data or stats."""
    
    def __init__(self, data: list[str], header: Header | None, colors: list[str]) -> None:
        self._console = Console()
        self.data = data
        self.header = header
        self.colors = colors

    def print(self) -> None:
        if type(self.header) == Header:
            self.header.print()
        for text, color in zip(self.data, self.colors):
            self._console.print(f'[{color}]+[/{color}] {text}', highlight=False)


class Selector(Widget):
    """A simple selector."""
    
    def __init__(self, header: Header | None, choices: list[dict], style: str = 'blue') -> None:
        self.header = header
        self.choices = choices
        self.style = style
        self._console = Console()

    def print(self) -> None:
        if type(self.header) == Header:
            self.header.print()

        _i = 1

        for choice in self.choices:
            for _key in choice.keys():
                self._console.print(f'[b]{_i}. {_key}[/]', highlight=False)
                self._console.print(f'   {choice[_key]}', highlight=False)
                _i += 1

    def ask(self, print: bool = True) -> int:
        if print:
            self.print()
        try:
            return int(self._console.input(f'[b][{self.style}]+[/][/] '))
        except KeyboardInterrupt:
            return False


class InfoFrame(Widget):
    """A simple header-body information frame widget."""

    def __init__(self, data: list[dict], header: Header | None = None) -> None:
        self.header = header
        self._console = Console()
        self.data = data
    
    def print(self) -> None:
        if type(self.header) == Header:
            self.header.print()
        for entry in self.data:
            self._console.print(f'[bold]{list(entry.keys())[0]}[/]', highlight=False)
            self._console.print(f'{list(entry.values())[0]}', highlight=False)


class FixedLabel(Widget):
    """A text label with fixed size."""

    def __init__(self, text: str, limit: int = 10) -> None:
        self.limit = limit
        self.text = text
        self._console = Console()
    
    def _construct(self) -> str:
        text_length: int = len(self.text)
        if text_length < self.limit:
            return f"{self.text}{' ' * (self.limit - text_length)}"
        elif text_length == self.limit:
            return self.text
        else:
            return self.text[:self.limit-3] + '...'
    
    def __str__(self) -> str:
        return self._construct()
    
    def __repr__(self) -> str:
        return self._construct()
    
    def print(self) -> None:
        self._console.print(self._construct())
    
    def construct(self) -> str:
        return self._construct()
