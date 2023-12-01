import tkinter as tk
from lark import Lark

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
    def __init__(self, value, data_type):
        self.value = value
        self.data_type = data_type
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
            node = Node(root, 'Number')
            parent_node.children.append(node)
        else:
            node = Node(root, 'Operation')
            parent_node.children.append(node)
            for child in tree[1:]:
                if child is not None:
                    build_tree(child, node)
    elif hasattr(tree, 'children'):
        root = str(tree.data)
        if root == 'number':
            root = str(tree.children[0])
            node = Node(root, 'Number')
            parent_node.children.append(node)
        else:
            node = Node(root, 'Operation')
            parent_node.children.append(node)
            for child in tree.children:
                if child is not None:
                    build_tree(child, node)
    elif tree is not None:
        node = Node(str(tree), 'Number')
        parent_node.children.append(node)

def calculate_tree_size(node, x_spacing, y_spacing):
    if not node.children:
        return 1, 1  # Nodo hoja, retorna un tamaño mínimo

    width = sum(calculate_tree_size(child, x_spacing, y_spacing)[0] for child in node.children)
    height = max(calculate_tree_size(child, x_spacing, y_spacing)[1] for child in node.children) + 1

    return width, height


def draw_tree(node, canvas, x, y, x_spacing, y_spacing, level=0):
    text_size = 12
    node_radius = 20  # Radio del nodo

    # Dibuja el nodo actual
    canvas.create_oval(x - node_radius, y - node_radius, x + node_radius, y + node_radius, fill="white", outline="black")
    canvas.create_text(x, y, text=f"{node.value}\n({node.data_type})", justify='center', font=("Arial", text_size))

    children_count = len(node.children)
    if children_count > 0:
        # Calcula el ancho total ocupado por los nodos hijos
        total_width = sum(calculate_tree_size(child, x_spacing, y_spacing)[0] for child in node.children) + (children_count - 1) * x_spacing

        # Ajusta las posiciones iniciales de los nodos hijos
        start_x = x - total_width // 2

        # Lista para almacenar las posiciones de los nodos hijos
        children_positions = []

        # Calcula las posiciones de los nodos hijos
        for child in node.children:
            child_width = calculate_tree_size(child, x_spacing, y_spacing)[0]
            children_positions.append(start_x + child_width // 2)
            start_x += child_width + x_spacing

        # Calcula la separación entre los nodos hijos
        spacing = max(node_radius * 6, total_width // (children_count + 1))

        # Dibuja las líneas y los nodos hijos
        for child_x, child_node in zip(children_positions, node.children):
            child_y = y + y_spacing  # Establece una separación vertical entre niveles
            canvas.create_line(x, y + node_radius, child_x, child_y - node_radius, fill="black")

            # Dibuja el nodo hijo en su posición calculada
            draw_tree(child_node, canvas, child_x, child_y, spacing if level > 0 else x_spacing, y_spacing, level + 1)


def display_tree_in_window(expression):
    try:
        tree = build_ast(expression)
        root_node = Node("Root", 'Operation')
        build_tree(tree, root_node)

        tree_width, tree_height = calculate_tree_size(root_node, x_spacing=250, y_spacing=120)  # Incremento del espacio entre nodos

        new_window = tk.Toplevel()
        new_window.title("Árbol Sintáctico")

        # Ajuste del tamaño del canvas y del espacio interno
        canvas_width = tree_width * 250 + 100
        canvas_height = tree_height * 120 + 100
        canvas = tk.Canvas(new_window, width=canvas_width, height=canvas_height, bg="white")  # Fondo blanco con espacio interno
        canvas.pack()

        draw_tree(root_node, canvas, x=canvas_width // 2, y=60, x_spacing=250, y_spacing=120)

    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(f"Error inesperado: {e}")

root = tk.Tk()
root.title("Visualizador de Árbol Sintáctico")

label = tk.Label(root, text="Ingresa una expresión matemática:")
label.pack()

entry = tk.Entry(root)
entry.pack()

canvas = tk.Canvas(root, bg="white")  # Fondo blanco para el lienzo
canvas.pack(fill=tk.BOTH, expand=True)

button = tk.Button(root, text="Mostrar Árbol", command=lambda: display_tree_in_window(entry.get()))
button.pack()

root.mainloop()
