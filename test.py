import os

token = os.getenv('BND_TOKEN')

if token:
    print(f"Valid:")
else:
    print("Invalid.")