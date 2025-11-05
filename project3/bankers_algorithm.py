"""
bankers_algorithm.py
CECS 326 - Operating Systems
Group Project 3 - Darren Ammara & Samuel Kim

This program implements the Banker's Algorithm to detect safe states
and handle resource allocation requests while avoiding deadlocks.
"""


class BankersAlgorithm:
    """
    Implementation of the Banker's Algorithm for deadlock avoidance.
    
    Attributes:
        n (int): Number of processes
        m (int): Number of resource types
        available (list): Available instances of each resource type
        max_need (list): Maximum demand of each process
        allocation (list): Currently allocated resources to each process
        need (list): Remaining resource need of each process
    """
    
    def __init__(self, n, m, available, max_need, allocation):
        """
        Initialize the Banker's Algorithm with system state.
        
        Args:
            n (int): Number of processes
            m (int): Number of resource types
            available (list): Available resources vector
            max_need (list): Maximum demand matrix (n x m)
            allocation (list): Current allocation matrix (n x m)
        """
        self.n = n
        self.m = m
        self.available = available.copy()
        self.max_need = [row.copy() for row in max_need]
        self.allocation = [row.copy() for row in allocation]
        
        # Calculate the Need matrix (Need = Max - Allocation)
        self.need = self._calculate_need()
    
    def _calculate_need(self):
        """
        Calculate the Need matrix.
        Need[i][j] = Max[i][j] - Allocation[i][j]
        
        Returns:
            list: Need matrix (n x m)
        """
        need = []
        for i in range(self.n):
            process_need = []
            for j in range(self.m):
                process_need.append(self.max_need[i][j] - self.allocation[i][j])
            need.append(process_need)
        return need
    
    def is_safe(self):
        """
        Safety Algorithm: Check if the system is in a safe state.
        
        This algorithm tries to find a safe sequence of process execution
        that allows all processes to complete without deadlock.
        
        Returns:
            tuple: (bool, list) - (True if safe, safe sequence) or (False, [])
        """
        # Step 1: Initialize Work and Finish vectors
        work = self.available.copy()  # Work represents available resources
        finish = [False] * self.n      # Finish[i] indicates if process i can finish
        safe_sequence = []              # Store the safe sequence
        
        # Step 2: Find processes that can complete
        while len(safe_sequence) < self.n:
            # Find a process that can be satisfied
            found = False
            
            for i in range(self.n):
                # Check if process i is not finished and its needs can be satisfied
                if not finish[i]:
                    # Check if Need[i] <= Work (process i can get needed resources)
                    can_allocate = True
                    for j in range(self.m):
                        if self.need[i][j] > work[j]:
                            can_allocate = False
                            break
                    
                    # If process i can be allocated resources
                    if can_allocate:
                        # Step 3: Simulate process completion
                        # Add allocated resources back to work (process finishes and releases)
                        for j in range(self.m):
                            work[j] += self.allocation[i][j]
                        
                        finish[i] = True
                        safe_sequence.append(i)
                        found = True
                        break
            
            # If no process can proceed, system is not in safe state
            if not found:
                return False, []
        
        # Step 4: Check if all processes can finish
        # If all processes finished, system is in safe state
        return True, safe_sequence
    
    def request_resources(self, process_id, request):
        """
        Resource-Request Algorithm: Handle a resource request from a process.
        
        This algorithm checks if a resource request can be granted safely.
        
        Args:
            process_id (int): ID of the requesting process
            request (list): Requested resources vector
            
        Returns:
            bool: True if request granted, False otherwise
        """
        print(f"\nProcess {process_id} requests resources {request}")
        
        # Step 1: Check if request <= Need
        # Request should not exceed declared maximum need
        for j in range(self.m):
            if request[j] > self.need[process_id][j]:
                print(f"Error: Process {process_id} has exceeded its maximum claim.")
                return False
        
        # Step 2: Check if request <= Available
        # Check if enough resources are currently available
        for j in range(self.m):
            if request[j] > self.available[j]:
                print("Error: Not enough resources available.")
                return False
        
        # Step 3: Pretend to allocate resources (simulate allocation)
        # Save the current state for rollback if needed
        old_available = self.available.copy()
        old_allocation = [row.copy() for row in self.allocation]
        old_need = [row.copy() for row in self.need]
        
        # Temporarily modify state
        for j in range(self.m):
            self.available[j] -= request[j]
            self.allocation[process_id][j] += request[j]
            self.need[process_id][j] -= request[j]
        
        # Step 4: Check if the new state is safe
        is_safe, safe_seq = self.is_safe()
        
        if is_safe:
            # If safe, keep the allocation
            print("System is in a safe state.")
            print(f"Safe Sequence: {safe_seq}")
            print(f"Resources allocated to process {process_id}.")
            return True
        else:
            # If unsafe, rollback to previous state
            print("System would be in an unsafe state.")
            print(f"Request from process {process_id} cannot be granted.")
            
            # Restore the old state
            self.available = old_available
            self.allocation = old_allocation
            self.need = old_need
            return False
    
    def print_state(self):
        """Print the current system state for debugging."""
        print("\n=== Current System State ===")
        print(f"Available: {self.available}")
        print("\nAllocation Matrix:")
        for i, row in enumerate(self.allocation):
            print(f"Process {i}: {row}")
        print("\nMaximum Matrix:")
        for i, row in enumerate(self.max_need):
            print(f"Process {i}: {row}")
        print("\nNeed Matrix:")
        for i, row in enumerate(self.need):
            print(f"Process {i}: {row}")
        print("=" * 30)


