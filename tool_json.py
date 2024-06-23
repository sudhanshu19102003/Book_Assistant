import json

def add_tool(tools_list):
    name = input("Enter the tool name: ")
    description = input("Enter the tool description: ")
    format_ = input("Enter the tool format: ")
    example = input("Enter the tool example (as a JSON string): ")

    try:
        example_json = json.loads(example)
    except json.JSONDecodeError:
        print("Invalid JSON format for example. Please try again.")
        return

    tool = {
        "name": name,
        "description": description,
        "format": format_,
        "example": example_json
    }

    tools_list.append(tool)

def main():
    tools_list = []

    while True:
        add_tool(tools_list)
        more = input("Do you want to add another tool? (yes/no): ").strip().lower()
        if more != 'yes':
            break

    with open('tools.json', 'w') as file:
        json.dump({"tools": tools_list}, file, indent=4)

    print("Tools saved to tools.json")

if __name__ == "__main__":
    main()
