import numpy as np
from typing import Dict, List, Any
import random
import itertools
from tqdm import tqdm
import time


class GeneticOptimizer:
    def __init__(
        self,
        parameter_ranges: Dict,
        population_size: int = 50,
        elite_size: int = 5,
        mutation_rate: float = 0.2,
        mutation_strength: float = 0.3,
        tournament_size: int = 3
    ):
        self.parameter_ranges = parameter_ranges
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.tournament_size = tournament_size
        self.best_fitness_history = []
        self.diversity_history = []
        
    def generate_population(self) -> List[Dict]:
        return [
            {key: np.random.choice(list(self.parameter_ranges[key]))
             for key in self.parameter_ranges.keys()}
            for _ in range(self.population_size)
        ]
    
    def calculate_population_diversity(self, population: List[Dict]) -> float:
        diversity = 0
        for key in self.parameter_ranges.keys():
            values = [ind[key] for ind in population]
            diversity += len(set(values)) / len(self.parameter_ranges[key])
        return diversity / len(self.parameter_ranges)
    
    def tournament_selection(self, population: List[Dict], fitness_values: List[float]) -> Dict:
        tournament_idx = random.sample(range(len(population)), self.tournament_size)
        tournament_fitness = [fitness_values[i] for i in tournament_idx]
        winner_idx = tournament_idx[np.argmax(tournament_fitness)]
        return population[winner_idx]
    
    def adaptive_mutation(self, individual: Dict, diversity: float) -> Dict:
        mutated = individual.copy()
        # Increase mutation rate when diversity is low
        adaptive_rate = self.mutation_rate * (1 + (1 - diversity))
        
        for key in mutated.keys():
            if random.random() < adaptive_rate:
                current_idx = list(self.parameter_ranges[key]).index(mutated[key])
                range_size = len(self.parameter_ranges[key])
                
                # Calculate mutation step size based on diversity
                step_size = int(range_size * self.mutation_strength * (1 + (1 - diversity)))
                step = random.randint(-step_size, step_size)
                
                # Apply circular mutation to stay within bounds
                new_idx = (current_idx + step) % range_size
                mutated[key] = list(self.parameter_ranges[key])[new_idx]
                
        return mutated
    
    def crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        child = {}
        for key in parent1.keys():
            # Implement arithmetic crossover
            if isinstance(parent1[key], (int, float)):
                weight = random.random()
                value = int(parent1[key] * weight + parent2[key] * (1 - weight))
                # Ensure value is in range
                valid_values = list(self.parameter_ranges[key])
                closest_idx = min(range(len(valid_values)), 
                                key=lambda i: abs(valid_values[i] - value))
                child[key] = valid_values[closest_idx]
            else:
                child[key] = random.choice([parent1[key], parent2[key]])
        return child
    
    def optimize(self, fitness_function, n_generations: int, min_diversity: float = 0.3):
        population = self.generate_population()
        best_solution = None
        best_fitness = float('-inf')
        generations_without_improvement = 0
        
        for generation in range(n_generations):
            # Evaluate fitness
            fitness_values = fitness_function(population)
            
            # Track best solution
            current_best_idx = np.argmax(fitness_values)
            current_best_fitness = fitness_values[current_best_idx]
            
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_solution = population[current_best_idx]
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1
            
            # Calculate diversity
            diversity = self.calculate_population_diversity(population)
            self.diversity_history.append(diversity)
            self.best_fitness_history.append(best_fitness)
            
            # Store elite individuals
            elite = sorted(zip(population, fitness_values), 
                         key=lambda x: x[1], 
                         reverse=True)[:self.elite_size]
            elite_population = [e[0] for e in elite]
            
            # Create new population
            new_population = elite_population.copy()
            
            # Restart population if diversity is too low or no improvement
            if diversity < min_diversity or generations_without_improvement > 10:
                print(f"Restarting population at generation {generation + 1}")
                new_population.extend(self.generate_population()[:self.population_size - self.elite_size])
                generations_without_improvement = 0
            else:
                # Regular evolution
                while len(new_population) < self.population_size:
                    parent1 = self.tournament_selection(population, fitness_values)
                    parent2 = self.tournament_selection(population, fitness_values)
                    child = self.crossover(parent1, parent2)
                    child = self.adaptive_mutation(child, diversity)
                    new_population.append(child)
            
            population = new_population
            
            print(f'Generation {generation + 1}/{n_generations} - '
                  f'Best Fitness: {best_fitness:.2f} - '
                  f'Diversity: {diversity:.2f}', end='\r')
            
        return best_solution, best_fitness, self.best_fitness_history, self.diversity_history
    


class GridSearchOptimizer:
    def __init__(self, param_ranges: Dict,data,strategy):
        self.data = data
        self.strategy = strategy
        self.param_ranges = param_ranges
        self.best_params = {}
        self.best_result = -np.inf
    
    def _calculate_total_iterations(self) -> int:
        return np.prod([len(range_) for range_ in self.param_ranges.values()])
    
    def optimize(self,fitness_function):
        param_names = list(self.param_ranges.keys())
        param_values = list(self.param_ranges.values())
        total_iters = self._calculate_total_iterations()
        
        param_combinations = itertools.product(*param_values)

        for i,values in enumerate(param_combinations):
            # Crear diccionario de parámetros
            params = dict(zip(param_names, values))
                
            # Ejecutar estrategia y obtener resultado
            result = fitness_function(self.data, self.strategy, **params)
            
            # Actualizar mejores parámetros si el resultado es mejor
            if result > self.best_result:
                self.best_result = result
                self.best_params = params.copy()
                
        
            print(
                f'Iteration: {i+1} / {total_iters} - '
                f'Best Params {self.best_params} - '
                f'Best Result: {self.best_result:.2f} - ', end='\r')
            
        return {
            'best_params': self.best_params,
            'best_result': self.best_result,
        }