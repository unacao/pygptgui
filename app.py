import vision
import pyautogui

def run(query: str):
    """Run query."""
    if query.startswith("type"):
        # Keyboard.
        pyautogui.write(query[len("type "):])
    else:
        # Mouse.
        response = vision.ask(query)
        if 'choices' in response:
            message = response['choices'][0]['message']
            role = message['role']
            content = message['content']
            print(f'\n{role}: {content}')
        else:
            print(response)



def main():
    """Entry point for the program.

    It continuously prompts the user for a query, sends it to the vision module for processing,
    and displays the response received from the vision module.
    """

    while True:
        query = input("Query: ")
        run(query)



if __name__ == '__main__':
    main()