def main():
    """Main function to demonstrate the Banker's Algorithm."""
    
    # System configuration from the project description
    n = 5  # Number of processes
    m = 3  # Number of resource types
    
    # Available Vector (initially total resources available)
    available = [3, 3, 2]
    
    # Maximum Matrix - maximum resource needs for each process
    max_need = [
        [7, 5, 3],  # Process 0
        [3, 2, 2],  # Process 1
        [9, 0, 2],  # Process 2
        [2, 2, 2],  # Process 3
        [4, 3, 3]   # Process 4
    ]
    
    # Allocation Matrix - currently allocated resources to each process
    allocation = [
        [0, 1, 0],  # Process 0
        [2, 0, 0],  # Process 1
        [3, 0, 2],  # Process 2
        [2, 1, 1],  # Process 3
        [0, 0, 2]   # Process 4
    ]
    
    # Print initial configuration
    print("=" * 50)
    print("BANKER'S ALGORITHM - DEADLOCK AVOIDANCE")
    print("=" * 50)
    print(f"\nNumber of processes: {n}")
    print(f"Number of resource types: {m}")
    print(f"Available resources: {available}")
    
    # Create Banker's Algorithm instance
    banker = BankersAlgorithm(n, m, available, max_need, allocation)
    
    # Print initial state
    banker.print_state()
    
    # Test Case 1: Check if initial state is safe
    print("\n" + "=" * 50)
    print("TEST CASE 1: Run Safe Test")
    print("=" * 50)
    is_safe, safe_seq = banker.is_safe()
    if is_safe:
        print("System is in a safe state.")
        print(f"Safe Sequence: {safe_seq}")
    else:
        print("System is NOT in a safe state.")
    
    # Test Case 2: Process 1 requests resources [1, 0, 2]
    print("\n" + "=" * 50)
    print("TEST CASE 2: Process 1 Resource Request")
    print("=" * 50)
    request = [1, 0, 2]
    banker.request_resources(1, request)
    
    # Test Case 3: Process 4 requests resources [3, 3, 1]
    print("\n" + "=" * 50)
    print("TEST CASE 3: Process 4 Resource Request")
    print("=" * 50)
    request = [3, 3, 1]
    banker.request_resources(4, request)
    
    # Additional test case: Process 0 requests resources [0, 2, 0]
    print("\n" + "=" * 50)
    print("TEST CASE 4: Process 0 Resource Request")
    print("=" * 50)
    request = [0, 2, 0]
    banker.request_resources(0, request)
    
    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    main()