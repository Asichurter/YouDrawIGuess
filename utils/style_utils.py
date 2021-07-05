

def get_qlabel_font_stylesheet(color='black', size=10):
    return "QLabel{color:%s;font-size:%dpx;font-weight:bold;font-family:Arial;}"%(
        color, size
    )

def get_html_formatted_text(text, color='black', size=20):
    return f'<span style="color:{color};font-size:{size}px;">{text}</span>'