

def get_font_stylesheet(color=(0,0,0), size=10):
    return "QLabel{color:rgb(%d,%d,%d,255);font-size:%dpx;font-weight:bold;font-family:Arial;}"%(
        color[0], color[1], color[2], size
    )

def get_html_formatted_text(text, color='black', size=20):
    return f'<span style="color:{color};font-size:{size}px;">{text}</span>'