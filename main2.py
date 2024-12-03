import tkinter as tk

class AdditionalScreen:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.geometry("1920x1080")
        self.window.title("Additional Screen")

        # Add a label to the window
        label = tk.Label(self.window, text="This is an additional screen")
        label.pack(pady=20)

def create_two_additional_windows(root):
    # Create the first additional screen
    screen1 = AdditionalScreen(root)
    
    # Create the second additional screen
    screen2 = AdditionalScreen(root)

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window if you don't want to show it

    # Call the function to create and show two additional windows
    create_two_additional_windows(root)

    root.mainloop()

if __name__ == "__main__":
    main()
