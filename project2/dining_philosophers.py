"""
dining_philosophers.py
CECS 326 - Operating Systems
Group Project 2 - Darren Ammara & Samuel Kim

This program implements a solution to the Dining Philosophers problem using
Python threading with mutex locks and condition variables. Five philosophers
alternate between thinking and eating, requiring two forks to eat while
preventing deadlock through proper synchronization.
"""

import threading
import time
import random

class DiningPhilosophers:
    def __init__(self, num_philosophers=5):
        self.num_philosophers = num_philosophers
        # Each philosopher has a state: THINKING, HUNGRY, or EATING
        self.state = ['THINKING'] * num_philosophers
        # Mutex lock for critical section
        self.mutex = threading.Lock()
        # Condition variable for each philosopher
        self.condition = [threading.Condition(self.mutex) for _ in range(num_philosophers)]
        # Track fork ownership (-1 means on table, otherwise philosopher number)
        self.forks = [0] * num_philosophers
        
    def left_fork(self, philosopher_num):
        """Return the left fork index for a philosopher"""
        return philosopher_num
    
    def right_fork(self, philosopher_num):
        """Return the right fork index for a philosopher"""
        return (philosopher_num + 1) % self.num_philosophers
    
    def test(self, philosopher_num):
        """Test if philosopher can eat (both forks available)"""
        left = self.left_fork(philosopher_num)
        right = self.right_fork(philosopher_num)
        
        # Can eat if hungry and neighbors are not eating
        if (self.state[philosopher_num] == 'HUNGRY' and
            self.state[left] != 'EATING' and
            self.state[right] != 'EATING'):
            
            self.state[philosopher_num] = 'EATING'
            # Update fork counts
            self.forks[left] = self.count_forks(left)
            self.forks[right] = self.count_forks(right)
            
            print(f"Forks are with Philosopher #{philosopher_num}")
            self.condition[philosopher_num].notify()
    
    def count_forks(self, fork_num):
        """Count how many philosophers are holding this fork"""
        count = 0
        # Check left philosopher
        left_phil = fork_num
        if self.state[left_phil] == 'EATING':
            count += 1
        # Check right philosopher
        right_phil = (fork_num - 1) % self.num_philosophers
        if self.state[right_phil] == 'EATING':
            count += 1
        return count
    
    def print_fork_status(self):
        """Print the status of all forks"""
        for i in range(self.num_philosophers):
            count = self.count_forks(i)
            print(f"  Fork #{i} is with {count}")
    
    def pickup_forks(self, philosopher_num):
        """Philosopher attempts to pick up forks"""
        self.mutex.acquire()
        
        self.state[philosopher_num] = 'HUNGRY'
        self.test(philosopher_num)
        
        # If can't eat, wait on condition variable
        while self.state[philosopher_num] != 'EATING':
            self.condition[philosopher_num].wait()
        
        self.mutex.release()
    
    def return_forks(self, philosopher_num):
        """Philosopher returns forks after eating"""
        self.mutex.acquire()
        
        self.state[philosopher_num] = 'THINKING'
        
        # Update fork status
        left = self.left_fork(philosopher_num)
        right = self.right_fork(philosopher_num)
        self.forks[left] = self.count_forks(left)
        self.forks[right] = self.count_forks(right)
        
        # Print fork status
        self.print_fork_status()
        
        # Test if left and right neighbors can now eat
        self.test(left)
        self.test(right)
        
        self.mutex.release()


class Philosopher(threading.Thread):
    def __init__(self, philosopher_num, dining_philosophers):
        threading.Thread.__init__(self)
        self.philosopher_num = philosopher_num
        self.dining_philosophers = dining_philosophers
        self.daemon = True
    
    def run(self):
        """Philosopher thread main loop"""
        while True:
            # Think for random time (1-3 seconds)
            think_time = random.randint(1000, 3000)
            print(f"Philosopher #{self.philosopher_num} took {think_time}ms thinking")
            time.sleep(think_time / 1000.0)
            
            # Try to pick up forks
            self.dining_philosophers.pickup_forks(self.philosopher_num)
            
            # Eat for random time (1-3 seconds)
            eat_time = random.randint(1000, 3000)
            print(f"Philosopher #{self.philosopher_num} took {eat_time}ms eating")
            time.sleep(eat_time / 1000.0)
            
            # Return forks
            self.dining_philosophers.return_forks(self.philosopher_num)


def main():
    """Main function to run the dining philosophers simulation"""
    num_philosophers = 5
    
    print("=== Dining Philosophers Problem ===")
    print(f"Starting simulation with {num_philosophers} philosophers\n")
    
    # Create dining philosophers instance
    dining = DiningPhilosophers(num_philosophers)
    
    # Create and start philosopher threads
    philosophers = []
    for i in range(num_philosophers):
        philosopher = Philosopher(i, dining)
        philosophers.append(philosopher)
        philosopher.start()
    
    # Run simulation for a certain time (or indefinitely)
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nSimulation stopped by user")


if __name__ == "__main__":
    main()