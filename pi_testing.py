!/home/magic/Projects/magic-mirror-frontend/porcupine/.venv/bin/python


import time

def main():
    messages = ["Starting the script...", 
                "Waiting for a while...", 
                "Printing again...", 
                "And we wait again...", 
                "Final message!", 
                "Exiting the script..."]

    for msg in messages:
        print(msg)
        time.sleep(2)  # Waits for 2 seconds

if __name__ == "__main__":
    main()
