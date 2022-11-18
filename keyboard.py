from pynput import keyboard

COG = 0


    

# The event listener will be running in this block
with keyboard.Events() as events:
    for event in events:
        if event.key == keyboard.Key.esc:
            break
        elif type(event) == keyboard.Events.Press:
            if event.key == keyboard.Key.left:
                COG -= 1
            elif event.key == keyboard.Key.right:
                COG += 1
            if COG < 0:
                COG += 360
            if COG > 360:
                COG -= 360

            print(COG)





