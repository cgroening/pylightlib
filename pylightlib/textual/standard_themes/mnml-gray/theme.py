from textual.theme import Theme


TEXTUAL_THEME = Theme(
    name='mnml-gray',
    primary='#8BD3CD',
    secondary='#444444',
    accent='#A9B7C6',
    foreground='#E5E5E5',
    background='#222222',
    surface="#727272",
    panel="#242628",
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