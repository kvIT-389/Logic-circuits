def open_file(self):
    selected_file = QFileDialog.getOpenFileName(
        None, "Open file",
        os.path.expanduser("~"),
        "Circuit files (*.circuit, *.circ)"
    )

    if selected_file[0] != "":
        print(f"File {selected_file[0]} was opened.")

def save_file_as(self):
    file_name = QFileDialog.getSaveFileName(
        None, "Save as",
        os.path.expanduser("~"),
        "Circuit file (*.circuit, *.circ)"
    )
    print(file_name)


def load_circuit(self, string):
    """
    Loads circuit from the given string. 
    """

    element_pattern = r"/(?:\s)*(And|Or|Xor|Not|Switch|Lamp|Wire)([\d\-\s]*)"

    for elem in re.findall(element_pattern, string):
        elem_type = elem[0]
        elem_data = [int(n) for n in elem[1].split()]

        if elem_type in ("And", "Or", "Xor", "Not", "Switch", "Lamp"):
            elem_data.extend([0] * (3 - len(elem_data)))
            new_element = self.add_element({
                "And": And, "Or": Or, "Xor": Xor, "Not": Not,
                "Switch": Switch, "Lamp": Lamp
            }[elem_type])
            new_element.move(*elem_data[:2])
            if elem_data[2] != 0:
                new_element.rotate(elem_data[2])

            new_element.connect_to(self.elements)

        elif elem_type == "Wire":
            pass

def circuit_to_string(self):
    string = f"/Scale {self.circuit_scale}"
    for element in self.elements:
        elem_type = element.__class__.__name__
        if elem_type in ("And", "Or", "Xor", "Not", "Switch", "Lamp"):
            string += f" /{elem_type} {element.x()} {element.y()} {element.rotation}"

        elif elem_type == "Wire":
            pass

    return string
