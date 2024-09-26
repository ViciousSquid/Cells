import random
import math
import uuid

class Genome:
    def __init__(self, genes=None, never_consume=False):
        self.genes = genes or {
            'size': random.uniform(5, 20),
            'speed': random.uniform(0.5, 2.0),
            'energy_efficiency': random.uniform(0.5, 1.5),
            'division_threshold': random.uniform(20, 40),
            'color': (random.random(), random.random(), random.random()),
            'has_tail': random.choice([True, False]),
            'can_consume': random.choice([True, False]),
            'consumption_size_ratio': random.uniform(1.2, 2.0),
            'nitrogen_reserve': random.uniform(0.2, 0.5),
            'adhesin': random.choice([True, False]),
            'radiation_sensitivity': random.uniform(0.1, 0.5)
        }
        self.dna = self.encode_genes()
        self.never_consume = never_consume

    def encode_genes(self):
        dna = 0
        dna |= (int(self.genes['size'] * 10) & 0xFF) << 24
        dna |= (int(self.genes['speed'] * 10) & 0xFF) << 16
        dna |= (int(self.genes['energy_efficiency'] * 10) & 0xFF) << 8
        dna |= (int(self.genes['division_threshold'] * 10) & 0xFF)
        dna |= (int(self.genes['consumption_size_ratio'] * 10) & 0xFF) << 32
        dna |= (int(self.genes['color'][0] * 255) & 0xFF) << 40
        dna |= (int(self.genes['color'][1] * 255) & 0xFF) << 48
        dna |= (int(self.genes['color'][2] * 255) & 0xFF) << 56
        dna |= (int(self.genes['has_tail']) & 0x1) << 64
        dna |= (int(self.genes['can_consume']) & 0x1) << 65
        dna |= (int(self.genes['nitrogen_reserve'] * 10) & 0xFF) << 72
        dna |= (int(self.genes['adhesin']) & 0x1) << 80
        dna |= (int(self.genes['radiation_sensitivity'] * 10) & 0xFF) << 88
        return dna

    def decode_genes(self, dna):
        self.genes['size'] = ((dna >> 24) & 0xFF) / 10.0
        self.genes['speed'] = ((dna >> 16) & 0xFF) / 10.0
        self.genes['energy_efficiency'] = ((dna >> 8) & 0xFF) / 10.0
        self.genes['division_threshold'] = (dna & 0xFF) / 10.0
        self.genes['consumption_size_ratio'] = ((dna >> 32) & 0xFF) / 10.0
        self.genes['color'] = (
            ((dna >> 40) & 0xFF) / 255.0,
            ((dna >> 48) & 0xFF) / 255.0,
            ((dna >> 56) & 0xFF) / 255.0
        )
        self.genes['has_tail'] = (dna >> 64) & 0x1
        self.genes['can_consume'] = (dna >> 65) & 0x1
        self.genes['nitrogen_reserve'] = ((dna >> 72) & 0xFF) / 10.0
        self.genes['adhesin'] = (dna >> 80) & 0x1
        self.genes['radiation_sensitivity'] = ((dna >> 88) & 0xFF) / 10.0

    def mutate(self, mutation_rate=0.1):
        for gene in self.genes:
            if random.random() < mutation_rate:
                if isinstance(self.genes[gene], bool):
                    if gene == 'can_consume' and self.never_consume:
                        continue  # Skip mutation if never_consume is enabled
                    self.genes[gene] = not self.genes[gene]
                elif isinstance(self.genes[gene], tuple):
                    self.genes[gene] = tuple(min(1, max(0, x + random.uniform(-0.1, 0.1))) for x in self.genes[gene])
                else:
                    self.genes[gene] *= random.uniform(0.8, 1.2)

    def copy(self):
        return Genome(self.genes.copy(), self.never_consume)

