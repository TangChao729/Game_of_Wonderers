from wonder import start, update


# def main():
    
#     start()
#     return 0


# if __name__ == "__main__":
#     main()

import cProfile

def run():
    # Your code or function calls to profile
    start()  # replace with your main function

cProfile.run('run()', 'profile_output')
