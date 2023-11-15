import vision

def main():
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
