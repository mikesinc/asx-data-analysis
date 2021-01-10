import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

if __name__ == "__main__":
    
    print(os.path.abspath(os.path.join(os.path.dirname(resource_path(__file__)), '..\\..\\data')))

    print(resource_path(__file__))
    print(sys.argv[1])
    print(sys.argv[2])