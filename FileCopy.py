"""
FileCopy.py
CECS 326 - Operating Systems
Group Project  - Darren Ammara & Samuel Kim

This program opens a file and writes its contents to a pipe,
demonstrating interprocess communication between parent and child processes.
"""

import os
import sys
import errno

# Buffer size for reading/writing operations
BUFFER_SIZE = 25

def print_usage():
    """Print usage information for the program."""
    print("Usage: python3 filecopy.py <source_file> <destination_file>")
    print("Example: python3 filecopy.py input.txt output.txt")

def validate_arguments(argv):
    """
    Validate command line arguments.
    
    Args:
        argv: Command line arguments list
        
    Returns:
        tuple: (source_file, dest_file) or None if invalid
    """
    if len(argv) != 3:
        print("Error: Incorrect number of arguments.")
        print_usage()
        return None
    
    source_file = argv[1]
    dest_file = argv[2]
    
    # Check if source file exists and is readable
    if not os.path.exists(source_file):
        print(f"Error: Unable to open source file '{source_file}'.")
        return None
    
    if not os.access(source_file, os.R_OK):
        print(f"Error: No read permission for source file '{source_file}'.")
        return None
    
    return source_file, dest_file

def handle_parent_process(source_file, pipe_write_fd, child_pid):
    """
    Handle the parent process logic: read from source file and write to pipe.
    
    Args:
        source_file: Path to the source file
        pipe_write_fd: Write end of the pipe
        child_pid: Process ID of the child process
    """
    try:
        # Open source file for reading
        with open(source_file, 'rb') as src_fd:
            # Read from source file in chunks and write to pipe
            while True:
                # Read a chunk from the source file
                data = src_fd.read(BUFFER_SIZE)
                if not data:
                    break  # End of file reached
                
                # Write the chunk to the pipe
                os.write(pipe_write_fd, data)
        
        # Close the write end of the pipe to signal end of data
        os.close(pipe_write_fd)
        
        # Wait for child process to complete
        pid, status = os.waitpid(child_pid, 0)
        
        if status == 0:
            # Extract just the filename for cleaner output
            source_name = os.path.basename(source_file)
            dest_name = os.path.basename(dest_file)  # Fixed: use dest_file instead of sys.argv[2]
            print(f"File successfully copied from {source_name} to {dest_name}.")
        else:
            print(f"Error: Child process exited with status {status}")
            
    except IOError as e:
        print(f"Error: Unable to open source file '{source_file}'.")
        os.close(pipe_write_fd)
        # Terminate child process if needed
        try:
            os.kill(child_pid, 9)
        except:
            pass
        sys.exit(1)

def handle_child_process(dest_file, pipe_read_fd):
    """
    Handle the child process logic: read from pipe and write to destination file.
    
    Args:
        dest_file: Path to the destination file
        pipe_read_fd: Read end of the pipe
    """
    try:
        # Open destination file for writing
        with open(dest_file, 'wb') as dest_fd:
            # Read from pipe and write to destination file
            while True:
                try:
                    # Read from the pipe
                    data = os.read(pipe_read_fd, BUFFER_SIZE)
                    if not data:
                        break  # No more data in pipe
                    
                    # Write to destination file
                    dest_fd.write(data)
                    
                except OSError as e:
                    if e.errno == errno.EBADF:
                        # Pipe closed by parent, normal termination
                        break
                    else:
                        raise
        
        # Close the read end of the pipe
        os.close(pipe_read_fd)
        
        # Child process exits successfully
        sys.exit(0)
        
    except IOError as e:
        print(f"Error: Unable to create destination file '{dest_file}'.")
        os.close(pipe_read_fd)
        sys.exit(1)

def copy_file_with_pipe(source_file, dest_file):
    """
    Main file copying function using pipes for IPC.
    
    Args:
        source_file: Path to the source file
        dest_file: Path to the destination file
    """
    try:
        # Create a pipe - returns (read_fd, write_fd)
        pipe_read_fd, pipe_write_fd = os.pipe()
        
        # Fork a child process
        child_pid = os.fork()
        
        if child_pid == 0:
            # This is the child process
            # Close unused pipe end (write end) in child
            os.close(pipe_write_fd)
            
            # Execute child process logic
            handle_child_process(dest_file, pipe_read_fd)
            
        elif child_pid > 0:
            # This is the parent process
            # Close unused pipe end (read end) in parent
            os.close(pipe_read_fd)
            
            # Execute parent process logic
            handle_parent_process(source_file, pipe_write_fd, child_pid)
            
        else:
            # Fork failed
            print("Error: Failed to fork child process")
            os.close(pipe_read_fd)
            os.close(pipe_write_fd)
            sys.exit(1)
            
    except OSError as e:
        print(f"Error creating pipe or forking process: {e}")
        sys.exit(1)

def main():
    """Main function to orchestrate the file copying process."""
    # Validate command line arguments
    result = validate_arguments(sys.argv)
    if result is None:
        sys.exit(1)
    
    source_file, dest_file = result
    
    # Start the file copying process
    copy_file_with_pipe(source_file, dest_file)

if __name__ == "__main__":
    main()