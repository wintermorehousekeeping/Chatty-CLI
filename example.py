"""
Test file for Chatty-CLI demonstration
"""

def fibonacci(n):
    """Calculate fibonacci number recursively"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)


class Calculator:
    """Basic calculator with some bugs"""
    
    def add(self, a, b):
        return a + b
    
    def divide(self, a, b):
        if b == 0:
            return None
        return a / b
    
    def multiply(self, a, b):
        return a + b  # Bug: should be multiplication


def process_data(data):
    """Process a list of numbers"""
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result


if __name__ == "__main__":
    calc = Calculator()
    print(calc.add(5, 3))
    print(calc.multiply(5, 3))  # Bug: should be 15 but will be 8