class Cell:
    def __init__(self, genome, position, dna=None):
        self.genome = genome
        self.position = position
        self.energy = 20
        self.age = 0
        self.dna = dna or self.genome.encode_genes()
        self.angle = random.uniform(0, 2 * math.pi)
        self.type = "Phagocyte"
        self.nitrogen_reserve = self.genome.genes['nitrogen_reserve']
        self.adhesin = self.genome.genes['adhesin']
        self.radiation_sensitivity = self.genome.genes['radiation_sensitivity']
        self.last_eaten = 0  # Track the last time the cell ate
        self.adhered_cells = []  # List to store adhered cells

    def update(self, environment, dt):
        self.age += dt
        self.energy += self.genome.genes['energy_efficiency'] * dt

        # Energy consumption based on size
        energy_consumption = self.genome.genes['size'] * 0.01 * dt
        self.energy -= energy_consumption

        self.nitrogen_reserve += 0.01 * dt

        self.energy -= self.radiation_sensitivity * dt

        if self.genome.genes['has_tail']:
            speed = self.genome.genes['speed']
            dx = math.cos(self.angle) * speed * dt
            dy = math.sin(self.angle) * speed * dt
        else:
            dx = random.uniform(-1, 1) * self.genome.genes['speed'] * dt
            dy = random.uniform(-1, 1) * self.genome.genes['speed'] * dt

        new_x = self.position[0] + dx
        new_y = self.position[1] + dy

        # Calculate energy loss due to movement
        distance_moved = math.sqrt(dx ** 2 + dy ** 2)
        energy_loss = distance_moved * 0.1  # Adjust the multiplier as needed
        self.energy -= energy_loss

        self.resolve_boundary_collision(environment)

        self.position = (new_x, new_y)

        if self.energy <= 0:
            self.genome.genes['color'] = (0.5, 0.5, 0.5)  # Turn grey
            self.die(environment)

        # Check for starvation
        if environment.current_time - self.last_eaten > environment.starvation_threshold:
            self.die(environment)

        # Scale size based on energy
        self.genome.genes['size'] = max(5, min(128, self.energy * 0.5))

        # Cap energy at 100
        self.energy = min(100, self.energy)

        # Energy sharing with adhered cells
        if self.adhesin and self.adhered_cells:
            total_energy = self.energy + sum(cell.energy for cell in self.adhered_cells)
            avg_energy = total_energy / (len(self.adhered_cells) + 1)
            self.energy = avg_energy
            for cell in self.adhered_cells:
                cell.energy = avg_energy

    def can_divide(self):
        return self.age >= 20 and self.energy > self.genome.genes['division_threshold'] and self.nitrogen_reserve >= 0.2

    def divide(self):
        child_genome = self.genome.copy()
        child_genome.mutate()
        child_position = (
            self.position[0] + random.choice([-8, 8]),
            self.position[1] + random.choice([-8, 8])
        )
        child_dna = (self.dna & 0xFFFF0000) | (random.randint(0, 65535) & 0x0000FFFF)
        child = Cell(child_genome, child_position, child_dna)
        child.type = self.type
        self.energy /= 2
        child.energy = self.energy
        child.nitrogen_reserve = self.nitrogen_reserve / 2
        self.nitrogen_reserve /= 2
        return child

    def can_consume(self, other_cell):
        if not self.genome.genes['can_consume']:
            return False
        size_ratio = self.genome.genes['size'] / other_cell.genome.genes['size']
        return size_ratio > self.genome.genes['consumption_size_ratio']

    def consume(self, other_cell, environment):
        self.energy += other_cell.energy
        self.nitrogen_reserve += other_cell.nitrogen_reserve
        self.genome.genes['size'] = min(self.genome.genes['size'] + 0.5, 32)  # Increase size slightly, but limit to 32
        self.last_eaten = environment.current_time  # Update the last eaten time

        # Cap energy at 100
        self.energy = min(100, self.energy)

    def die(self, environment):
        distance = math.sqrt((self.position[0] - environment.center[0]) ** 2 + (self.position[1] - environment.center[1]) ** 2)
        if distance <= environment.radius:
            environment.food.append((self.position[0], self.position[1]))
        environment.remove_cell(self)

    def adhere_to(self, other_cell):
        if self.adhesin and other_cell.adhesin and other_cell not in self.adhered_cells:
            self.adhered_cells.append(other_cell)
            other_cell.adhered_cells.append(self)

    def separate_from(self, other_cell):
        if other_cell in self.adhered_cells:
            self.adhered_cells.remove(other_cell)
            other_cell.adhered_cells.remove(self)

    def check_collision(self, other_cell):
        distance = math.sqrt((self.position[0] - other_cell.position[0]) ** 2 + (self.position[1] - other_cell.position[1]) ** 2)
        return distance < (self.genome.genes['size'] + other_cell.genome.genes['size']) / 2

    def resolve_collision(self, other_cell):
        distance = math.sqrt((self.position[0] - other_cell.position[0]) ** 2 + (self.position[1] - other_cell.position[1]) ** 2)
        overlap = (self.genome.genes['size'] + other_cell.genome.genes['size']) / 2 - distance
        if overlap > 0:
            angle = math.atan2(other_cell.position[1] - self.position[1], other_cell.position[0] - self.position[0])
            self.position = (
                self.position[0] - math.cos(angle) * overlap / 2,
                self.position[1] - math.sin(angle) * overlap / 2
            )
            other_cell.position = (
                other_cell.position[0] + math.cos(angle) * overlap / 2,
                other_cell.position[1] + math.sin(angle) * overlap / 2
            )

    def resolve_boundary_collision(self, environment):
        distance = math.sqrt((self.position[0] - environment.center[0]) ** 2 + (self.position[1] - environment.center[1]) ** 2)
        if distance > environment.radius - self.genome.genes['size'] / 2:
            angle = math.atan2(environment.center[1] - self.position[1], environment.center[0] - self.position[0])
            new_x = environment.center[0] + math.cos(angle) * (environment.radius - self.genome.genes['size'] / 2)
            new_y = environment.center[1] + math.sin(angle) * (environment.radius - self.genome.genes['size'] / 2)
            self.position = (new_x, new_y)

class Bacteria(Cell):
    def __init__(self, genome, position, dna=None):
        super().__init__(genome, position, dna)
        self.type = "Bacteria"
        self.genome.genes['size'] *= 0.5
        self.genome.genes['speed'] *= 1.5
        self.genome.genes['energy_efficiency'] *= 0.8

    def update(self, environment, dt):
        super().update(environment, dt)
        if random.random() < 0.001:
            self.energy = self.genome.genes['division_threshold']

        # Cap energy at 100
        self.energy = min(100, self.energy)

class Phagocyte(Cell):
    def __init__(self, genome, position, dna=None):
        super().__init__(genome, position, dna)
        self.type = "Phagocyte"

    def update(self, environment, dt):
        super().update(environment, dt)

class Photocyte(Cell):
    def __init__(self, genome, position, dna=None):
        super().__init__(genome, position, dna)
        self.type = "Photocyte"

    def update(self, environment, dt):
        super().update(environment, dt)
