import vision


def main():
    """Entry point for the program.

    It continuously prompts the user for a query, sends it to the vision module for processing,
    and displays the response received from the vision module.
    """

    while True:
        query = input("Query: ")
        response = vision.ask(query)
        message = response['choices'][0]['message']
        role = message['role']
        content = message['content']
        print()
        print(f'{role}: {content}')


if __name__ == '__main__':
    main()
