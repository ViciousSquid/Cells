# file_io.py
import json
from cell import Cell, Genome

def save_environment(environment, filename):
    data = {
        'width': environment.width,
        'height': environment.height,
        'cells': [
            {
                'position': cell.position,
                'energy': cell.energy,
                'age': cell.age,
                'genome': cell.genome.genes
            }
            for cell in environment.cells
        ],
        'food': environment.food
    }
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_environment(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    
    environment = Environment(data['width'], data['height'])
    environment.food = data['food']
    
    for cell_data in data['cells']:
        genome = Genome(cell_data['genome'])
        cell = Cell(genome, cell_data['position'])
        cell.energy = cell_data['energy']
        cell.age = cell_data['age']
        environment.add_cell(cell)
    
    return environment

def save_genome(genome, filename):
    with open(filename, 'w') as f:
        json.dump(genome.genes, f)

def load_genome(filename):
    with open(filename, 'r') as f:
        genes = json.load(f)
    return Genome(genes)