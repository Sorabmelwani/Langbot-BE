

# function to read file
def read_file():
    with open('train.txt', 'r') as f:
        return f.read()
    

# function to write file
def write_file(data):
    with open('train.txt', 'w') as f:
        f.write(data)
        return data