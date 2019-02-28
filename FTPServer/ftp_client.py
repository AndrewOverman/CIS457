from ftplib import FTP

client = FTP()
prompt = "-"*10 + "\nCONNECT <server_name/IP_address> <server_port>\n" \
                  "LIST\nRETRIEVE <filename>\nSTORE <filename>\nQUIT\n" + "-"*10 + "\n"

# prompts user for input of command
def read_input():
    return input(prompt)

# parses input from read_input and determines what command is passed
def main():
    input = read_input()
    # while input is not QUIT, check which command is passed forever
    # if input is QUIT, break out of loop and conitnue function
    while input != "QUIT":
        command = input.split()
        # Connects to specified server and port number and passes default login credentials
        if command[0].upper() == "CONNECT":
            client.connect(command[1], int(command[2]))
            client.login("user", "pass")
        # Lists files in current directory
        elif command[0].upper() == "LIST":
            client.dir()
        # Retrieves a file from server or updates current file if already exists
        elif command[0].upper() == "RETRIEVE":
            file = open(command[1], "wb")
            client.retrbinary("RETR " + command[1], file.write)
            file.close()
        # Stores a file in server or updates current file if already exists
        elif command[0].upper() == "STORE":
            client.storbinary("STOR " + command[1], open(command[1], "rb"))
        # Warns user command is invalid and prompts again fo ruser input
        else:
            print("Invalid command\n")
        # updates input before returning to start of loop
        input = read_input()
    # Disconnects from host and ends program
    client.close()


if __name__ == "__main__":
    main()
