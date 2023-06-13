from pywinauto import Desktop, mouse

def activate_window(partial_title):
    
    windows = Desktop(backend='win32').windows()
    for window in windows:
        if partial_title.lower() in window.window_text().lower():
            window.set_focus()
            window.move_window(x=500, y=0, width=int(1425), height=1045)
            break
        
    mouse.move(coords=(int(1920/4), int(1080/2)))

# Example usage
activate_window("navis n4")