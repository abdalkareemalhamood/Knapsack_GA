import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from random import random
from typing import Callable, List, Tuple
from random import choices, randint, randrange
from functools import partial

Genome = List[int]  
#Genome is just a list of 0,1 eg> g1 = [0,1,1,0,0], g2 = [1,0,1,1,0]
Population = List[Genome]  
#Population is a list of all genomes eg> p1 = [g1,g2,...]
FitnessFunc = Callable[[Genome], float]  
#The fitness function takes a Genome and returns a fitness value for the given Genome
PopulationFunc = Callable[[],Population]  
#The population function generates a list of Genomes, the list is called the current generation population
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]  
#The Selection function takes a population and the fitness function and gives us a pair of genomes (called parents) prefering genomes with higher fitness values
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]  
#The Crossover Function takes two parent genomes sptilts them randomly at an index and then switches the sliced parts of the genome
MutationFunc = Callable[[Genome], Genome]  
#Mutation function changes the given number of values in a genome depending on the given value of probability and returns the mutated genome

#A general purpose thing object to store each item, an named tupple could also be used for the same

class Item:
    def __init__(self,name,value,weight):
        self.name = name
        self.value = value
        self.weight = weight

things = []

#defining all of the above mentioned functions

def generate_genome(length: int) -> Genome:
    return choices([0,1],k=length)

def generate_population(size: int, genome_length: int) -> Population:
    return [generate_genome(genome_length) for _ in range(size)]

def fitness(genome: Genome, things: List[Item], weight_limit: float) -> float:
    if len(genome) != len(things):
        raise ValueError("Genome and Thimgs must be of same length")
    
    weight  = 0
    value = 0
    for i, thing in enumerate(things):
        if genome[i] == 1:
            weight += thing.weight
            value += thing.value

            if weight > weight_limit:
                return 0
    
    return value

def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    return choices(
        population= population,
        weights= [fitness_func(genome) for genome in population],
        k=2
    )

def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome,Genome]:
    if len(a) != len(b):
        raise ValueError("Genomes a and b need to be of the same length")

    length = len(a)
    if length < 2:
        return a,b
    
    p = randint(1,length-1)
    return a[:p] + b[p:] , b[:p] + a[p:]

def mutation(genome: Genome, num: int = 1, probability: float = 0.5) -> Genome:
    for _ in range(num):
        index = randrange(len(genome))
        genome[index] = genome[index] if random() > probability else abs(genome[index]-1)
    return genome

def run_evolution(
    populate_func: PopulationFunc,
    fitness_func: FitnessFunc,
    fitness_limit: float,
    selection_func: SelectionFunc = selection_pair,
    crossover_func: CrossoverFunc = single_point_crossover,
    mutation_func: MutationFunc = mutation,
    generation_limit: int = 100) -> Tuple[Population, int]:

    population = populate_func()

    for i in range(generation_limit):
        population = sorted(
            population,
            key= lambda genome: fitness_func(genome),
            reverse= True
        )

        if fitness_func(population[0]) >= fitness_limit:
            break

        next_generation = population[:2]

        for j in range(int(len(population)/2)-1):
            parents = selection_func(population, fitness_func)
            offspring_a, offspring_b = crossover_func(parents[0], parents[1])
            offspring_a = mutation_func(offspring_a)
            offspring_b = mutation_func(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation

    population = sorted(
        population,
        key= lambda genome: fitness_func(genome),
        reverse= True
    )

    return population, i

def genome_to_things(genome: Genome, things: List[Item]) -> List[Item]:
    result = []
    for i,thing in enumerate(things):
        if genome[i]==1:
            result += [thing.name]
    
    return result


def cal(items,values,weights,limw):
    items = items.strip()
    items = items.split(" ")
    values = values.strip()
    values = values.split(" ")
    weights = weights.strip()
    weights = weights.split(" ")

    for i in range(0,len(items)):
        items[i] = int(items[i])

    for i in range(0,len(values)):
        values[i] = int(values[i])

    for i in range(0,len(weights)):
        weights[i] = int(weights[i])

    global things
    things=[]
    for i in range(0,len(items)): 
        things.append(Item(items[i],values[i],weights[i]))
    global population
    global generations    
    population, generations = run_evolution(
        populate_func= partial(
            generate_population, size = 10, genome_length = len(things)
        ),
        fitness_func=partial(
            fitness, things = things, weight_limit = limw
        ),
        fitness_limit= 999999,
        generation_limit=100
    )




def index(request):
    if request.method == 'GET' and 'items' in request.GET:
        items = request.GET.get('items')
        values = request.GET.get('values')
        weights = request.GET.get('weights')
        limW = request.GET.get('limW')
        limW = int(limW)

        cal(items,values,weights,limW)

        best= genome_to_things(population[0], things)
        bestsolution = str(best[0])
        for i in range (1,len(best)):
            bestsolution = bestsolution + ' , ' + str(best[i])
        
        return JsonResponse({
            'result': 'Genetic Algorithms Knapsack Problem Solving:<br>'+'The Optimal Solution is:  ' + bestsolution+'<br>with Total Value: '+str({fitness(population[0], things, limW)})
        },status=200,
        )

    return render(
        request,
        'Knapsack_GA.html'
    )
