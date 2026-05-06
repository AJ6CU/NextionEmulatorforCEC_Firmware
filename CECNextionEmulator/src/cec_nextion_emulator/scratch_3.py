import tkinter as tk

root = tk.Tk()
canvas = tk.Canvas(root, width=400, height=300, bg="white")
canvas.pack()

# Data
categories = ["A", "B", "C"]
data1 = [50, 80, 40]
data2 = [70, 30, 90]

bar_width = 30
spacing = 50  # Space between groups

for i in range(len(categories)):
    # Calculate group start position
    x_base = 50 + i * (2 * bar_width + spacing)

    # Draw Bar 1 (Green)
    canvas.create_rectangle(x_base, 250 - data1[i], x_base + bar_width, 250, fill="green")

    # Draw Bar 2 (Blue) - shifted by bar_width
    canvas.create_rectangle(x_base + bar_width, 250 - data2[i], x_base + 2 * bar_width, 250, fill="blue")

    # Add Label
    canvas.create_text(x_base + bar_width, 265, text=categories[i])

root.mainloop()