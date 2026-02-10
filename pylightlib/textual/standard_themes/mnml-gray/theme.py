from textual.theme import Theme


TEXTUAL_THEME = Theme(
    name='mnml-gray',
    primary='#8BD3CD',
    secondary='#2B2B2B',
    accent='#A9B7C6',
    foreground='#E5E5E5',
    background='#1A1A1A',
    surface="#3E3E3E",
    panel="#212121",
    boost='#444C5E',
    success='#A3C995',
    warning='#E6C384',
    error='#D67B76',
    dark=True,
    variables={
        'block-hover-background': "#335D48",
        'footer-key-foreground': '#D2D05F',
        'input-cursor-text-style': 'reverse',
    }
)
