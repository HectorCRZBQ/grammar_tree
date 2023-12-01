import tkinter as tk
from lark import Lark

# Definir la gramática y el parser
GRAMMAR = '''
    ?start: expr
    ?expr: NUMBER -> number
        | expr "+" expr  -> add
        | expr "-" expr  -> sub
        | expr "*" expr  -> mul
        | expr "/" expr  -> div
        | "(" expr ")"
    NUMBER: /\d+(\.\d+)?/
    %import common.WS
    %ignore WS
'''

PARSER = Lark(GRAMMAR, parser='lalr')

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

def build_ast(expression):
    try:
        return PARSER.parse(expression)
    except Exception as e:
        raise ValueError(f"Error al analizar la expresión: {e}")

def build_tree(tree, parent_node):
    if isinstance(tree, tuple):
        root = str(tree[0])
        if tree[0] == 'NUMBER':
            root = str(tree[1])
            node = Node(root)
            parent_node.children.append(node)
        else:
            node = Node(root)
            parent_node.children.append(node)
            for child in tree[1:]:
                if child is not None:
                    build_tree(child, node)
    elif hasattr(tree, 'children'):
        root = str(tree.data)
        node = Node(root)
        parent_node.children.append(node)
        for child in tree.children:
            if child is not None:
                build_tree(child, node)
    elif tree is not None:
        node = Node(str(tree))
        parent_node.children.append(node)

def display_tree(expression):
    try:
        tree = build_ast(expression)
        root_node = Node("Root")
        build_tree(tree, root_node)
        draw_tree(root_node, canvas, x=200, y=50, x_increment=100)

    except ValueError as ve:
        error_label.config(text=str(ve))
    except Exception as e:
        error_label.config(text=f"Error inesperado: {e}")

def draw_tree(node, canvas, x, y, x_increment):
    canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="white", outline="black")
    canvas.create_text(x, y, text=node.value)
    children_count = len(node.children)
    if children_count > 0:
        start_x = x - x_increment * children_count // 2
        start_y = y + 50
        for child in node.children:
            canvas.create_line(x, y + 15, start_x + x_increment // 2, start_y - 15, fill="black")
            draw_tree(child, canvas, start_x + x_increment // 2, start_y, x_increment)
            start_x += x_increment

root = tk.Tk()
root.title("Visualizador de Árbol Sintáctico")
root.geometry("600x400")

label = tk.Label(root, text="Ingresa una expresión matemática:")
label.pack()

entry = tk.Entry(root)
entry.pack()

button = tk.Button(root, text="Mostrar Árbol", command=lambda: display_tree(entry.get()))
button.pack()

canvas = tk.Canvas(root, width=800, height=600)
canvas.pack()

error_label = tk.Label(root, text="", fg="red")
error_label.pack()

root.mainloop()
